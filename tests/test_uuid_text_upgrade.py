"""Synthetic PostgreSQL tests only; no Neon credentials or Production data."""
import io
import json
import os
from pathlib import Path
import subprocess
import sys
import unittest
from unittest.mock import patch
from uuid import uuid4
import zipfile

import psycopg
from advisor import postgres_store as pg
from advisor.guest_quota import reserve_guest_request, get_guest_usage
from advisor.store import empty_profile
from postgres_fixture import LocalPostgres

ROOT=Path(__file__).resolve().parents[1]
SQL=ROOT/'migrations/005_uuid_text_compat.sql'

class UUIDUpgradeTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.cluster=LocalPostgres().__enter__()
        cls.oldroot=ROOT/'artifacts'/('old-7c07d33-'+uuid4().hex[:8])
        data=subprocess.check_output(['git','archive','--format=zip','7c07d33'],cwd=ROOT)
        with zipfile.ZipFile(io.BytesIO(data)) as archive:archive.extractall(cls.oldroot)
    @classmethod
    def tearDownClass(cls):cls.cluster.__exit__(None,None,None)
    def setUp(self):
        self.connection=self.cluster.schema(initialize=False)
        for name in ('001_conversations.sql','002_guest_quota.sql'):
            self.execute((ROOT/'migrations'/name).read_text(encoding='utf-8'))
        self.execute('''ALTER TABLE guest_ai_requests ALTER COLUMN request_id TYPE UUID USING request_id::uuid,
            ALTER COLUMN session_id TYPE UUID USING session_id::uuid;
            ALTER TABLE guest_ai_requests ADD COLUMN created_at TIMESTAMPTZ NOT NULL DEFAULT NOW();
            CREATE INDEX guest_requests_owner ON guest_ai_requests(uid,created_at);
            ALTER TABLE guest_ai_requests ALTER COLUMN request_id SET DEFAULT gen_random_uuid();
            ALTER TABLE guest_ai_requests ADD CHECK(status IN ('reserved','completed','failed'));
            ALTER TABLE guest_ai_usage ADD CHECK(used_questions>=0 AND used_questions<=8);''')
        with patch.object(pg,'postgres_connection',self.connection):
            self.session=pg.create_postgres_session('synthetic-uuid-owner')
        self.request_id=str(uuid4())
        with self.connection() as db:
            db.execute("INSERT INTO guest_ai_usage(uid,used_questions) VALUES('synthetic-uuid-owner',2)")
            db.execute("INSERT INTO guest_ai_requests(request_id,uid,session_id,status) VALUES(%s,'synthetic-uuid-owner',%s,'completed'),(%s,'synthetic-uuid-owner',%s,'completed')",
                       (self.request_id,self.session['id'],str(uuid4()),str(uuid4())))
    def execute(self,sql):
        with self.connection() as db:
            db.autocommit=True
            db.execute(sql)
    def types(self):
        with self.connection() as db:
            return [r['kind'] for r in db.execute("SELECT format_type(atttypid,atttypmod) AS kind FROM pg_attribute WHERE attrelid='guest_ai_requests'::regclass AND attname IN ('request_id','session_id') ORDER BY attname").fetchall()]
    def snapshot(self):
        with self.connection() as db:
            rows=[dict(r) for r in db.execute('SELECT to_jsonb(q)::text AS v FROM guest_ai_requests q ORDER BY request_id::text').fetchall()]
            quota=[dict(r) for r in db.execute('SELECT * FROM guest_ai_usage ORDER BY uid').fetchall()]
            return rows,quota
    def test_cast_preserves_orphan_ledger_quota_checks_defaults_and_primary_key(self):
        before=self.snapshot()
        self.execute(SQL.read_text(encoding='utf-8'))
        self.assertEqual(self.types(),['text','text']);self.assertEqual(before,self.snapshot())
        with self.connection() as db:
            result=db.execute("INSERT INTO guest_ai_requests(uid,session_id,status) VALUES('synthetic-uuid-owner',%s,'failed') RETURNING request_id",(self.session['id'],)).fetchone()
            self.assertIsInstance(result['request_id'],str)
            with self.assertRaises(psycopg.errors.UniqueViolation):
                db.execute("INSERT INTO guest_ai_requests(request_id,uid,session_id,status) VALUES(%s,'synthetic-uuid-owner',%s,'failed')",(self.request_id,self.session['id']))
    def test_already_text_is_noop_and_004_sequence_is_compatible(self):
        self.execute(SQL.read_text(encoding='utf-8'));before=self.snapshot()
        self.execute(SQL.read_text(encoding='utf-8'));self.assertEqual(before,self.snapshot())
        self.execute((ROOT/'migrations/004_shared_ai_protection.sql').read_text(encoding='utf-8'))
        from advisor.schema_check import inspect_schema
        with self.connection() as db:self.assertTrue(inspect_schema(db)['ready'])
    def test_incoming_foreign_key_stops_and_rolls_back(self):
        self.execute('CREATE TABLE synthetic_fk(request_id UUID REFERENCES guest_ai_requests(request_id))')
        before=self.snapshot()
        with self.assertRaises(psycopg.Error):self.execute(SQL.read_text(encoding='utf-8'))
        self.assertEqual(self.types(),['uuid','uuid']);self.assertEqual(before,self.snapshot())
    def test_outgoing_foreign_key_stops_without_dropping_it(self):
        self.execute('CREATE TABLE synthetic_parent(id UUID PRIMARY KEY); ALTER TABLE guest_ai_requests ADD FOREIGN KEY(session_id) REFERENCES synthetic_parent(id) NOT VALID')
        with self.assertRaises(psycopg.Error):self.execute(SQL.read_text(encoding='utf-8'))
        self.assertEqual(self.types(),['uuid','uuid'])
    def test_view_or_custom_identifier_check_stops(self):
        self.execute('CREATE VIEW synthetic_view AS SELECT request_id FROM guest_ai_requests')
        with self.assertRaises(psycopg.Error):self.execute(SQL.read_text(encoding='utf-8'))
        self.execute('DROP VIEW synthetic_view; ALTER TABLE guest_ai_requests ADD CHECK(request_id<>\'00000000-0000-0000-0000-000000000000\'::uuid)')
        with self.assertRaises(psycopg.Error):self.execute(SQL.read_text(encoding='utf-8'))
        self.assertEqual(self.types(),['uuid','uuid'])
    def test_expression_index_and_user_trigger_stop(self):
        self.execute('CREATE INDEX synthetic_expr ON guest_ai_requests ((request_id::text))')
        with self.assertRaises(psycopg.Error):self.execute(SQL.read_text(encoding='utf-8'))
        self.execute('DROP INDEX synthetic_expr; CREATE FUNCTION synthetic_trigger() RETURNS trigger LANGUAGE plpgsql AS $$BEGIN RETURN NEW; END$$; CREATE TRIGGER synthetic_t BEFORE UPDATE ON guest_ai_requests FOR EACH ROW EXECUTE FUNCTION synthetic_trigger()')
        with self.assertRaises(psycopg.Error):self.execute(SQL.read_text(encoding='utf-8'))
        self.assertEqual(self.types(),['uuid','uuid'])
    def test_lock_timeout_does_not_partially_convert(self):
        with self.connection() as held:
            held.execute('LOCK TABLE guest_ai_requests IN ACCESS EXCLUSIVE MODE')
            with self.assertRaises(psycopg.errors.LockNotAvailable):self.execute(SQL.read_text(encoding='utf-8'))
        self.assertEqual(self.types(),['uuid','uuid'])
    def test_postflight_failure_rolls_back_types_defaults_and_data(self):
        before=self.snapshot()
        failing=SQL.read_text(encoding='utf-8').replace('IF rows_before<>rows_after','IF TRUE OR rows_before<>rows_after')
        with self.assertRaises(psycopg.Error):self.execute(failing)
        self.assertEqual(self.types(),['uuid','uuid']);self.assertEqual(before,self.snapshot())
        with self.connection() as db:
            expression=db.execute("SELECT pg_get_expr(adbin,adrelid) AS value FROM pg_attrdef WHERE adrelid='guest_ai_requests'::regclass AND adnum=(SELECT attnum FROM pg_attribute WHERE attrelid='guest_ai_requests'::regclass AND attname='request_id')").fetchone()['value']
            self.assertEqual(expression,'gen_random_uuid()')
    def old_write(self,label):
        # Run actual archived Production store/quota modules in a separate interpreter.
        code='''import json,os,sys,dotenv
dotenv.load_dotenv=lambda *a,**k:False
sys.path.insert(0,os.getcwd())
from advisor.store import get_store,empty_profile
from advisor.guest_quota import reserve_guest_request,get_guest_usage
from advisor.postgres_store import save_messages_atomic
from uuid import uuid4
uid='synthetic-old-'+sys.argv[1]
s=get_store().create(uid,True);r=str(uuid4());m='Synthetic compatibility'
lease=reserve_guest_request(uid,s['id'],r,m)
save_messages_atomic(uid,s['id'],r,m,{'answer':'Synthetic reply','profile':empty_profile(),'summary':'','recommendations':[]},'demo',lease['reservation_token'])
assert get_guest_usage(uid)['used_questions']==1
print(json.dumps({'old_write':'PASS'}))'''
        env={**os.environ,'DATABASE_URL':self.cluster.url,'PGOPTIONS':'-c search_path='+self.connection.schema_name,
             'AI_DEMO_MODE':'true','DEEPSEEK_API_KEY':'','VERCEL':'','PYTHONDONTWRITEBYTECODE':'1'}
        result=subprocess.run([sys.executable,'-B','-c',code,label],cwd=self.oldroot,env=env,capture_output=True,text=True,timeout=20)
        self.assertEqual(result.returncode,0,'Old store compatibility failed; credentials withheld')
    def test_actual_old_store_before_after_and_new_store_after(self):
        self.old_write('before')
        self.execute(SQL.read_text(encoding='utf-8'))
        self.old_write('after')
        self.execute((ROOT/'migrations/004_shared_ai_protection.sql').read_text(encoding='utf-8'))
        with patch.object(pg,'postgres_connection',self.connection):
            uid='synthetic-new';s=pg.create_postgres_session(uid);r=str(uuid4());m='Synthetic new request'
            lease=reserve_guest_request(uid,s['id'],r,m)
            pg.save_messages_atomic(uid,s['id'],r,m,{'answer':'New reply','profile':empty_profile(),'summary':'','recommendations':[]},'demo',lease['reservation_token'])
            self.assertEqual(get_guest_usage(uid)['used_questions'],1)
