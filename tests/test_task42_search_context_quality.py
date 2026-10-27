"""Context/relevance tests. Provider mocks are not LIVE Internet evidence."""
import asyncio
import unittest
from unittest.mock import AsyncMock,patch
from advisor.conversation_context import public_search_plan,public_search_query
from advisor import search_provider as s

GOOD={'title':'Điểm chuẩn các trường Công an nhân dân năm 2020','url':'https://example.gov.vn/diem-2020',
      'description':'Điểm chuẩn năm 2020: Học viện An ninh nhân dân, thí sinh nam tổ hợp A01: 26,50 điểm.'}
LEAP={'title':'Năm nhuận 2020 có bao nhiêu ngày?','url':'https://example.org/calendar',
      'description':'Công thức tính năm nhuận: năm 2020 có 366 ngày. Vậy bao nhiêu ngày?'}


class ContextQualityTests(unittest.TestCase):
    def setUp(self):s._cache.clear()
    def session(self):
        return {'messages':[{'role':'assistant','content':'Chào bạn','survey':{'answers':['PRIVATE_SURVEY']*5}},
            {'role':'user','content':'Điểm chuẩn các trường đại học Công an năm 2024 là bao nhiêu?'},
            {'role':'assistant','content':'Bạn muốn tìm trường hay ngành nào của khối Công an nhân dân?'}],
            'profile':{'interests':['PRIVATE_PROFILE']},'summary':'PRIVATE_SUMMARY'}

    def test_exact_elliptical_year_followup_resolves_subject_and_replaces_year(self):
        for message in ['Vậy năm 2020 là bao nhiêu ạ?','Thế năm 2020 là bao nhiêu?', 'Còn năm 2020?', 'Vậy năm 2020 điểm chuẩn bao nhiêu ạ?']:
            with self.subTest(message=message):
                plan=public_search_plan(self.session(),message)
                self.assertEqual(plan['query'],'điểm chuẩn các trường đại học Công an nhân dân năm 2020')
                self.assertTrue(plan['requires_score']);self.assertNotIn('2024',plan['query'])
                self.assertNotIn('PRIVATE',plan['query'])

    def test_successive_followups_and_bad_assistant_calendar_reply_do_not_hijack_user_topic(self):
        session=self.session();session['messages'] += [
            {'role':'user','content':'Vậy năm 2021 là bao nhiêu ạ?'},
            {'role':'assistant','content':'Năm nhuận 2020 có 366 ngày, chưa có số liệu.'}]
        query=public_search_query(session,'Vậy năm 2020 là bao nhiêu ạ?')
        self.assertIn('điểm chuẩn',query);self.assertIn('Công an',query);self.assertNotIn('nhuận',query)

    def test_explicit_calendar_or_new_subject_does_not_inherit_police(self):
        for text in ['Năm 2020 có phải năm nhuận không?', 'Tìm nguồn chính thức về ngành công nghệ thông tin.',
                     'Điểm chuẩn Đại học Bách khoa năm 2020 là bao nhiêu?']:
            self.assertEqual(public_search_query(self.session(),text),text)
        session=self.session();session['messages'].append({'role':'user','content':'Đổi chủ đề: năm nhuận có bao nhiêu ngày?'})
        self.assertTrue(public_search_plan(session,'Vậy năm 2020 là bao nhiêu ạ?')['ambiguous'])

    def test_year_only_without_known_subject_asks_instead_of_searching_calendar(self):
        state={'uid':'fixture','message':'Vậy năm 2020 là bao nhiêu ạ?','session':{'messages':[]},'web_search_allowed':True}
        with patch.object(s,'retrieve',side_effect=AssertionError('no year-only query')):
            result=asyncio.run(s.search_context(state))['retrieval']
        self.assertEqual(result['status'],'needs_clarification');self.assertEqual(result['sources'],[])
        only_career={'messages':[{'role':'assistant','content':'Chào bạn','career_context':{'career_name':'Thiết kế đồ họa'}}]}
        self.assertTrue(public_search_plan(only_career,'Vậy năm 2020 là bao nhiêu ạ?')['ambiguous'])

    def test_specific_school_survives_followup_and_other_school_source_is_rejected(self):
        session={'messages':[{'role':'user','content':'Điểm chuẩn Đại học Cảnh sát nhân dân năm 2024?'}]}
        query=public_search_query(session,'Vậy năm 2020 là bao nhiêu ạ?')
        self.assertIn('Đại học Cảnh sát nhân dân',query)
        self.assertFalse(s.relevant(query,'Điểm chuẩn Đại học An ninh nhân dân năm 2020','25,50 điểm'))
        self.assertTrue(s.relevant(query,'Điểm chuẩn Đại học Cảnh sát nhân dân năm 2020','25,50 điểm'))

    def test_school_and_public_cohort_survive_year_change_and_retry(self):
        session={'messages':[{'role':'user','content':'Điểm chuẩn Học viện An ninh nhân dân nữ miền Bắc tổ hợp D01 năm 2024?'}]}
        query=public_search_query(session,'Vậy năm 2020 là bao nhiêu ạ?')
        for expected in ['Học viện An ninh nhân dân','nữ','miền Bắc','D01','2020']:
            self.assertIn(expected,query);self.assertIn(expected,s.retry_query(query))
        self.assertNotIn('2024',query)

    def test_require_actual_subject_metric_and_year_not_filler_word_or_calendar(self):
        query=public_search_query(self.session(),'Vậy năm 2020 là bao nhiêu ạ?')
        for row in [LEAP,{'title':'Công an công bố thống kê 2020','description':'Số liệu trật tự xã hội.'},
                    {'title':'Điểm chuẩn Công an năm 2024','description':'Đợt tuyển sinh năm 2024.'},
                    {'title':'Điểm chuẩn Công an 2020','description':'Năm nhuận 2020 có 366 ngày.'}]:
            self.assertFalse(s.relevant(query,row['title'],row['description']))
        self.assertTrue(s.relevant(query,GOOD['title'],GOOD['description']))

    def test_wrong_topic_retries_once_and_only_correct_source_is_visible(self):
        provider=type('P',(),{'search':AsyncMock(side_effect=[[LEAP],[GOOD]])})()
        with patch.object(s,'provider',return_value=provider),patch.object(s,'check_link',return_value=True) as head:
            result=asyncio.run(s.retrieve('fixture','điểm chuẩn các trường đại học Công an nhân dân năm 2020'))
        self.assertEqual(provider.search.await_count,2);self.assertIn('site:bocongan.gov.vn',provider.search.call_args_list[1].args[0])
        self.assertEqual(result['attempts'],2);self.assertEqual([r['url'] for r in result['sources']],[GOOD['url']])
        head.assert_called_once_with(GOOD['url']);self.assertEqual(result['data_status'],'score_snippets_available')

    def test_second_wrong_topic_stops_without_link_checks_or_calendar_sources(self):
        provider=type('P',(),{'search':AsyncMock(return_value=[LEAP])})()
        with patch.object(s,'provider',return_value=provider),patch.object(s,'check_link',side_effect=AssertionError('bad subject')):
            result=asyncio.run(s.retrieve('fixture','điểm chuẩn Công an năm 2020'))
        self.assertEqual(provider.search.await_count,2);self.assertEqual(result['status'],'no_verified_sources');self.assertEqual(result['sources'],[])

    def test_correct_subject_without_score_does_not_invent_score_or_retry_unnecessarily(self):
        row={**GOOD,'description':'Ngày 5/10, công bố điểm chuẩn của các trường Công an năm 2020.'}
        provider=type('P',(),{'search':AsyncMock(return_value=[row])})()
        with patch.object(s,'provider',return_value=provider),patch.object(s,'check_link',return_value=True):
            result=asyncio.run(s.retrieve('fixture','điểm chuẩn Công an năm 2020'))
        self.assertEqual(provider.search.await_count,1);self.assertEqual(result['status'],'ok')
        self.assertEqual(result['data_status'],'score_data_not_in_snippets');self.assertIn('trường/ngành',result['clarification_question'])
        self.assertFalse(s.score_in_snippet('Ngày công bố 12.02.2020. Năm 2020 có thông báo mới.'))

    def test_both_attempts_share_existing_timeout_and_no_retry_after_provider_error(self):
        timeouts=[];real_timeout=asyncio.timeout
        def timeout(seconds):timeouts.append(seconds);return real_timeout(seconds)
        provider=type('P',(),{'search':AsyncMock(side_effect=s.SearchUnavailable('blocked'))})()
        with patch.object(s,'provider',return_value=provider),patch.object(s.asyncio,'timeout',side_effect=timeout):
            result=asyncio.run(s.retrieve('fixture','điểm chuẩn Công an năm 2020'))
        self.assertEqual(timeouts,[12]);self.assertEqual(provider.search.await_count,1);self.assertEqual(result['status'],'unavailable')

    def test_private_earlier_user_and_assistant_prose_never_leave_in_query(self):
        session={'messages':[{'role':'user','content':'Em tên là PRIVATE_NAME, tra điểm chuẩn Công an 2024'},
            {'role':'assistant','content':'PRIVATE_NAME dùng token PRIVATE_TOKEN. Bạn hỏi điểm chuẩn Công an nhân dân? https://internal.invalid/'}],
            'profile':{'interests':['PRIVATE_PROFILE']},'summary':'PRIVATE_SUMMARY'}
        query=public_search_query(session,'Vậy năm 2020 là bao nhiêu ạ?')
        self.assertNotIn('PRIVATE',query);self.assertNotIn('https:',query)

    def test_official_sources_sort_before_nonofficial_equivalent(self):
        provider=type('P',(),{'search':AsyncMock(return_value=[
            {**GOOD,'url':'https://example.org/2020'},
            {**GOOD,'url':'https://bocongan.gov.vn/2020'}])})()
        with patch.object(s,'provider',return_value=provider),patch.object(s,'check_link',return_value=True):
            result=asyncio.run(s.retrieve('fixture','điểm chuẩn Công an năm 2020'))
        self.assertEqual(result['sources'][0]['domain'],'bocongan.gov.vn')

    def test_no_year_followup_keeps_prior_year_and_no_data_cache_is_short(self):
        self.assertEqual(public_search_query(self.session(),'Vậy là bao nhiêu ạ?'),'điểm chuẩn các trường đại học Công an nhân dân năm 2024')
        provider=type('P',(),{'search':AsyncMock(return_value=[])})()
        with patch.object(s,'provider',return_value=provider):
            asyncio.run(s.retrieve('fixture','điểm chuẩn Công an năm 2020'))
        self.assertLess(next(iter(s._cache.values()))[0]-s.time.monotonic(),16)

    def test_retry_is_cancelled_by_single_total_deadline(self):
        calls=[];cancelled=[];real_timeout=asyncio.timeout
        async def search(query):
            calls.append(query)
            if len(calls)==1:return [LEAP]
            try:await asyncio.sleep(.2)
            except asyncio.CancelledError:cancelled.append(True);raise
        def budget(seconds):
            self.assertEqual(seconds,12)
            return real_timeout(.03)  # Exercise cancellation without a 12-second sleep.
        with patch.object(s,'provider',return_value=type('P',(),{'search':staticmethod(search)})()),patch.object(s.asyncio,'timeout',side_effect=budget):
            result=asyncio.run(s.retrieve('fixture','điểm chuẩn Công an năm 2020'))
        self.assertEqual(len(calls),2);self.assertTrue(cancelled);self.assertEqual(result['status'],'unavailable')

    def test_valid_ddgs_result_after_old_cutoff_is_not_discarded(self):
        real_timeout=asyncio.timeout
        def scaled_timeout(seconds):return real_timeout(seconds/100)
        def search(query):
            s.time.sleep(.075)  # Scale 7.5s: later than the old 7s, before the new 9s.
            return [GOOD]
        with patch.object(s.DDGSSearch,'_search',side_effect=search),patch.object(s.asyncio,'timeout',side_effect=scaled_timeout):
            rows=asyncio.run(s.DDGSSearch().search('public synthetic query'))
        self.assertEqual(rows,[GOOD])

    def test_clarification_carries_most_recent_followup_year_not_old_year(self):
        session=self.session();session['messages'] += [
            {'role':'user','content':'Vậy năm 2020 là bao nhiêu ạ?'},
            {'role':'assistant','content':'Em hỏi điểm chuẩn trường/ngành Công an nào?'}]
        plan=public_search_plan(session,'Học viện Cảnh sát nhân dân, nam, tổ hợp A01 nhé.')
        self.assertEqual(plan['query'],'điểm chuẩn Học viện Cảnh sát nhân dân nam A01 năm 2020')
        self.assertTrue(plan['follow_up']);self.assertTrue(plan['requires_score'])
        session['messages'].append({'role':'user','content':'Học viện Cảnh sát nhân dân, nam, tổ hợp A01 nhé.'})
        self.assertIn('năm 2020',public_search_query(session,'Ngành Nghiệp vụ Cảnh sát nhé.'))
        question='Giải thích an toàn thông tin là gì?'
        self.assertEqual(public_search_query(session,question),question)

    def test_official_school_abbreviation_matches_same_entity_not_other_school(self):
        self.assertTrue(s.relevant('điểm chuẩn Học viện Cảnh sát nhân dân năm 2020','Điểm chuẩn Học viện CSND 2020','Nam A01: 23,09 điểm.'))
        self.assertFalse(s.relevant('điểm chuẩn Đại học Cảnh sát nhân dân năm 2020','Điểm chuẩn Học viện CSND 2020','Nam A01: 23,09 điểm.'))
