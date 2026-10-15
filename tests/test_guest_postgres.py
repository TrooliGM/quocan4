import asyncio
import os
import threading
import unittest
from concurrent.futures import ThreadPoolExecutor
from unittest.mock import patch
from uuid import uuid4

from fastapi import Header, HTTPException
from fastapi.testclient import TestClient
from app import app
from advisor.routes import require_user
from advisor.store import get_store, empty_profile
from advisor import postgres_store as pg
from advisor.guest_quota import get_guest_usage, claim_guest_history, check_chat_rate
from postgres_fixture import LocalPostgres


def reply():
    return {'answer': 'Bạn có thể thử vẽ một poster.', 'profile': empty_profile(), 'summary': '', 'recommendations': []}


def fake_user(authorization: str | None = Header(default=None)):
    users = {'Bearer guest': {'uid':'guest','provider':'anonymous'},
             'Bearer google': {'uid':'google','provider':'google.com'},
             'Bearer email': {'uid':'email','provider':'password'}}
    if authorization not in users: raise HTTPException(401,'Unauthorized')
    return users[authorization]


class GuestPostgresTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.cluster = LocalPostgres().__enter__()

    @classmethod
    def tearDownClass(cls):
        cls.cluster.__exit__(None,None,None)

    def setUp(self):
        self.connection = self.cluster.schema()
        self.env = patch.dict(os.environ, {'DATABASE_URL':self.cluster.url,'AI_DEMO_MODE':'true','DEEPSEEK_API_KEY':''})
        self.dbpatch = patch.object(pg,'postgres_connection',self.connection)
        self.env.start();self.dbpatch.start()
        app.dependency_overrides[require_user] = fake_user
        self.client = TestClient(app)
        async def mocked(state):
            return {'session':pg.save_messages_atomic(state['uid'],state['session_id'],state['request_id'],state['message'],reply(),'demo',state.get('guest_reservation_token'))}
        self.graph = patch('advisor.routes.advisor_graph.ainvoke',side_effect=mocked)
        self.graph_mock = self.graph.start()

    def tearDown(self):
        self.graph.stop();self.client.close();app.dependency_overrides.pop(require_user,None)
        self.dbpatch.stop();self.env.stop()

    def session(self,owner='guest',remember=False):
        response = self.client.post('/api/ai/sessions',headers={'Authorization':'Bearer '+owner},json={'remember':remember})
        self.assertEqual(response.status_code,201,response.text)
        return response.json()['session']['id']

    def send(self,sid,request_id=None,owner='guest',message='Mình thích vẽ'):
        return self.client.post('/api/ai/chat',headers={'Authorization':'Bearer '+owner},json={'session_id':sid,'request_id':request_id or str(uuid4()),'message':message})

    def test_guest_1_to_8_then_9_both_session_types(self):
        for i in range(8):
            sid = self.session(remember=bool(i%2))
            response = self.send(sid)
            self.assertEqual(response.status_code,200,response.text)
            self.assertEqual(response.json()['guest_quota']['used_questions'],i+1)
        self.assertEqual(self.send(self.session()).status_code,403)
        self.assertEqual(self.graph_mock.call_count,8)
        last=self.graph_mock.call_args.args[0]
        self.assertEqual(self.send(last['session_id'],last['request_id'],message=last['message']).status_code,200)
        self.assertEqual(self.graph_mock.call_count,8)

    def test_members_not_limited_to_8_and_rate_protection_remains(self):
        for owner in ('google','email'):
            sid = self.session(owner)
            for _ in range(9):self.assertEqual(self.send(sid,owner=owner).status_code,200)
        for _ in range(30):check_chat_rate('speed-test')
        with self.assertRaises(HTTPException) as error:check_chat_rate('speed-test')
        self.assertEqual(error.exception.status_code,429)

    def test_duplicate_and_changed_content(self):
        sid=self.session();rid=str(uuid4())
        self.assertEqual(self.send(sid,rid).status_code,200)
        duplicate=self.send(sid,rid)
        self.assertTrue(duplicate.json()['duplicate'])
        self.assertEqual(self.graph_mock.call_count,1)
        self.assertEqual(get_guest_usage('guest')['used_questions'],1)
        self.assertEqual(self.send(sid,rid,message='Nội dung khác').status_code,409)

    def test_validation_missing_key_and_other_owner_do_not_charge(self):
        sid=self.session()
        self.assertEqual(self.send(sid,message='  ').status_code,422)
        self.assertEqual(self.send(sid,owner='email').status_code,404)
        with patch.dict(os.environ,{'AI_DEMO_MODE':'false','DEEPSEEK_API_KEY':''}):
            self.assertEqual(self.send(sid).status_code,503)
        self.assertEqual(get_guest_usage('guest')['used_questions'],0)

    def test_failure_refund_once_and_retry(self):
        sid=self.session();rid=str(uuid4())
        with patch('advisor.routes.advisor_graph.ainvoke',side_effect=RuntimeError('mock failure')):
            self.assertEqual(self.send(sid,rid).status_code,502)
        self.assertEqual(get_guest_usage('guest')['used_questions'],0)
        with self.connection() as db:
            record=db.execute('SELECT * FROM guest_ai_requests WHERE request_id=%s',(rid,)).fetchone()
        pg.finish_guest_request('guest',rid,False,record['reservation_token'])
        self.assertEqual(get_guest_usage('guest')['used_questions'],0)
        self.assertEqual(self.send(sid,rid).status_code,200)
        self.assertEqual(get_guest_usage('guest')['used_questions'],1)

    def test_committed_answer_never_refunded_after_error(self):
        for remember in (False,True):
            sid=self.session(remember=remember);rid=str(uuid4())
            async def saved_then_error(state):
                pg.save_messages_atomic(state['uid'],sid,rid,state['message'],reply(),'demo',state['guest_reservation_token'])
                raise RuntimeError('lost response after commit')
            with patch('advisor.routes.advisor_graph.ainvoke',side_effect=saved_then_error) as ai:
                self.assertEqual(self.send(sid,rid).status_code,200)
                self.assertEqual(self.send(sid,rid).status_code,200)
                self.assertEqual(ai.call_count,1)
        self.assertEqual(get_guest_usage('guest')['used_questions'],2)

    def test_new_reservation_pending_and_concurrent_boundary(self):
        sid=self.session();rid=str(uuid4())
        first=pg.reserve_guest_request('guest',sid,rid,'text')
        second=pg.reserve_guest_request('guest',sid,rid,'text')
        self.assertTrue(first['new_reservation']);self.assertFalse(second['new_reservation'])
        self.assertEqual(second['used_questions'],1)
        with self.connection() as db:db.execute('UPDATE guest_ai_usage SET used_questions=7 WHERE uid=%s',('guest',))
        barrier=threading.Barrier(2)
        def reserve():
            barrier.wait()
            try:return pg.reserve_guest_request('guest',sid,str(uuid4()),'parallel')['new_reservation']
            except HTTPException as e:return e.status_code
        with ThreadPoolExecutor(max_workers=2) as pool:results=list(pool.map(lambda _:reserve(),range(2)))
        self.assertCountEqual(results,[True,403])
        self.assertEqual(get_guest_usage('guest')['used_questions'],8)

    def test_expired_lease_fences_old_worker_and_recovers(self):
        sid=self.session();rid=str(uuid4())
        old=pg.reserve_guest_request('guest',sid,rid,'hello')
        with self.connection() as db:db.execute("UPDATE guest_ai_requests SET lease_until=NOW()-INTERVAL '1 second' WHERE request_id=%s",(rid,))
        new=pg.reserve_guest_request('guest',sid,rid,'hello')
        self.assertTrue(new['new_reservation'])
        self.assertNotEqual(old['reservation_token'],new['reservation_token'])
        with self.assertRaises(HTTPException):pg.save_messages_atomic('guest',sid,rid,'hello',reply(),'demo',old['reservation_token'])
        pg.finish_guest_request('guest',rid,False,old['reservation_token'])
        self.assertEqual(get_guest_usage('guest')['used_questions'],1)
        pg.save_messages_atomic('guest',sid,rid,'hello',reply(),'demo',new['reservation_token'])
        self.assertEqual(get_guest_usage('guest')['used_questions'],1)

    def test_account_claim_preserves_both_histories_and_is_one_time(self):
        destination=self.session('email',True)
        ids=[self.session(remember=r) for r in (False,True)]
        for sid in ids:self.assertEqual(self.send(sid).status_code,200)
        result=claim_guest_history('guest','email')
        self.assertCountEqual(result['session_ids'],ids)
        for sid in ids:self.assertEqual(len(get_store().get('email',sid)['messages']),3)
        self.assertEqual(get_store().get('email',destination)['id'],destination)
        self.assertFalse(claim_guest_history('guest','email')['transferred'])
        with self.assertRaises(HTTPException):claim_guest_history('guest','google')
        self.assertEqual(self.client.post('/api/ai/sessions',headers={'Authorization':'Bearer guest'},json={}).status_code,403)
        self.assertEqual(self.send(ids[0],owner='email').status_code,200)

    def test_same_request_reserved_concurrently_only_once(self):
        sid=self.session();rid=str(uuid4());barrier=threading.Barrier(2)
        def reserve(_):
            barrier.wait()
            return pg.reserve_guest_request('guest',sid,rid,'same')
        with ThreadPoolExecutor(max_workers=2) as pool:results=list(pool.map(reserve,range(2)))
        self.assertEqual(sum(r['new_reservation'] for r in results),1)
        self.assertEqual(get_guest_usage('guest')['used_questions'],1)

    def test_two_http_requests_at_last_slot(self):
        sid=self.session()
        for _ in range(7):self.assertEqual(self.send(sid).status_code,200)
        sessions=[self.session(),self.session()];barrier=threading.Barrier(2)
        def send_parallel(session_id):
            barrier.wait()
            return self.send(session_id).status_code
        with ThreadPoolExecutor(max_workers=2) as pool:results=list(pool.map(send_parallel,sessions))
        self.assertCountEqual(results,[200,403])
        self.assertEqual(get_guest_usage('guest')['used_questions'],8)
        self.assertEqual(self.graph_mock.call_count,8)

    def test_cancellation_before_save_releases_owned_reservation(self):
        from advisor.routes import chat, ChatInput
        sid=self.session();rid=str(uuid4())
        with patch('advisor.routes.advisor_graph.ainvoke',side_effect=asyncio.CancelledError):
            with self.assertRaises(asyncio.CancelledError):
                asyncio.run(chat(ChatInput(session_id=sid,request_id=rid,message='cancel'),{'uid':'guest','provider':'anonymous'}))
        self.assertEqual(get_guest_usage('guest')['used_questions'],0)

    def test_save_and_quota_update_roll_back_together(self):
        sid=self.session();rid=str(uuid4())
        held=pg.reserve_guest_request('guest',sid,rid,'rollback')
        from advisor.guest_quota import settle_locked
        def settle_then_fail(*args):
            settle_locked(*args)
            raise RuntimeError('failure before transaction commit')
        with patch('advisor.guest_quota.settle_locked',side_effect=settle_then_fail):
            with self.assertRaises(RuntimeError):
                pg.save_messages_atomic('guest',sid,rid,'rollback',reply(),'demo',held['reservation_token'])
        self.assertEqual(len(get_store().get('guest',sid)['messages']),1)
        with self.connection() as db:
            self.assertEqual(db.execute('SELECT status FROM guest_ai_requests WHERE request_id=%s',(rid,)).fetchone()['status'],'reserved')
        pg.finish_guest_request('guest',rid,False,held['reservation_token'])
        self.assertEqual(get_guest_usage('guest')['used_questions'],0)

    def test_recovery_keeps_committed_legacy_answer(self):
        sid=self.session();rid=str(uuid4())
        self.assertEqual(self.send(sid,rid).status_code,200)
        with self.connection() as db:
            db.execute("UPDATE guest_ai_requests SET status='reserved',lease_until=NULL,updated_at=NOW()-INTERVAL '3 minutes' WHERE request_id=%s",(rid,))
        self.assertEqual(get_guest_usage('guest')['used_questions'],1)
        with self.connection() as db:
            self.assertEqual(db.execute('SELECT status FROM guest_ai_requests WHERE request_id=%s',(rid,)).fetchone()['status'],'completed')

    def test_claim_requires_two_tokens_and_refuses_busy_guest(self):
        sid=self.session();rid=str(uuid4())
        held=pg.reserve_guest_request('guest',sid,rid,'busy')
        token='test-guest-proof-token-only'
        endpoint='/api/ai/guest/claim';body={'guest_id_token':token}
        self.assertEqual(self.client.post(endpoint,json=body).status_code,401)
        self.assertEqual(self.client.post(endpoint,json=body,headers={'Authorization':'Bearer guest'}).status_code,403)
        with patch('advisor.routes.verify_user',return_value={'uid':'guest','provider':'password'}):
            self.assertEqual(self.client.post(endpoint,json=body,headers={'Authorization':'Bearer email'}).status_code,403)
        with patch('advisor.routes.verify_user',return_value={'uid':'guest','provider':'anonymous'}):
            self.assertEqual(self.client.post(endpoint,json=body,headers={'Authorization':'Bearer email'}).status_code,409)
            pg.finish_guest_request('guest',rid,False,held['reservation_token'])
            self.assertEqual(self.client.post(endpoint,json=body,headers={'Authorization':'Bearer email'}).status_code,200)
        self.assertEqual(get_store().get('email',sid)['id'],sid)

    def test_rename_does_not_replace_newly_saved_messages(self):
        for remember in (False,True):
            sid=self.session(remember=remember);store=get_store();original_get=store.get
            def stale_then_save(uid,session_id):
                stale=original_get(uid,session_id)
                self.assertEqual(self.send(sid).status_code,200)
                return stale
            with patch.object(store,'get',side_effect=[stale_then_save('guest',sid),original_get('guest',sid)]):
                # store.rename reads an old snapshot before UPDATE title.
                renamed=store.rename('guest',sid,'Tên mới')
            self.assertEqual(len(renamed['messages']),3)
            self.assertEqual(len(original_get('guest',sid)['messages']),3)


if __name__=='__main__':unittest.main()
