"""PostgreSQL LOCAL, Firebase/model fixture; never Production SQL/provider calls."""
import asyncio,copy,json,os,unittest
from unittest.mock import patch,AsyncMock
from concurrent.futures import ThreadPoolExecutor
from uuid import uuid4
import test_advisor30_profile as base
from postgres_fixture import LocalPostgres
from advisor import analysis_jobs as jobs
from advisor.survey_analysis import validate_analysis
from advisor.store import get_store
class JobTests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):cls.cluster=LocalPostgres().__enter__()
 @classmethod
 def tearDownClass(cls):cls.cluster.__exit__(None,None,None)
 def setUp(self):
  self.env=patch.dict(os.environ,{'DEEPSEEK_API_KEY':'unit-test-key','AI_DEMO_MODE':'false','ADVISOR_CONTROLLED_ROLLOUT':'false','AI_TRUSTED_PROXY_CIDRS':''});self.env.start()
  self.f=base.ProfileTests();self.f.cluster=self.cluster;self.f.setUp();self.client=self.f.client;self.sid=self.new_session()
  row=get_store().get('owner-one',self.sid);self.survey=row['messages'][0]['survey'];self.result=validate_analysis(base.RAW,self.survey,self.sid)
 def tearDown(self):self.f.tearDown();self.env.stop()
 def new_session(self):
  sid=self.client.post('/api/ai/sessions',json={'remember':False}).json()['session']['id']
  r=self.client.put('/api/ai/sessions/'+sid+'/survey',json={'answers':base.ANSWERS});self.assertEqual(r.status_code,200);return sid
 def post(self,retry=False,sid=None):return self.client.post('/api/ai/sessions/'+(sid or self.sid)+'/analysis',json={'retry':retry})
 def test_pending_then_completed_cached_no_chat_charge_or_auto_save(self):
  self.assertEqual(self.client.get('/api/ai/sessions/'+self.sid+'/analysis').json()['status'],'pending')
  with patch('advisor.survey_analysis.generate_analysis',AsyncMock(return_value=self.result)) as ai:
   for _ in range(3):self.assertEqual(self.post().json()['status'],'completed')
   self.assertEqual(ai.await_count,1)
  row=get_store().get('owner-one',self.sid);self.assertEqual(len(row['messages']),1);self.assertEqual(row['messages'][0]['analysis_job']['attempts'],1)
  self.assertEqual(self.client.get('/api/ai/career-profile').json()['items'],[])
  with self.f.connection() as db:self.assertEqual(db.execute("SELECT used_questions AS n FROM guest_ai_usage WHERE uid='owner-one'").fetchone()['n'],0)
 def test_concurrent_calls_get_single_provider_attempt(self):
  async def slow(*a):await asyncio.sleep(.2);return self.result
  with patch('advisor.survey_analysis.generate_analysis',AsyncMock(side_effect=slow)) as ai,ThreadPoolExecutor(max_workers=2) as pool:
   results=list(pool.map(lambda _:self.post().json()['status'],range(2)));self.assertEqual(ai.await_count,1)
  self.assertIn('completed',results);self.assertTrue(set(results)<={'completed','processing'})
 def test_failure_requires_explicit_retry_and_no_automatic_repeat(self):
  with patch('advisor.survey_analysis.generate_analysis',AsyncMock(side_effect=ValueError('synthetic provider error'))) as ai:
   self.assertEqual(self.post().json()['status'],'failed');self.assertEqual(self.post().json()['status'],'failed');self.assertEqual(ai.await_count,1)
  with patch('advisor.survey_analysis.generate_analysis',AsyncMock(return_value=self.result)) as ai:
   self.assertEqual(self.post(True).json()['status'],'completed');self.assertEqual(ai.await_count,1)
 def test_stale_worker_cannot_overwrite_new_lease(self):
  _,first,_=jobs.claim('owner-one',self.sid,'127.0.0.1')
  with self.f.connection() as db:db.execute("UPDATE advisor_temporary_sessions SET messages=jsonb_set(messages::jsonb,'{0,analysis_job,lease_until}','0')::text WHERE id=%s",(self.sid,))
  _,second,_=jobs.claim('owner-one',self.sid,'127.0.0.1');self.assertNotEqual(first,second)
  self.assertEqual(jobs.finish('owner-one',self.sid,first,jobs.fingerprint(self.survey),self.result)['status'],'processing')
  self.assertEqual(jobs.finish('owner-one',self.sid,second,jobs.fingerprint(self.survey),self.result)['status'],'completed')
 def test_ownership_and_payload_forgery(self):
  self.f.identity={'uid':'owner-other','provider':'password'}
  self.assertEqual(self.post().status_code,404);self.assertEqual(self.client.get('/api/ai/sessions/'+self.sid+'/analysis').status_code,404)
  self.assertEqual(self.client.post('/api/ai/sessions/'+self.sid+'/analysis',json={'retry':False,'uid':'owner-one'}).status_code,422)
 def test_separate_budget_shared_pg_no_forwarded_header_bypass(self):
  with patch.dict(os.environ,{'ANALYSIS_USER_PER_DAY':'1'}),patch('advisor.survey_analysis.generate_analysis',AsyncMock(return_value=self.result)) as ai:
   self.assertEqual(self.post().json()['status'],'completed');other=self.new_session()
   r=self.client.post('/api/ai/sessions/'+other+'/analysis',json={},headers={'X-Forwarded-For':'203.0.113.8'});self.assertEqual(r.status_code,429)
   self.assertEqual(self.post().json()['status'],'completed');self.assertEqual(ai.await_count,1)
 def test_confirm_and_reject_from_job_without_chat_message(self):
  with patch('advisor.survey_analysis.generate_analysis',AsyncMock(return_value=self.result)):self.post()
  p=self.result['proposed_profile_items'][0];r=self.client.post('/api/ai/career-profile/items',json={'session_id':self.sid,'proposal_id':p['id'],'value':p['value'],'confirmed':True});self.assertEqual(r.status_code,200);self.assertEqual(len(r.json()['items']),1)
  other=self.result['proposed_profile_items'][1]['id'];self.assertEqual(self.client.post('/api/ai/sessions/'+self.sid+'/profile-proposals/'+other+'/reject').status_code,200)
  self.assertIn(other,get_store().get('owner-one',self.sid)['messages'][0]['profile_rejections'])
 def test_guest_analysis_keeps_eight_chat_questions(self):
  self.f.identity['provider']='anonymous'
  before=self.client.get('/api/ai/config').json()['guest_quota']
  with patch('advisor.survey_analysis.generate_analysis',AsyncMock(return_value=self.result)):self.post()
  after=self.client.get('/api/ai/config').json()['guest_quota'];self.assertEqual(before,after);self.assertEqual(after['remaining'],8)
 def test_committed_job_is_cached_after_response_failure(self):
  real=jobs.finish
  def after_commit(*a,**kw):real(*a,**kw);raise RuntimeError('fixture response interrupted after commit')
  with patch('advisor.survey_analysis.generate_analysis',AsyncMock(return_value=self.result)) as ai:
   with patch('advisor.analysis_jobs.finish',after_commit):
    with self.assertRaises(RuntimeError):self.post()
   self.assertEqual(self.post().json()['status'],'completed');self.assertEqual(ai.await_count,1)
 def test_repeated_vague_answers_do_not_trigger_false_verbatim_rejection(self):
  survey={**self.survey,'answers':['Em chưa rõ']*5}
  raw={'summary':'Em chưa rõ sở thích hay môi trường mong muốn; cần thử một hoạt động nhỏ trước.','proposed_profile_items':[],'clarification_questions':['Bạn muốn thử hoạt động nào trước?']}
  self.assertEqual(validate_analysis(raw,survey,self.sid)['proposed_profile_items'],[])
  raw['summary']=' '.join(survey['answers'])
  with self.assertRaises(ValueError):validate_analysis(raw,survey,self.sid)

 def test_missing_provider_does_not_spend_budget_and_cache_survives_key_removed(self):
  with patch.dict(os.environ,{'DEEPSEEK_API_KEY':''}),patch('advisor.survey_analysis.generate_analysis',AsyncMock()) as ai:
   self.assertEqual(self.post().json()['status'],'failed');self.assertEqual(ai.await_count,0)
  with patch('advisor.survey_analysis.generate_analysis',AsyncMock(return_value=self.result)) as ai:
   self.assertEqual(self.post(True).json()['status'],'completed')
   with patch.dict(os.environ,{'DEEPSEEK_API_KEY':''}):self.assertEqual(self.post().json()['status'],'completed')
   self.assertEqual(ai.await_count,1)

 def test_chat_save_and_analysis_finish_preserve_each_other(self):
  from advisor.guest_quota import reserve_guest_request
  from advisor.postgres_store import save_messages_atomic
  for finish_first in [True,False]:
   sid=self.new_session();survey=get_store().get('owner-one',sid)['messages'][0]['survey']
   result=validate_analysis(base.RAW,survey,sid);_,attempt,_=jobs.claim('owner-one',sid,'127.0.0.1')
   rid=str(uuid4());reservation=reserve_guest_request('owner-one',sid,rid,'Fixture chat',False)
   if finish_first:jobs.finish('owner-one',sid,attempt,jobs.fingerprint(survey),result)
   save_messages_atomic('owner-one',sid,rid,'Fixture chat',{'answer':'Fixture answer','profile':{'interests':[],'strengths':[],'growth_skills':[],'careers':[]},'summary':'','recommendations':[]},'live',reservation['reservation_token'])
   if not finish_first:jobs.finish('owner-one',sid,attempt,jobs.fingerprint(survey),result)
   row=get_store().get('owner-one',sid);self.assertEqual(len(row['messages']),3);self.assertEqual(row['messages'][0]['analysis_job']['status'],'completed')
 def test_chat_attaches_compact_insights_not_proposals_every_turn(self):
  with patch('advisor.survey_analysis.generate_analysis',AsyncMock(return_value=self.result)):self.post()
  state=jobs.attach_analysis({'session':get_store().get('owner-one',self.sid)})
  self.assertIsNone(state['survey_analysis']);self.assertNotIn('proposed_profile_items',state['survey_insights']);self.assertEqual(state['survey_insights']['summary'],self.result['summary'])
 def test_lack_of_confidence_is_never_classified_as_strength(self):
  survey={**self.survey,'answers':[*self.survey['answers']]};survey['answers'][2]='Em kiên nhẫn nhưng chưa tự tin giao tiếp'
  raw={'summary':'Học sinh tự nhận kiên nhẫn, chưa tự tin giao tiếp; không phải đánh giá năng lực.',
       'proposed_profile_items':[{'category':'strengths','value':'Chưa tự tin giao tiếp','evidence':[{'question_id':3,'excerpt':'chưa tự tin giao tiếp'}],'confidence':'rõ ràng','inference_type':'trực tiếp','proposed_action':'confirm'}],
       'clarification_questions':[]}
  with self.assertRaisesRegex(ValueError,'confidence_is_not_strength'):validate_analysis(raw,survey,self.sid)
  p=raw['proposed_profile_items'][0];p.update(category='uncertainties',proposed_action='clarify')
  self.assertEqual(validate_analysis(raw,survey,self.sid)['strengths'],[])
  p.update(category='strengths',value='Tự nhận kiên nhẫn',evidence=[{'question_id':3,'excerpt':'kiên nhẫn'}],proposed_action='confirm')
  self.assertEqual(validate_analysis(raw,survey,self.sid)['strengths'],['Tự nhận kiên nhẫn'])
