"""Local mock model + real isolated PG, not evidence of LIVE model quality."""
import asyncio,json,os,random,unittest
from unittest.mock import AsyncMock,patch
from uuid import uuid4
import httpx
from advisor import navigation as n,navigation_review as review
from advisor.guest_quota import get_guest_usage
from career_library import catalog,find_career
import test_advisor30_profile as base

def message(answer,actions,basis,intent='navigate',updates=None):
    return {'content':None,'tool_calls':[{'function':{'name':n.TOOL_NAME,'arguments':json.dumps(dict(answer=answer,actions=actions,basis=basis,intent=intent,profile_updates=updates or []))}}]}
def response(raw):return httpx.Response(200,json={'choices':[{'message':raw,'finish_reason':'tool_calls'}]})
def verdict(rows):return httpx.Response(200,json={'choices':[{'message':{'content':json.dumps({'decisions':rows})},'finish_reason':'stop'}]})

class ReviewTests(unittest.TestCase):
    def case(self,career=None):
        c=career or catalog().careers[22];state={'message':'Mở truyện '+c.name,'session':{'messages':[]}};answer='Bạn có thể xem một ngày làm việc của '+c.name+'.';label,href=n.destination('career_story',c.career_id);actions=[dict(kind='career_story',career_id=c.career_id,label=label,href=href)];row=dict(index=0,decision='allow',relation='requested',request_quote=state['message'],answer_quote=answer)
        return state,answer,actions,row
    def test_correct_grounding_random_catalog_and_finite_model_budget(self):
        for c in random.Random(44).sample(catalog().careers,4):
            state,answer,actions,row=self.case(c)
            with patch.object(review,'post_completion',AsyncMock(return_value=verdict([row]))) as model:
                self.assertEqual(asyncio.run(review.review_navigation(state,answer,actions)),(actions,'accepted'));payload=model.call_args.args[0];self.assertNotIn('tools',payload);self.assertEqual(payload['response_format'],{'type':'json_object'});self.assertEqual(model.await_count,1);self.assertLessEqual(model.call_args.kwargs['timeout'],8)
    def test_topic_change_and_negated_example_require_semantics_not_name_only(self):
        state,answer,actions,row=self.case();state['session']['messages']=[dict(role='user',content=state['message'])];state['message']='Đổi chủ đề, em không muốn chọn '+find_career(actions[0]['career_id']).name;row.update(decision='deny',relation='none',request_quote=state['message'])
        with patch.object(review,'post_completion',AsyncMock(return_value=verdict([row]))) as model:
            self.assertEqual(asyncio.run(review.review_navigation(state,answer,actions)),([],'rejected'));data=json.loads(model.call_args.args[0]['messages'][-1]['content']);self.assertEqual(data['current_request'],state['message']);self.assertEqual(data['recent_history'],state['session']['messages']);self.assertIn('PHỦ ĐỊNH',model.call_args.args[0]['messages'][0]['content'])
    def test_invented_request_or_answer_quote_is_rejected(self):
        state,answer,actions,row=self.case()
        for field,value in [('request_quote','Yêu cầu cũ'),('answer_quote','Nguồn giả'),('answer_quote','Bạn có thể xem một ngày')]:
            with patch.object(review,'post_completion',AsyncMock(return_value=verdict([{**row,field:value}]))):self.assertEqual(asyncio.run(review.review_navigation(state,answer,actions)),([],'rejected'))
    def test_duplicate_missing_invalid_index_or_extra_fields_fail_closed(self):
        state,answer,actions,row=self.case()
        for rows in [[],[row,row],[{**row,'index':1}],[{**row,'index':True}],[{**row,'href':'https://evil.test'}]]:
            with patch.object(review,'post_completion',AsyncMock(return_value=verdict(rows))):self.assertEqual(asyncio.run(review.review_navigation(state,answer,actions)),([],'unavailable'))
    def test_timeout_bad_json_and_truncation_omit_actions(self):
        state,answer,actions,row=self.case()
        for value in [TimeoutError(),httpx.Response(200,json={'choices':[]}),httpx.Response(200,json={'choices':[{'finish_reason':'length','message':{'content':'{}'}}]})]:
            model=AsyncMock(side_effect=value) if isinstance(value,Exception) else AsyncMock(return_value=value)
            with patch.object(review,'post_completion',model):self.assertEqual(asyncio.run(review.review_navigation(state,answer,actions)),([],'unavailable'))
    def test_no_actions_no_additional_model_call(self):
        with patch.object(review,'post_completion',AsyncMock()) as model:
            self.assertEqual(asyncio.run(review.review_navigation({'message':'Xin chào'},'Chào bạn',[])),([],'accepted'));model.assert_not_awaited()
    def test_library_requires_library_relation_not_a_guessed_substitute(self):
        state,answer,actions,row=self.case();label,href=n.destination('career_story',None);actions=[dict(kind='career_story',career_id=None,label=label,href=href)]
        for relation,expected in [('requested',[]),('library',actions)]:
            with patch.object(review,'post_completion',AsyncMock(return_value=verdict([{**row,'relation':relation}]))):self.assertEqual(asyncio.run(review.review_navigation(state,answer,actions))[0],expected)
    def test_stale_basis_not_authority_optional_decode_keeps_answer(self):
        state,answer,actions,row=self.case();state['session']['messages']=[dict(role='user',content=state['message'])];state['message']='Giờ giải thích khái niệm khác';raw=message(answer,[{k:v for k,v in actions[0].items() if k in ('kind','career_id')}],row['request_quote'])
        with self.assertRaises(n.NavigationMetadataError):n.decode_completion(raw,state)
        self.assertEqual(n.decode_completion(raw,state,strict_navigation=False),(answer,[]))

class GroundingPipelineTests(unittest.TestCase):
    setUpClass=classmethod(base.ProfileTests.setUpClass.__func__);tearDownClass=classmethod(base.ProfileTests.tearDownClass.__func__);setUp=base.ProfileTests.setUp;tearDown=base.ProfileTests.tearDown
    def send(self,raw,decision,text='Cho em xem truyện nghề',remember=False):
        if remember:
            from advisor.store import get_store
            from advisor.survey import save_survey,SurveyInput
            session=get_store().create(self.identity['uid'],True);session=save_survey(get_store(),self.identity['uid'],session['id'],SurveyInput(answers=base.ANSWERS))
        else:session=self.session
        body=dict(session_id=session['id'],request_id=str(uuid4()),message=text)
        with patch.dict(os.environ,{'AI_DEMO_MODE':'false','DEEPSEEK_API_KEY':'fixture-only','SEARCH_PROVIDER':''}),patch('advisor.graph.post_completion',AsyncMock(return_value=response(raw))) as model,patch.object(review,'post_completion',AsyncMock(return_value=decision)) as judge,patch('advisor.graph.compress_context',AsyncMock(return_value={})):
            result=self.client.post('/api/ai/chat',json=body);self.assertEqual(result.status_code,200,result.text);count=(model.await_count,judge.await_count);again=self.client.post('/api/ai/chat',json=body);self.assertEqual(again.status_code,200);self.assertTrue(again.json()['duplicate']);self.assertEqual((model.await_count,judge.await_count),count);loaded=self.client.get('/api/ai/sessions/'+session['id']).json()['session'];self.assertEqual(loaded['messages'][-1],result.json()['session']['messages'][-1])
            if self.identity['provider']=='anonymous':self.assertEqual(again.json()['guest_quota'],result.json()['guest_quota'])
            return result.json(),count
    def test_three_roles_both_stores_history_free_replay(self):
        c=catalog().careers[19];text='Cho em xem truyện nghề '+c.name;answer='Một ngày làm việc của '+c.name+'.';raw=message(answer,[dict(kind='career_story',career_id=c.career_id)],text);row=dict(index=0,decision='allow',relation='requested',request_quote=text,answer_quote=answer)
        for provider in ['anonymous','password','google.com']:
            self.identity['provider']=provider
            for remember in [False,True]:
                data,count=self.send(raw,verdict([row]),text,remember);self.assertEqual(count,(1,1));self.assertEqual(data['session']['messages'][-1]['navigation_actions'][0]['career_id'],c.career_id)
    def test_semantic_mismatch_twice_keeps_answer_proposals_no_502_one_quota(self):
        self.identity['provider']='anonymous';before=get_guest_usage(self.identity['uid'])['used_questions'];c=catalog().careers[19];text='Em thích chăm sóc thiên nhiên';answer='Đây là lời giải thích nghề '+c.name+'.';update=dict(area='interests',value=text,excerpt=text,inference_type='trực tiếp',operation='add',replaces=[]);raw=message(answer,[dict(kind='career_story',career_id=c.career_id)],text,updates=[update]);row=dict(index=0,decision='deny',relation='none',request_quote=text,answer_quote=answer)
        data,count=self.send(raw,verdict([row]),text);self.assertEqual(count,(2,2));self.assertEqual(data['session']['messages'][-1]['navigation_actions'],[]);self.assertEqual(data['session']['messages'][-1]['content'],answer);self.assertTrue(data['session']['messages'][-1]['profile_updates']);self.assertEqual(get_guest_usage(self.identity['uid'])['used_questions'],before+1)
    def test_unknown_id_twice_omits_button_not_answer_or_charge(self):
        self.identity['provider']='anonymous';before=get_guest_usage(self.identity['uid'])['used_questions'];text='Cho em xem truyện nghề';raw=message('Nghề này chưa có trong thư viện.',[dict(kind='career_story',career_id='unknown-career')],text)
        data,count=self.send(raw,verdict([]),text);self.assertEqual(count,(2,0));self.assertEqual(data['session']['messages'][-1]['navigation_actions'],[]);self.assertEqual(get_guest_usage(self.identity['uid'])['used_questions'],before+1)
    def test_information_only_skips_review_keeps_profile_controls(self):
        raw=message('Đây là khái niệm phổ thông.',[],'Giải thích khái niệm',intent='reply')
        with patch.dict(os.environ,{'ADVISOR_CONTROLLED_ROLLOUT':'true','ADVISOR_TEST_UIDS':'another-owner'}):
            data,count=self.send(raw,verdict([]),'Giải thích khái niệm');self.assertEqual(count,(1,0));self.assertEqual(data['session']['messages'][-1]['navigation_actions'],[]);self.assertFalse(self.client.get('/api/ai/config').json()['profile_enabled'])
    def test_unavailable_review_keeps_answer_without_retry_loop(self):
        c=catalog().careers[22];text='Cho em xem truyện nghề';raw=message(c.name,[dict(kind='career_story',career_id=c.career_id)],text)
        data,count=self.send(raw,httpx.Response(200,json={'choices':[]}),text);self.assertEqual(count,(1,1));self.assertEqual(data['session']['messages'][-1]['content'],c.name);self.assertEqual(data['session']['messages'][-1]['navigation_actions'],[])
    def test_semantic_retry_can_repair_once_before_atomic_save(self):
        c=catalog().careers[22];text='Mở truyện '+c.name;answer='Đây là '+c.name;raw=message(answer,[dict(kind='career_story',career_id=c.career_id)],text);deny=dict(index=0,decision='deny',relation='none',request_quote=text,answer_quote=answer);allow={**deny,'decision':'allow','relation':'requested'}
        with patch.dict(os.environ,{'AI_DEMO_MODE':'false','DEEPSEEK_API_KEY':'fixture-only','SEARCH_PROVIDER':''}),patch('advisor.graph.post_completion',AsyncMock(return_value=response(raw))) as model,patch.object(review,'post_completion',AsyncMock(side_effect=[verdict([deny]),verdict([allow])])) as judge,patch('advisor.graph.compress_context',AsyncMock(return_value={})):
            result=self.client.post('/api/ai/chat',json=dict(session_id=self.session['id'],request_id=str(uuid4()),message=text));self.assertEqual(result.status_code,200,result.text);self.assertTrue(result.json()['session']['messages'][-1]['navigation_actions']);self.assertEqual(model.await_count,2);self.assertEqual(judge.await_count,2)
