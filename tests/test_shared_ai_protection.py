"""Shared AI security contracts, real isolated PostgreSQL; Firebase/LLM mocked only."""
import asyncio
import hashlib
import os
import unittest
from concurrent.futures import ThreadPoolExecutor
from unittest.mock import patch
from uuid import uuid4

from fastapi import HTTPException
from fastapi.testclient import TestClient
from starlette.requests import Request

import app as application
from advisor import postgres_store as pg
from advisor.guest_quota import get_guest_usage
from advisor.protection import client_ip
from advisor.store import empty_profile
from postgres_fixture import LocalPostgres


class SharedAIProtectionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls): cls.cluster = LocalPostgres().__enter__()

    @classmethod
    def tearDownClass(cls): cls.cluster.__exit__(None,None,None)

    def setUp(self):
        self.connection = self.cluster.schema()
        def verify(token):
            if token not in ('member','other','firebase-guest'):
                raise HTTPException(401,'Invalid or expired Firebase token')
            return {'uid':token,'provider':'anonymous' if token=='firebase-guest' else 'google.com'}
        async def legacy(state): return {'answer':'Hãy thử vẽ một poster.'}
        async def chat(state):
            return {'session':pg.save_messages_atomic(state['uid'],state['session_id'],state['request_id'],state['message'],
                {'answer':'Thử thiết kế, lập trình và minh họa.','profile':empty_profile(),'summary':'','recommendations':[]},'demo',state.get('guest_reservation_token'))}
        self.patches=[patch.dict(os.environ,{'DATABASE_URL':self.cluster.url,'AI_DEMO_MODE':'true','DEEPSEEK_API_KEY':'test-key',
            'AI_TRUSTED_PROXY_CIDRS':'','AI_USER_PER_MINUTE':'30','AI_IP_PER_MINUTE':'60','AI_IP_PER_DAY':'300','AI_USER_PER_DAY':'200',
            'AI_GUEST_CREATE_PER_MINUTE':'3','AI_GUEST_CREATE_PER_DAY':'10','VERCEL':''}),
            patch.object(pg,'postgres_connection',self.connection),patch('advisor.routes.verify_user',side_effect=verify),
            patch.object(application,'verify_user',side_effect=verify),patch('ai.advice_graph.ainvoke',side_effect=legacy),
            patch('story_ai.story_graph.ainvoke',side_effect=legacy),patch('advisor.routes.advisor_graph.ainvoke',side_effect=chat)]
        self.mocks=[p.start() for p in self.patches]
        self.client=TestClient(application.app,client=('127.0.0.1',41000))

    def tearDown(self):
        self.client.close()
        for p in reversed(self.patches):p.stop()

    def guest(self, client=None):
        result=(client or self.client).post('/api/ai/guest/session')
        self.assertEqual(result.status_code,200,result.text)
        return result.json()['user']['uid']

    def headers(self, member=False): return {'Authorization':'Bearer member'} if member else {}

    def send(self, kind='advice', member=False, request_id=None, client=None, **extra):
        client=client or self.client
        body={'question':'Em thích vẽ và máy tính','request_id':request_id or str(uuid4()),**extra}
        return client.post('/api/advice' if kind=='advice' else '/api/career-stories/bac-si/ask',headers=self.headers(member),json=body)

    def chat_session(self, member=False):
        h=self.headers(member)
        result=self.client.post('/api/ai/sessions',headers=h,json={'remember':False})
        self.assertEqual(result.status_code,201,result.text)
        sid=result.json()['session']['id']
        self.assertEqual(self.client.put('/api/ai/sessions/'+sid+'/survey',headers=h,json={'answers':['Vẽ và máy tính']*5,'address':'chị'}).status_code,200)
        return sid

    def test_member_all_three_apis_share_rate_and_daily_budget(self):
        with patch.dict(os.environ,{'AI_USER_PER_MINUTE':'2'}):
            self.assertEqual(self.send(member=True).status_code,200)
            self.assertEqual(self.send('story',member=True).status_code,200)
            sid=self.chat_session(True)
            response=self.client.post('/api/ai/chat',headers=self.headers(True),json={'session_id':sid,'request_id':str(uuid4()),'message':'Em thích vẽ'})
            self.assertEqual(response.status_code,429,response.text)
        with patch.dict(os.environ,{'AI_USER_PER_DAY':'2'}):self.assertEqual(self.send(member=True).status_code,429)

    def test_guest_eight_shared_questions_then_429_and_retry_free(self):
        uid=self.guest();sid=self.chat_session()
        response=self.client.post('/api/ai/chat',json={'session_id':sid,'request_id':str(uuid4()),'message':'Em thích vẽ'})
        self.assertEqual(response.status_code,200,response.text)
        final_id=None
        for index in range(7):
            final_id=str(uuid4())
            self.assertEqual(self.send('story' if index%2 else 'advice',request_id=final_id).status_code,200)
        self.assertEqual(get_guest_usage(uid)['used_questions'],8)
        self.assertEqual(self.send().status_code,429)
        self.assertEqual(self.send('advice',request_id=final_id).status_code,200)
        self.assertEqual(get_guest_usage(uid)['used_questions'],8)

    def test_invalid_expired_or_malformed_token_never_falls_back_to_valid_cookie(self):
        self.guest()
        for token in ('expired','forged','Basic abc','Bearer '):
            authorization=token if token.startswith(('Basic','Bearer')) else 'Bearer '+token
            for url in ('/api/advice','/api/career-stories/bac-si/ask'):
                self.assertEqual(self.client.post(url,headers={'Authorization':authorization},json={'question':'Em thích vẽ'}).status_code,401)
        self.client.cookies.clear()
        self.assertEqual(self.send().status_code,401)

    def test_forged_client_identity_fields_are_rejected_and_owner_isolated(self):
        self.guest();sid=self.chat_session()
        for field in ('user_id','guest_id','role','quota'):
            self.assertEqual(self.send(**{field:'member'}).status_code,422)
        self.assertEqual(self.client.get('/api/ai/sessions/'+sid,headers={'Authorization':'Bearer other'}).status_code,404)
        self.assertEqual(self.client.post('/api/ai/chat',headers={'Authorization':'Bearer other'},json={'session_id':sid,'request_id':str(uuid4()),'message':'Em thích vẽ'}).status_code,404)

    def test_two_concurrent_legacy_routes_cannot_exceed_shared_guest_quota(self):
        uid=self.guest()
        for _ in range(7):self.assertEqual(self.send().status_code,200)
        cookie=self.client.cookies.get('laban_guest')
        def invoke(kind):
            with TestClient(application.app,client=('127.0.0.1',41001)) as client:
                client.cookies.set('laban_guest',cookie)
                return self.send(kind,client=client).status_code
        with ThreadPoolExecutor(2) as pool:results=list(pool.map(invoke,('advice','story')))
        self.assertCountEqual(results,[200,429])
        self.assertEqual(get_guest_usage(uid)['used_questions'],8)

    def test_firebase_anonymous_and_rotated_cookie_share_ip_budget(self):
        with patch.dict(os.environ,{'AI_IP_PER_MINUTE':'2'}):
            self.guest();self.assertEqual(self.send().status_code,200)
            response=self.client.post('/api/advice',headers={'Authorization':'Bearer firebase-guest'},json={'question':'Em thích vẽ'})
            self.assertEqual(response.status_code,200,response.text)
            self.client.cookies.clear();self.guest()
            response=self.send()
            self.assertEqual(response.status_code,429,response.text)

    def test_spoofed_forwarding_headers_cannot_reset_identity_or_ip_rate(self):
        self.guest()
        with patch.dict(os.environ,{'AI_IP_PER_MINUTE':'1'}):
            self.assertEqual(self.send().status_code,200)
            response=self.client.post('/api/advice',headers={'X-Forwarded-For':'9.9.9.9','X-Real-IP':'8.8.8.8','X-User-ID':'someone'},json={'question':'Em thích vẽ'})
            self.assertEqual(response.status_code,429,response.text)
        def req(peer, forwarded):return Request({'type':'http','client':(peer,1),'headers':[(b'x-forwarded-for',forwarded.encode())]})
        with patch.dict(os.environ,{'AI_TRUSTED_PROXY_CIDRS':'10.0.0.0/8'}):
            self.assertEqual(client_ip(req('10.1.0.1','6.6.6.6, 8.8.8.8, 10.0.0.2')),'8.8.8.8')
            self.assertEqual(client_ip(req('127.0.0.1','6.6.6.6')),'127.0.0.1')
            with self.assertRaises(HTTPException) as error:client_ip(req('10.1.0.1','forged address'))
            self.assertEqual(error.exception.status_code,400)
            duplicate=Request({'type':'http','client':('10.1.0.1',1),'headers':[(b'x-forwarded-for',b'1.1.1.1'),(b'x-forwarded-for',b'2.2.2.2')]})
            with self.assertRaises(HTTPException) as error:client_ip(duplicate)
            self.assertEqual(error.exception.status_code,400)

    def test_cookie_security_issuance_limit_ttl_hash_and_csrf(self):
        uid=self.guest();raw=self.client.cookies.get('laban_guest')
        with self.connection() as db:
            row=db.execute('SELECT * FROM advisor_guest_sessions WHERE uid=%s',(uid,)).fetchone()
            self.assertEqual(row['token_hash'],hashlib.sha256(raw.encode()).hexdigest())
            self.assertNotIn(raw,str(row))
        self.assertEqual(self.client.post('/api/advice',headers={'Origin':'https://evil.example'},json={'question':'Em thích vẽ'}).status_code,403)
        for _ in range(2):self.client.cookies.clear();self.guest()
        self.client.cookies.clear();self.assertEqual(self.client.post('/api/ai/guest/session').status_code,429)
        with self.connection() as db:db.execute('UPDATE advisor_guest_sessions SET expires_at=NOW()-INTERVAL \'1 second\',created_at=NOW()-INTERVAL \'1 day\' WHERE uid=%s',(uid,))
        self.client.cookies.set('laban_guest',raw)
        self.assertEqual(self.send().status_code,401)
        with TestClient(application.app,base_url='https://laban.example',client=('127.0.0.2',1)) as secure:
            response=secure.post('/api/ai/guest/session')
            self.assertEqual(response.status_code,200,response.text)
            self.assertIn('__Host-laban_guest=',response.headers['set-cookie'])
            for flag in ('HttpOnly','Secure','SameSite=strict','Path=/'):self.assertIn(flag,response.headers['set-cookie'])

    def test_legacy_duplicate_hash_failure_refund_and_saved_pair_no_refund(self):
        uid=self.guest();rid=str(uuid4())
        self.assertEqual(self.send(request_id=rid).status_code,200)
        self.assertTrue(self.send(request_id=rid).json()['duplicate'])
        self.assertEqual(self.send(request_id=rid,question='Nội dung khác').status_code,409)
        with patch('ai.advice_graph.ainvoke',side_effect=TimeoutError('private')):
            self.assertEqual(self.send().status_code,504)
        self.assertEqual(get_guest_usage(uid)['used_questions'],1)
        original=pg.save_messages_atomic
        def committed(*args,**kwargs):original(*args,**kwargs);raise RuntimeError('response after commit')
        with patch('advisor.legacy_ai.save_messages_atomic',side_effect=committed):self.assertEqual(self.send().status_code,502)
        self.assertEqual(get_guest_usage(uid)['used_questions'],2)

    def test_cookie_upgrade_preserves_history_quota_and_rejects_double_claim(self):
        uid=self.guest();sid=self.chat_session()
        self.assertEqual(self.send().status_code,200)
        raw=self.client.cookies.get('laban_guest')
        result=self.client.post('/api/ai/guest/claim',headers=self.headers(True),json={})
        self.assertEqual(result.status_code,200,result.text)
        self.assertIn(sid,result.json()['session_ids'])
        self.assertEqual(self.client.get('/api/ai/sessions/'+sid,headers=self.headers(True)).status_code,200)
        self.client.cookies.set('laban_guest',raw)
        self.assertEqual(self.send().status_code,401)
        self.assertEqual(self.client.post('/api/ai/guest/claim',headers={'Authorization':'Bearer other'},json={}).status_code,401)
        with self.connection() as db:self.assertEqual(db.execute('SELECT used_questions FROM guest_ai_usage WHERE uid=%s',(uid,)).fetchone()['used_questions'],1)

    def test_missing_shared_database_or_guest_table_fails_closed(self):
        with patch.dict(os.environ,{'DATABASE_URL':'sqlite:///:memory:'}):
            self.assertEqual(self.send(member=True).status_code,503)
            self.assertEqual(self.client.post('/api/ai/guest/session').status_code,503)
        empty=self.cluster.schema(initialize=False)
        with patch.object(pg,'postgres_connection',empty):
            self.assertEqual(self.client.post('/api/ai/guest/session').status_code,503)
        for value in ('0','-1','not-an-integer','100001'):
            with patch.dict(os.environ,{'AI_USER_PER_MINUTE':value}):self.assertEqual(self.send(member=True).status_code,503)

    def test_member_concurrent_duplicate_uses_row_lease_without_charging_guest_counter(self):
        rid=str(uuid4())
        async def slow(state):
            await asyncio.sleep(.25)
            return {'answer':'Một gợi ý nghề nghiệp.'}
        def send(_):
            with TestClient(application.app,client=('127.0.0.1',1)) as client:
                return self.send(member=True,request_id=rid,client=client).status_code
        with patch('ai.advice_graph.ainvoke',side_effect=slow) as graph:
            with ThreadPoolExecutor(2) as pool:results=list(pool.map(send,range(2)))
            self.assertCountEqual(results,[200,409])
            self.assertEqual(graph.call_count,1)
            self.assertEqual(self.send(member=True,request_id=rid).status_code,200)
            self.assertEqual(graph.call_count,1)
        with self.connection() as db:
            row=db.execute('SELECT status,charge_quota FROM guest_ai_requests WHERE request_id=%s',(rid,)).fetchone()
            self.assertEqual(row,{'status':'completed','charge_quota':False})
            self.assertEqual(db.execute("SELECT used_questions FROM guest_ai_usage WHERE uid='member'").fetchone()['used_questions'],0)

    def test_member_expired_lease_fences_old_worker_and_cannot_refund_prior_guest_usage(self):
        from advisor.guest_quota import reserve_guest_request, finish_guest_request
        sid=self.chat_session(True);rid=str(uuid4())
        with self.connection() as db:db.execute("INSERT INTO guest_ai_usage(uid,used_questions) VALUES('member',7)")
        old=reserve_guest_request('member',sid,rid,'same',False)
        with self.connection() as db:db.execute("UPDATE guest_ai_requests SET lease_until=NOW()-INTERVAL '1 second' WHERE request_id=%s",(rid,))
        new=reserve_guest_request('member',sid,rid,'same',False)
        self.assertNotEqual(old['reservation_token'],new['reservation_token'])
        reply={'answer':'safe','profile':empty_profile(),'summary':'','recommendations':[]}
        with self.assertRaises(HTTPException):pg.save_messages_atomic('member',sid,rid,'same',reply,'live',old['reservation_token'])
        finish_guest_request('member',rid,False,old['reservation_token'])
        pg.save_messages_atomic('member',sid,rid,'same',reply,'live',new['reservation_token'])
        finish_guest_request('member',rid,False,new['reservation_token'])
        self.assertEqual(get_guest_usage('member')['used_questions'],7)

    def test_request_id_reuse_across_scopes_cannot_repeat_member_provider_call(self):
        rid=str(uuid4())
        self.assertEqual(self.send(member=True,request_id=rid).status_code,200)
        self.assertEqual(self.send('story',member=True,request_id=rid).status_code,409)
        sid=self.chat_session(True)
        self.assertEqual(self.client.post('/api/ai/chat',headers=self.headers(True),json={'session_id':sid,'request_id':rid,'message':'Em thích vẽ'}).status_code,409)
        self.assertEqual(self.mocks[5].call_count,0)
        self.assertEqual(self.mocks[6].call_count,0)

    def test_voice_provider_is_rate_limited_without_consuming_llm_quota(self):
        from test_advisor import wav_audio
        uid=self.guest()
        with patch('advisor.voice.google_stt_configured',return_value=True),patch('advisor.voice.transcribe',return_value='Em thích vẽ') as speech,patch.dict(os.environ,{'AI_IP_PER_MINUTE':'1'}):
            response=self.client.post('/api/voice/transcribe',content=wav_audio())
            self.assertEqual(response.status_code,200,response.text)
            self.assertEqual(self.client.post('/api/voice/transcribe',content=wav_audio()).status_code,429)
            self.assertEqual(speech.call_count,1)
        self.assertEqual(get_guest_usage(uid)['used_questions'],0)
