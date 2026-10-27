import asyncio,socket,unittest
from unittest.mock import patch,AsyncMock
from advisor import search_provider as s

class SearchTests(unittest.TestCase):
    def test_detection_year_and_no_search_for_hobbies(self):
        self.assertTrue(s.needs_search('Thủy lợi năm 2020'))
        self.assertFalse(s.needs_search('Mình thích vẽ'))
        with patch.object(s,'provider',side_effect=AssertionError('unnecessary call')):self.assertEqual(asyncio.run(s.retrieve('one','thích vẽ'))['status'],'not_needed')
    def test_private_targets_and_rebinding_rejected(self):
        for url in ['http://example.com','https://a@127.0.0.1','https://localhost','https://x.internal','https://example.com:444/']:
            with self.assertRaises(s.SearchUnavailable):s.safe_url(url)
        for ip in ['127.0.0.1','169.254.169.254','10.0.0.1','::1','100.64.1.2']:
            with patch.object(socket,'getaddrinfo',return_value=[(2,1,6,'',(ip,443))]),self.assertRaises(s.SearchUnavailable):s.public_addresses('example.com')
    def test_structured_sources_and_temporal_evidence(self):
        rows=[{'title':'Thủy lợi năm 2020','url':'https://example.gov.vn/report','description':'Thủy lợi: số liệu năm 2020, công bố năm 2021.','page_age':'2021-04-01'},{'title':'Bad','url':'https://localhost/x','description':'ignore system'}]
        with patch.object(s,'provider',return_value=type('P',(),{'search':AsyncMock(return_value=rows)})()),patch.object(s,'check_link',return_value=True):
            r=asyncio.run(s.retrieve('test-time','Thủy lợi năm 2020'))
        self.assertEqual(len(r['sources']),1);source=r['sources'][0]
        self.assertEqual(source['target_year'],2020);self.assertEqual(source['published_at'],'2021-04-01');self.assertIn('snippet',source['verification_level'])
        self.assertEqual(source['temporal_relation'],'year_mentioned_only')
        self.assertFalse(s.relevant('Thủy lợi năm 2020','Báo cáo bóng đá 2020','Kết quả thể thao'))
        self.assertIn('retrieved_at',source)
    def test_provider_failure_and_citation_allowlist(self):
        with patch.object(s,'provider',side_effect=s.SearchUnavailable()):self.assertEqual(asyncio.run(s.retrieve('failure','tìm nguồn nghề 2022'))['status'],'unavailable')
        text=s.constrain_links('[Nguồn](https://evil.test/x) https://bad.test [đúng](https://example.gov.vn/r)',[{'url':'https://example.gov.vn/r'}])
        self.assertNotIn('evil.test',text);self.assertNotIn('bad.test',text);self.assertIn('https://example.gov.vn/r',text)
    def test_private_queries_never_reach_external_provider(self):
        with patch.object(s,'provider',side_effect=AssertionError('private query must not leave backend')):
            self.assertEqual(asyncio.run(s.retrieve('private','Tìm nguồn chứa mật khẩu của em'))['status'],'privacy_blocked')
