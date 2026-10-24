import os,unittest
from unittest.mock import patch
from fastapi.testclient import TestClient
from app import app
from advisor.routes import require_user
from advisor.rollout import allowed

class RolloutTests(unittest.TestCase):
    def test_fail_closed_and_uid_cannot_be_forged(self):
        with patch.dict(os.environ,{'VERCEL_ENV':'production','ADVISOR_TEST_UIDS':'qa-only','ADVISOR_CONTROLLED_ROLLOUT':'true'}):
            self.assertTrue(allowed({'uid':'qa-only','provider':'password'}))
            self.assertFalse(allowed({'uid':'qa-only','provider':'anonymous'}))
            self.assertFalse(allowed({'uid':'other','provider':'google.com'}))
            app.dependency_overrides[require_user]=lambda:{'uid':'other','provider':'password'}
            try:
                with TestClient(app) as c:
                    self.assertEqual(c.get('/api/ai/task4-shell?uid=qa-only',headers={'X-User-Id':'qa-only'}).status_code,404)
                    self.assertEqual(c.post('/api/ai/career-profile/items',json={}).status_code,404)
                    self.assertIn('advisor-entry.js',c.get('/ai-career-advisor').text)
                    self.assertIn('stable-chat.css',c.get('/ai-career-advisor').text)
            finally:app.dependency_overrides.pop(require_user,None)
    def test_allowlisted_shell_only(self):
        with patch.dict(os.environ,{'ADVISOR_CONTROLLED_ROLLOUT':'true','ADVISOR_TEST_UIDS':'qa-only'}):
            app.dependency_overrides[require_user]=lambda:{'uid':'qa-only','provider':'google.com'}
            try:
                with TestClient(app) as c:self.assertIn('Trợ lý hướng nghiệp',c.get('/api/ai/task4-shell').text)
            finally:app.dependency_overrides.pop(require_user,None)
