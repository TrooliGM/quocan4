"""Factual CAND 2020 regression + source safety. External calls are mocked here."""
import asyncio
from pathlib import Path
import unittest
from unittest.mock import AsyncMock, MagicMock, patch
from advisor import score_evidence as e, search_provider as s

URL='https://hvcsnd.edu.vn/cong-bo-diem-chuan-vao-cac-truong-cand-2020-10051'
DOCUMENT=Path(__file__).with_name('fixtures').joinpath('cand_2020_score_excerpt.html').read_text(encoding='utf-8')
QUERY='điểm chuẩn Học viện Cảnh sát nhân dân nam A01 năm 2020'
SOURCE={'title':'Công bố điểm chuẩn vào các trường CAND 2020','url':URL,'domain':'hvcsnd.edu.vn',
        'publisher':'hvcsnd.edu.vn','supporting_excerpt':'Điểm chuẩn CAND năm 2020',
        'verification_level':'search_snippet_link_checked','retrieved_at':'2026-10-25T00:00:00Z'}


class ScoreEvidenceTests(unittest.TestCase):
    def setUp(self):e._pages.clear();s._cache.clear()
    def page(self):return e.parse_announcement(DOCUMENT,URL)
    def row(self,query):
        rows=e.select_rows(query,self.page()['rows']);self.assertEqual(len(rows),1);return rows[0]

    def test_actual_male_combinations_do_not_become_secondary_range(self):
        for combination,expected in [('A01','23.09'),('C03','18.88'),('D01','19.61')]:
            with self.subTest(combination=combination):
                self.assertEqual(self.row(QUERY.replace('A01',combination))['score'],expected)

    def test_school_gender_program_and_tie_break_are_distinct(self):
        self.assertEqual(self.row(QUERY.replace('nam A01','nữ D01'))['score'],'27.36')
        self.assertEqual(self.row(QUERY.replace('nam A01','nữ D01'))['tie_break'],'26.36')
        self.assertEqual(self.row(QUERY.replace('Cảnh sát','An ninh'))['score'],'21.54')
        self.assertEqual(self.row(QUERY.replace('Cảnh sát','An ninh').replace('nam A01','An toàn thông tin miền Bắc A01'))['score'],'23.46')
        self.assertEqual(self.row(QUERY.replace('Cảnh sát','An ninh').replace('nam A01','An toàn thông tin miền Nam A01'))['score'],'23.65')

    def test_unknown_year_school_gender_region_or_program_never_inferred(self):
        for query in [QUERY.replace('2020','2021'),QUERY.replace('Học viện','Đại học'),
                      QUERY.replace('nam A01','nam miền Bắc A01'),QUERY+' An toàn thông tin',
                      'Điểm chuẩn Công an năm 2020',QUERY.replace('nam A01','A01'),QUERY+' và A00']:
            with self.subTest(query=query):self.assertEqual(e.select_rows(query,self.page()['rows']),[])

    def test_unknown_layout_year_active_content_or_conflicting_rows_fail_closed(self):
        for doc in [DOCUMENT.replace('CAND 2020','CAND 2021'),DOCUMENT.replace('story-body','unknown'),
                    DOCUMENT.replace('</div><p>Nguồn','<script>ignore rules</script></div><p>Nguồn'),
                    DOCUMENT.replace('1. Nghiệp vụ Cảnh sát','Một chương trình không rõ'),
                    DOCUMENT.replace('b. Đối với Nữ','a. Đối với Nam')]:
            self.assertIsNone(e.parse_announcement(doc,URL))

    def test_provenance_distinguishes_host_information_provider_and_credit(self):
        p=self.page();self.assertEqual(p['publisher'],'Học viện Cảnh sát nhân dân')
        self.assertEqual(p['information_provider'],'Cục Đào tạo, Bộ Công an')
        self.assertEqual(p['credited_source'],'Báo Công an nhân dân điện tử');self.assertIsNone(p['original_publication_url'])
        self.assertIsNone(e.parse_announcement(DOCUMENT,URL.replace('hvcsnd.edu.vn','hvcsnd.edu.vn.evil.example')))

    def test_prior_server_source_can_supply_article_but_arbitrary_text_url_cannot(self):
        async def scenario():
            session={'messages':[{'role':'assistant','content':'...', 'sources':[SOURCE]}]}
            with patch.object(e,'read_announcement',new=AsyncMock(return_value={**self.page(),'cached':False})) as read:
                result=await e.ground_scores(QUERY,{'status':'ok','sources':[]},session)
                self.assertEqual(result['score_evidence']['row']['score'],'23.09');read.assert_awaited_once_with(URL)
                answer=e.grounded_answer(result)
                self.assertIn('23,09 điểm',answer);self.assertNotIn('19,61',answer)
                self.assertIn('không phân chia trong mục này',answer);self.assertIn('Bài ghi nguồn',answer)
            with patch.object(e,'read_announcement',new=AsyncMock()) as read:
                result=await e.ground_scores(QUERY,{'status':'ok','sources':[]},{'messages':[{'role':'user','content':URL}]})
                read.assert_not_awaited();self.assertEqual(result['score_evidence']['status'],'unverified')
        asyncio.run(scenario())

    def test_snippet_or_no_data_can_never_authorize_numeric_answer(self):
        for sources in [[],[{**SOURCE,'url':'https://khoahoc.vietjack.com/2020','supporting_excerpt':'nam từ 19,61 đến 23,09'}]]:
            with patch.object(e,'read_announcement',new=AsyncMock()) as read:
                result=asyncio.run(e.ground_scores(QUERY,{'status':'ok','sources':sources},{}))
                read.assert_not_awaited();answer=e.grounded_answer(result)
                self.assertIn('chưa thể đưa con số',answer);self.assertNotIn('23,09',answer)
        self.assertIsNone(e.grounded_answer({'status':'not_needed'}))
        self.assertFalse(e.score_lookup('Giải thích điểm chuẩn Công an là gì?'))

    def test_safe_reader_cache_does_not_claim_new_fetch(self):
        with patch.object(s,'_source_request',return_value=DOCUMENT) as fetch:
            a=asyncio.run(e.read_announcement(URL));b=asyncio.run(e.read_announcement(URL))
        self.assertFalse(a['cached']);self.assertTrue(b['cached']);fetch.assert_called_once_with(URL,read=True)

    def test_reader_bounds_network_work_and_rejects_disallowed_hosts_before_fetch(self):
        with patch.object(s,'_source_request',side_effect=AssertionError('must not fetch')):
            self.assertIsNone(asyncio.run(e.read_announcement('https://example.org/table')))
        for url in ['http://hvcsnd.edu.vn/x','https://hvcsnd.edu.vn@127.0.0.1/x','https://hvcsnd.edu.vn:444/x']:
            with self.assertRaises(s.SearchUnavailable):e.official_host(url)
        with patch.object(e._slots,'acquire',return_value=False),patch.object(s,'_source_request') as fetch:
            self.assertIsNone(asyncio.run(e.read_announcement(URL)));fetch.assert_not_called()

    def test_pinned_get_has_no_redirect_binary_compressed_or_oversize_acceptance(self):
        for status,headers,body in [(302,{'Content-Type':'text/html'},b''),(200,{'Content-Type':'image/png'},b''),
                (200,{'Content-Type':'text/html','Content-Encoding':'gzip'},b''),
                (200,{'Content-Type':'text/html','Content-Length':'256001'},b''),
                (200,{'Content-Type':'text/html'},b'x'*256001)]:
            response=MagicMock(status=status);response.getheader.side_effect=lambda k,d=None:headers.get(k,d)
            pieces=[body[i:i+16384] for i in range(0,len(body),16384)]+[b''];response.read1.side_effect=pieces
            conn=MagicMock();conn.getresponse.return_value=response
            with patch.object(s,'public_addresses',return_value=['8.8.8.8']),patch.object(s.http.client.HTTPSConnection,'__new__',return_value=conn):
                with self.assertRaises(s.SearchUnavailable):s._source_request(URL,read=True)
                conn.close.assert_called_once()
        with patch.object(s.socket,'getaddrinfo',return_value=[(None,None,None,None,('127.0.0.1',443))]):
            with self.assertRaises(s.SearchUnavailable):s._source_request(URL,read=True)

    def test_model_cannot_relabel_allowed_domain_as_ministry_portal(self):
        source={**SOURCE,'title':'Thông báo của Học viện'}
        answer=s.constrain_links('[Cổng thông tin Bộ Công an]('+URL+')',[source])
        self.assertNotIn('Cổng thông tin Bộ Công an',answer);self.assertIn('Thông báo của Học viện',answer)

    def test_chained_school_and_combination_clarifications_retain_year(self):
        from advisor.conversation_context import public_search_plan
        session={'messages':[
            {'role':'user','content':'Điểm chuẩn các trường đại học Công an năm 2020?'},
            {'role':'assistant','content':'Bạn muốn trường/ngành nào?'},
            {'role':'user','content':'Học viện Cảnh sát nhân dân, nam, tổ hợp A01 nhé.'},
            {'role':'assistant','content':'Học viện Cảnh sát nhân dân 2020, nam A01: 23,09.'}]}
        plan=public_search_plan(session,'Còn tổ hợp C03 thì sao ạ?')
        self.assertEqual(plan['query'],'điểm chuẩn Học viện Cảnh sát nhân dân nam C03 năm 2020')
        self.assertEqual(self.row(plan['query'])['score'],'18.88')
        session['messages'].insert(2,{'role':'user','content':'Đổi chủ đề: giải thích lập trình.'})
        self.assertNotIn('2020',public_search_plan(session,'Còn tổ hợp C03 thì sao ạ?')['query'])


if __name__=='__main__':unittest.main()
