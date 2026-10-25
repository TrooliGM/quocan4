"""One real graph/provider contract, local PG and mocked provider; never LIVE PASS."""
import json,os,unittest
from unittest.mock import patch
from uuid import uuid4
import httpx
import test_advisor30_profile as base
from postgres_fixture import LocalPostgres
from advisor.store import get_store,empty_profile

class UnifiedTests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):cls.cluster=LocalPostgres().__enter__()
 @classmethod
 def tearDownClass(cls):cls.cluster.__exit__(None,None,None)
 def setUp(self):
  self.env=patch.dict(os.environ,{'ADVISOR_CONTROLLED_ROLLOUT':'true','ADVISOR_TEST_UIDS':'qa-test','AI_DEMO_MODE':'false','DEEPSEEK_API_KEY':'fixture-key','SEARCH_PROVIDER':'','SEARCH_API_KEY':''});self.env.start()
  self.f=base.ProfileTests();self.f.cluster=self.cluster;self.f.setUp();self.client=self.f.client;self.payloads=[]
  async def provider(payload,**kw):
   self.payloads.append(payload)
   text=json.dumps({'profile':empty_profile(),'summary':'Synthetic bounded summary'}) if payload['max_tokens']==1800 else 'Một câu trả lời fixture từ pipeline Task4.1.'
   return httpx.Response(200,json={'choices':[{'message':{'content':text},'finish_reason':'stop'}]})
  self.provider=patch('advisor.graph.post_completion',provider);self.provider.start()
  self.legacy=patch('advisor.stable_graph.advisor_graph.ainvoke',side_effect=AssertionError('silent legacy fallback'));self.legacy.start()
 def tearDown(self):self.legacy.stop();self.provider.stop();self.f.tearDown();self.env.stop()
 def session(self,uid,provider='password',remember=False,mode='career_discovery'):
  self.f.identity={'uid':uid,'provider':provider}
  body={'remember':remember,'mode':mode}
  if mode=='career_exploration':body['career_id']='kiem-sat-vien'
  r=self.client.post('/api/ai/sessions',json=body);self.assertEqual(r.status_code,201)
  sid=r.json()['session']['id'];self.assertEqual(self.client.put('/api/ai/sessions/'+sid+'/survey',json={'answers':base.ANSWERS}).status_code,200)
  return sid
 def chat(self,sid,message='Nói ngắn gọn nghề này làm gì?',rid=None):
  return self.client.post('/api/ai/chat',json={'session_id':sid,'request_id':rid or str(uuid4()),'message':message})
 def test_all_roles_and_all_three_endpoints_use_same_answer_engine(self):
  for uid,role in [('guest-test','anonymous'),('member-test','password'),('qa-test','password')]:
   sid=self.session(uid,role)
   for path,body in [('/api/ai/chat',{'session_id':sid,'message':'Giải thích ngắn nghề thiết kế'}),('/api/advice',{'question':'Giải thích ngắn nghề thiết kế'}),('/api/career-stories/bac-si/ask',{'question':'Giải thích ngắn nghề thiết kế','scene_index':0})]:
    r=self.client.post(path,json={**body,'request_id':str(uuid4())});self.assertEqual(r.status_code,200,r.text)
    self.assertEqual(r.json()['pipeline'],'task41');self.assertIn('ai_pipeline;desc="task41"',r.headers['server-timing'])
  self.assertEqual(len(self.payloads),9)
  self.assertEqual(len({p['messages'][0]['content'] for p in self.payloads}),1)
  self.assertTrue(all(any(m['content'].startswith('Kế hoạch trả lời') for m in p['messages']) for p in self.payloads))
  self.assertIn('Cảnh đang xem',json.dumps(self.payloads[-1],ensure_ascii=False))
 def test_guest_and_member_cannot_read_confirmed_profile_even_if_old_session_opted_in(self):
  for uid,role in [('guest-test','anonymous'),('member-test','password')]:
   sid=self.session(uid,role);row=get_store().get(uid,sid);row['messages'][0]['use_confirmed_profile']=True;get_store().write(uid,row)
   with patch('advisor.confirmed_profile.context_items',side_effect=AssertionError('private profile read forbidden')):
    self.assertEqual(self.chat(sid).status_code,200)
   block=next(m['content'] for m in self.payloads[-1]['messages'] if m['content'].startswith('HỒ SƠ ĐÃ XÁC NHẬN'))
   self.assertFalse(json.loads(block.split('\n',1)[1])['enabled'])
 def test_old_and_new_sessions_both_modes_temporary_and_durable(self):
  for remember in [False,True]:
   for mode in ['career_discovery','career_exploration']:
    sid=self.session('member-test',remember=remember,mode=mode)
    first=self.chat(sid);self.assertEqual(first.status_code,200);second=self.chat(sid,'nghề đó cần kỹ năng gì?')
    self.assertEqual(second.status_code,200);row=second.json()['session'];self.assertEqual(len(row['messages']),5)
    self.assertEqual(row['messages'][0]['career_context']['mode'],mode)
    if mode=='career_exploration':self.assertEqual(row['messages'][0]['career_context']['career_id'],'kiem-sat-vien')
 def test_guest_eight_questions_shared_with_compatibility_api_duplicate_free_and_ninth_blocked(self):
  sid=self.session('guest-test','anonymous');rid=str(uuid4());self.assertEqual(self.chat(sid,rid=rid).status_code,200)
  count=len(self.payloads);self.assertTrue(self.chat(sid,rid=rid).json()['duplicate']);self.assertEqual(len(self.payloads),count)
  for _ in range(6):self.assertEqual(self.chat(sid).status_code,200)
  r=self.client.post('/api/advice',json={'question':'Câu thứ tám dùng cùng pipeline','request_id':str(uuid4())});self.assertEqual(r.status_code,200);self.assertEqual(r.json()['guest_quota']['remaining'],0)
  count=len(self.payloads);self.assertEqual(self.chat(sid).status_code,429);self.assertEqual(len(self.payloads),count)
 def test_errors_never_fall_back_and_analysis_ownership_still_enforced(self):
  sid=self.session('guest-test','anonymous')
  with patch('advisor.graph.post_completion',side_effect=httpx.ReadTimeout('fixture error')):
   self.assertEqual(self.chat(sid).status_code,504)
  self.assertEqual(self.client.get('/api/ai/config').json()['guest_quota']['remaining'],8)
  self.f.identity={'uid':'other-member','provider':'password'}
  self.assertEqual(self.client.get('/api/ai/sessions/'+sid).status_code,404)
  self.assertEqual(self.client.post('/api/ai/sessions/'+sid+'/analysis',json={}).status_code,404)
  self.assertEqual(self.chat(sid).status_code,404)

 def test_all_roles_get_owned_analysis_without_chat_charge_or_profile_permission(self):
  from unittest.mock import AsyncMock
  from advisor.survey_analysis import validate_analysis
  async def analyze(survey,sid):return validate_analysis(base.RAW,survey,sid)
  with patch('advisor.survey_analysis.generate_analysis',AsyncMock(side_effect=analyze)) as model:
   for uid,role in [('guest-test','anonymous'),('member-test','password'),('qa-test','password')]:
    sid=self.session(uid,role)
    for _ in range(2):
     result=self.client.post('/api/ai/sessions/'+sid+'/analysis',json={});self.assertEqual(result.status_code,200)
     self.assertEqual(result.json()['status'],'completed')
    with self.f.connection() as db:self.assertEqual(db.execute('SELECT count(*) AS n FROM advisor_profile_items WHERE owner=%s',(uid,)).fetchone()['n'],0)
    if role=='anonymous':self.assertEqual(self.client.get('/api/ai/config').json()['guest_quota']['remaining'],8)
    proposal=result.json()['result']['proposed_profile_items'][0]
    body={'session_id':sid,'proposal_id':proposal['id'],'value':proposal['value'],'confirmed':True}
    self.assertEqual(self.client.post('/api/ai/career-profile/items',json=body).status_code,200 if uid=='qa-test' else 404)
   self.assertEqual(model.await_count,3)
