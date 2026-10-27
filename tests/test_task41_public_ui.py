"""Unified chat/draft analysis must not grant experimental confirmed-profile rights."""
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
 def assert_public_ui_with_separate_data_rights(self):
  page=self.client.get('/ai-career-advisor')
  self.assertEqual(page.status_code,200);self.assertIn('Trợ lý hướng nghiệp',page.text)
  self.assertIn('Đồng hành cùng bạn khám phá nghề nghiệp',page.text)
  self.assertNotIn('advisor-entry.js',page.text);self.assertIn('task41-unified-1',page.text)
  self.assertEqual(page.headers['cache-control'],'no-store')
  config=self.client.get('/api/ai/config').json()
  self.assertTrue(config['premium_ui_public'])
  self.assertTrue(config['task4_enabled']);self.assertTrue(config['automatic_analysis']);self.assertFalse(config['profile_enabled'])
  self.assertEqual(config['chat_pipeline'],'task41')
  # The legacy GET returns this owner's conversation notes, not confirmed items.
  legacy=self.client.get('/api/ai/career-profile');self.assertEqual(legacy.status_code,200);self.assertNotIn('items',legacy.json())
  self.assertEqual(self.client.get('/api/ai/task4-shell').status_code,404)
  self.assertEqual(self.client.get('/api/ai/sessions/'+self.sid+'/analysis').status_code,200)
  self.assertEqual(self.client.post('/api/ai/sessions/'+self.sid+'/analysis',json={}).json()['status'],'completed')
  self.assertEqual(self.client.post('/api/ai/career-profile/items',json=self.f.body()).status_code,404)
 def test_guest_has_owned_analysis_without_private_profile_access(self):
  self.f.identity['provider']='anonymous';self.assert_public_ui_with_separate_data_rights()
  self.assertEqual(self.client.get('/api/ai/config').json()['guest_quota']['remaining'],8)
 def test_member_uses_new_ai_graph_without_profile_privilege(self):
  self.assert_public_ui_with_separate_data_rights()
  with patch('advisor.stable_graph.advisor_graph.ainvoke',side_effect=AssertionError('Legacy graph must never run')):
   r=self.client.post('/api/ai/chat',json={'session_id':self.sid,'request_id':str(uuid4()),'message':'Em thích vẽ'})
  self.assertEqual(r.status_code,200);self.assertEqual(r.json()['pipeline'],'task41')
 def test_verified_qa_retains_analysis_and_profile_access(self):
  with patch.dict(os.environ,{'ADVISOR_TEST_UIDS':'owner-one'}):
   config=self.client.get('/api/ai/config').json()
   self.assertTrue(config['premium_ui_public']);self.assertTrue(config['automatic_analysis']);self.assertTrue(config['profile_enabled'])
   self.assertEqual(self.client.get('/api/ai/career-profile').status_code,200)
   self.assertEqual(self.client.post('/api/ai/sessions/'+self.sid+'/analysis',json={}).json()['status'],'completed')
 def test_candidate_ui_is_unified_without_granting_profile_rights(self):
  with patch.dict(os.environ,{'VERCEL_ENV':'production'}):
   self.assertTrue(self.client.get('/api/ai/config').json()['premium_ui_public'])
   page=self.client.get('/ai-career-advisor?preview=1')
   self.assertNotIn('advisor-entry.js',page.text);self.assertIn('task41-unified',page.text)
 def test_old_presentation_flag_cannot_restore_legacy_chat(self):
  with patch.dict(os.environ,{'ADVISOR_PREMIUM_UI_PREVIEW':'false'}):
   self.assertNotIn('advisor-entry.js',self.client.get('/ai-career-advisor').text)
   self.assertEqual(self.client.get('/api/ai/config').json()['chat_pipeline'],'task41')
