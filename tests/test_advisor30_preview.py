import unittest
from unittest.mock import patch
from fastapi.testclient import TestClient
from app import app

class PreviewIsolationTests(unittest.TestCase):
    def test_read_only_is_server_controlled_and_blocks_all_mutations_before_provider(self):
        with patch.dict('os.environ',{'VERCEL_ENV':'preview','ADVISOR_READ_ONLY_PREVIEW':'true'}),patch('advisor.graph.post_completion',side_effect=AssertionError('must not call provider')),TestClient(app) as client:
            self.assertTrue(client.get('/api/ai/preview-info').json()['read_only'])
            for url in ['/api/advice','/api/career-stories/lap-trinh/ask','/api/ai/chat','/api/ai/guest/session','/api/ai/career-profile/items']:
                r=client.post(url,json={});self.assertEqual(r.status_code,503,url);self.assertIn('cách ly',r.text)
            self.assertEqual(client.get('/api/ai/preview-info').headers['cache-control'],'no-store')
    def test_preview_query_cannot_enable_readonly_bypass_in_production(self):
        with patch.dict('os.environ',{'VERCEL_ENV':'production','ADVISOR_READ_ONLY_PREVIEW':'true'}),TestClient(app) as client:
            self.assertFalse(client.get('/api/ai/preview-info?preview=1').json()['read_only'])
            self.assertEqual(client.post('/api/ai/chat',json={}).status_code,401)
