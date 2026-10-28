"""Cá nhân hóa bằng phiên hiện tại, không đọc Hồ sơ riêng. Chỉ PG/model LOCAL."""
import copy,json,os,unittest
from unittest.mock import patch
from uuid import uuid4
import httpx
import test_advisor30_profile as baseline
from postgres_fixture import LocalPostgres
from advisor.store import get_store,empty_profile

class PersonalizationTests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):cls.cluster=LocalPostgres().__enter__()
 @classmethod
 def tearDownClass(cls):cls.cluster.__exit__(None,None,None)
 def setUp(self):
  self.f=baseline.ProfileTests();self.f.cluster=self.cluster;self.f.setUp();self.client=self.f.client;self.calls=[]
 def tearDown(self):self.f.tearDown()
 def chat(self,sid=None):
  async def provider(payload,**kwargs):
   self.calls.append(copy.deepcopy(payload))
   text=json.dumps({'profile':empty_profile(),'summary':'Fixture only'}) if payload['max_tokens']==1800 else 'Fixture provider, không phải AI thật.'
   return httpx.Response(200,json={'choices':[{'message':{'content':text},'finish_reason':'stop'}]})
  with patch.dict(os.environ,{'AI_DEMO_MODE':'false','DEEPSEEK_API_KEY':'unit-test-key'}),patch('advisor.graph.post_completion',provider),patch('advisor.confirmed_profile.context_items',side_effect=AssertionError('private profile read')):
   r=self.client.post('/api/ai/chat',json={'session_id':sid or self.f.session['id'],'request_id':str(uuid4()),'message':'Anh gợi ý cho em một vài hoạt động khám phá nghề nhé.'})
  self.assertEqual(r.status_code,200)
  payload=next(p for p in reversed(self.calls) if any(m['content'].startswith('Dữ liệu ngữ cảnh') for m in p['messages']))
  self.assertFalse(any(m['content'].startswith('HỒ SƠ ĐÃ XÁC NHẬN') for m in payload['messages']))
  return payload
 def context(self,payload):return json.loads(next(m['content'] for m in payload['messages'] if m['content'].startswith('Dữ liệu ngữ cảnh')).split('\n',1)[1])
 def test_old_opt_in_cannot_enable_private_profile(self):
  self.f.accept();row=self.f.session;row['messages'][0]['use_confirmed_profile']=True;get_store().write('owner-one',row)
  payload=self.chat();self.assertNotIn(self.f.body()['value'],json.dumps(payload,ensure_ascii=False))
 def test_fresh_session_does_not_import_other_session_notes_or_confirmed_values(self):
  self.f.accept();row=get_store().create('owner-one',False);row['messages'][0]['survey_required']=False;get_store().write('owner-one',row)
  payload=self.chat(row['id']);self.assertEqual(self.context(payload)['conversation_notes'],empty_profile());self.assertNotIn(self.f.body()['value'],json.dumps(payload,ensure_ascii=False))
 def test_current_session_notes_summary_and_survey_remain_available(self):
  row=self.f.session;row['profile']['interests']=['Ghi chú do học sinh chia sẻ trong phiên'];row['summary']='Tóm tắt của phiên hiện tại';get_store().write('owner-one',row)
  context=self.context(self.chat());self.assertEqual(context['summary'],row['summary']);self.assertEqual(context['conversation_notes'],row['profile']);self.assertTrue(context['survey'])
 def test_other_owner_cannot_read_session_or_import_legacy_profile(self):
  self.f.accept();sid=self.f.session['id'];self.f.identity={'uid':'owner-two','provider':'password'}
  self.assertEqual(self.client.get('/api/ai/sessions/'+sid).status_code,404)
  row=get_store().create('owner-two',False);row['messages'][0]['survey_required']=False;get_store().write('owner-two',row)
  self.assertEqual(self.context(self.chat(row['id']))['conversation_notes'],empty_profile())
