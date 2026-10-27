"""Real local PostgreSQL; no provider requests or Production connection strings."""
import os,re,unittest
from contextlib import contextmanager
from concurrent.futures import ThreadPoolExecutor
from urllib.parse import quote
from unittest.mock import patch
from fastapi import HTTPException
from fastapi.testclient import TestClient
from app import app
from advisor import postgres_store as pg
from advisor.postgres_adapter import PostgresConversationStore
from advisor.performance import current,RequestPerformance
from postgres_fixture import LocalPostgres

class NavigationStorageTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):cls.cluster=LocalPostgres().__enter__()
    @classmethod
    def tearDownClass(cls):cls.cluster.__exit__(None,None,None)
    def setUp(self):
        connection=self.cluster.schema()
        self.env=patch.dict(os.environ,{'DATABASE_URL':self.cluster.url+'?options='+quote('-c search_path='+connection.schema_name),'AI_DEMO_MODE':'true','VERCEL':''})
        self.env.start();self.client=TestClient(app,client=('127.0.0.1',1))
    def tearDown(self):self.client.close();self.env.stop()
    def test_one_connection_per_navigation_request_and_no_provider(self):
        with patch('advisor.graph.post_completion') as provider:
            self.assertEqual(self.client.post('/api/ai/guest/session').status_code,200)
            ids=[]
            for _ in range(5):
                r=self.client.post('/api/ai/sessions',json={'remember':False})
                self.assertEqual(r.status_code,201,r.text);ids.append(r.json()['session']['id'])
                self.assertIn('db_connections;desc="1"',r.headers['server-timing'])
            for sid in ids:
                r=self.client.get('/api/ai/sessions/'+sid)
                self.assertEqual(r.status_code,200);self.assertIn('db_connections;desc="1"',r.headers['server-timing'])
            r=self.client.get('/api/ai/sessions');self.assertEqual(len(r.json()['items']),5)
            self.assertIn('db_connections;desc="1"',r.headers['server-timing'])
            self.assertNotIn('postgresql',r.headers['server-timing']);provider.assert_not_called()
    def test_union_owner_expiry_and_saved_priority(self):
        store=PostgresConversationStore();saved=store.create('owner',True);temp=store.create('owner',False)
        for s in [saved,temp]:
            self.assertEqual(store.get('owner',s['id'])['remember'],s['remember'])
            with self.assertRaises(HTTPException):store.get('other',s['id'])
        with pg.postgres_connection() as db:db.execute("UPDATE advisor_temporary_sessions SET expires_at=NOW()-INTERVAL '1 second' WHERE id=%s",(temp['id'],))
        self.assertEqual(len(store.list('owner')),1)
        with self.assertRaises(HTTPException):store.get('owner',temp['id'])
    def test_reuse_transactions_rollback_and_cleanup(self):
        state=RequestPerformance(reuse=True);token=current.set(state)
        try:
            store=PostgresConversationStore();s=store.create('owner',True)
            conn=state.db
            with self.assertRaises(ValueError):
                with pg.postgres_connection() as db:
                    db.execute('UPDATE advisor_sessions SET title=%s WHERE id=%s',('not committed',s['id']))
                    raise ValueError('rollback test')
            self.assertEqual(store.get('owner',s['id'])['title'],s['title'])
            self.assertIs(conn,state.db);self.assertEqual(state.connections,1)
            self.assertEqual(int(conn.info.transaction_status),0)
            state.close();self.assertTrue(conn.closed)
        finally:state.close();current.reset(token)
    def test_capacity_guard_serializes_concurrent_creates(self):
        store=PostgresConversationStore()
        with pg.postgres_connection() as db:
            db.execute("""INSERT INTO advisor_sessions SELECT 'capacity-'||i,'capacity','Old','0','0','[]','{}','' FROM generate_series(1,99) AS i""")
        def create(_):
            try:store.create('capacity',False);return 201
            except HTTPException as e:return e.status_code
        with ThreadPoolExecutor(2) as pool:self.assertEqual(sorted(pool.map(create,range(2))),[201,409])
        self.assertEqual(len(store.list('capacity')),100)
    def test_request_connection_and_identity_never_shared(self):
        clients=[self.client,TestClient(app,client=('127.0.0.2',1))]
        try:
            a,b=clients
            a.post('/api/ai/guest/session');b.post('/api/ai/guest/session')
            sid=a.post('/api/ai/sessions',json={}).json()['session']['id']
            self.assertEqual(b.get('/api/ai/sessions/'+sid).status_code,404)
            self.assertEqual(len(b.get('/api/ai/sessions').json()['items']),0)
            self.assertEqual(a.get('/api/ai/sessions/'+sid).status_code,200)
        finally:clients[1].close()
