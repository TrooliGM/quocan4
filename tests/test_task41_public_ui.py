"""Presentation flag must never authorize the QA-only backend. Local PG/verified-user fixture."""
import os,unittest
from unittest.mock import patch
from uuid import uuid4
import test_advisor30_profile as base
from postgres_fixture import LocalPostgres

class PublicUITests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):cls.cluster=LocalPostgres().__enter__()
 @classmethod
 def tearDownClass(cls):cls.cluster.__exit__(None,None,None)
 def setUp(self):
  self.env=patch.dict(os.environ,{'VERCEL_ENV':'preview','ADVISOR_PREMIUM_UI_PREVIEW':'true','ADVISOR_CONTROLLED_ROLLOUT':'true','ADVISOR_TEST_UIDS':'qa-only','AI_DEMO_MODE':'true'});self.env.start()
  self.f=base.ProfileTests();self.f.cluster=self.cluster;self.f.setUp();self.client=self.f.client;self.sid=self.f.session['id']
 def tearDown(self):self.f.tearDown();self.env.stop()
 def assert_public_ui_without_backend(self):
  page=self.client.get('/ai-career-advisor')
  self.assertEqual(page.status_code,200);self.assertIn('Trợ lý hướng nghiệp',page.text)
  self.assertIn('Đồng hành cùng bạn khám phá nghề nghiệp',page.text)
  self.assertNotIn('advisor-entry.js',page.text);self.assertIn('task41-public-ui-1',page.text)
  self.assertEqual(page.headers['cache-control'],'no-store')
  config=self.client.get('/api/ai/config').json()
  self.assertTrue(config['premium_ui_public'])
  for flag in ['task4_enabled','automatic_analysis','profile_enabled']:self.assertFalse(config[flag])
  # The legacy GET returns this owner's conversation notes, not confirmed items.
  legacy=self.client.get('/api/ai/career-profile');self.assertEqual(legacy.status_code,200);self.assertNotIn('items',legacy.json())
  for path in ['/api/ai/task4-shell','/api/ai/sessions/'+self.sid+'/analysis']:
   self.assertEqual(self.client.get(path).status_code,404)
  self.assertEqual(self.client.post('/api/ai/sessions/'+self.sid+'/analysis',json={}).status_code,404)
  self.assertEqual(self.client.post('/api/ai/career-profile/items',json=self.f.body()).status_code,404)
 def test_guest_sees_new_ui_without_gaining_analysis_or_profile(self):
  self.f.identity['provider']='anonymous';self.assert_public_ui_without_backend()
  self.assertEqual(self.client.get('/api/ai/config').json()['guest_quota']['remaining'],8)
 def test_member_still_uses_stable_ai_graph(self):
  self.assert_public_ui_without_backend()
  with patch('advisor.routes.advisor_graph.ainvoke',side_effect=AssertionError('UI flag must not open Task4 graph')):
   r=self.client.post('/api/ai/chat',json={'session_id':self.sid,'request_id':str(uuid4()),'message':'Em thích vẽ'})
  self.assertEqual(r.status_code,200);self.assertNotIn('survey_analysis',r.json()['session']['messages'][-1])
 def test_verified_qa_retains_analysis_and_profile_access(self):
  with patch.dict(os.environ,{'ADVISOR_TEST_UIDS':'owner-one'}):
   config=self.client.get('/api/ai/config').json()
   self.assertTrue(config['premium_ui_public']);self.assertTrue(config['automatic_analysis']);self.assertTrue(config['profile_enabled'])
   self.assertEqual(self.client.get('/api/ai/career-profile').status_code,200)
   self.assertEqual(self.client.post('/api/ai/sessions/'+self.sid+'/analysis',json={}).json()['status'],'completed')
 def test_production_cannot_enable_public_ui_even_with_flag_or_query(self):
  with patch.dict(os.environ,{'VERCEL_ENV':'production'}):
   self.assertFalse(self.client.get('/api/ai/config?premium_ui_public=true').json()['premium_ui_public'])
   page=self.client.get('/ai-career-advisor?preview=1')
   self.assertIn('advisor-entry.js',page.text);self.assertNotIn('task41-public-ui-1',page.text)
 def test_preview_requires_explicit_presentation_flag(self):
  with patch.dict(os.environ,{'ADVISOR_PREMIUM_UI_PREVIEW':'false'}):
   self.assertIn('advisor-entry.js',self.client.get('/ai-career-advisor').text)
   self.assertFalse(self.client.get('/api/ai/config').json()['premium_ui_public'])
