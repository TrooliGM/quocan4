"""Isolated PostgreSQL + FastAPI, fake model. No Neon or real AI calls."""
import asyncio,copy,json,os,unittest
from uuid import uuid4
from unittest.mock import patch,AsyncMock
import httpx
from fastapi import HTTPException
import test_advisor30_profile as base
from advisor import profile_proposals as p,confirmed_profile as cp
from advisor.analysis_jobs import analysis_for_session
from advisor.store import get_store
from advisor.navigation import TOOL_NAME
from career_library import catalog
from advisor.conversation_context import current_career,public_search_plan

class Task44Tests(unittest.TestCase):
    setUpClass=classmethod(base.ProfileTests.setUpClass.__func__)
    tearDownClass=classmethod(base.ProfileTests.tearDownClass.__func__)
    setUp=base.ProfileTests.setUp
    tearDown=base.ProfileTests.tearDown
    def state(self,text,rid=None):return {'session':self.session,'session_id':self.session['id'],'request_id':rid or str(uuid4()),'message':text}
    def update(self,text,area='interests',value=None,**kw):
        return {'area':area,'value':value or text,'excerpt':text,'inference_type':'trực tiếp','operation':'add','replaces':[],**kw}
    def add(self,text,updates):
        rid=str(uuid4());state=self.state(text,rid);rows=p.validate_updates(updates,state)
        self.session['messages'].extend([{'role':'user','content':text,'request_id':rid},{'role':'assistant','content':'fixture only','profile_updates':rows,'request_id':rid}])
        self.session=get_store().write(self.identity['uid'],self.session)
        return rows
    def test_additive_eight_areas_and_correction_keep_survey(self):
        rows=self.add('Em thích giúp đỡ người khác.',[self.update('Em thích giúp đỡ người khác.')]);old=rows[0]['id']
        self.add('Em thích môn Sinh và thường giúp các bạn học bài.',[self.update('Em thích môn Sinh',area='subjects'),self.update('thường giúp các bạn học bài',area='experiences')])
        a=analysis_for_session(self.session);self.assertTrue(any(x['id']==old for x in a['proposed_profile_items']));self.assertEqual(len(a['proposed_profile_items']),5)
        self.add('Em không còn thích giúp đỡ người khác.',[self.update('Em không còn thích giúp đỡ người khác.',operation='withdraw',replaces=[old])])
        a=analysis_for_session(self.session);self.assertFalse(any(x['id']==old for x in a['proposed_profile_items']));self.assertEqual(a['changes'][-1]['operation'],'withdraw')
        self.assertEqual(self.session['messages'][0]['survey']['answers'],base.ANSWERS)
        self.assertEqual(cp.read(self.identity['uid'])['items'],[])
    def test_no_assistant_web_pii_skill_inference_or_unknown_replacement(self):
        state=self.state('Em thích vẽ.')
        for row in [self.update('Em thích Sinh'),self.update('Em thích vẽ.',area='self_reported_skills',value='Vẽ giỏi'),self.update('Em thích vẽ.',operation='correct',replaces=[str(uuid4())]),self.update('Em thích vẽ.',value='a@example.com')]:self.assertEqual(p.validate_updates([row],state),[])
        self.assertEqual(p.validate_updates([self.update('Em thích vẽ.',owner='victim')],state),[])
    def test_duplicate_stable_id_reject_and_no_implicit_confirmation(self):
        text='Em thích môn Sinh';rows=self.add(text,[self.update(text,area='subjects')]);id=rows[0]['id']
        rows2=self.add(text,[self.update(text,area='subjects')]);self.assertEqual(id,rows2[0]['id'])
        a=analysis_for_session(self.session);self.assertEqual(sum(x['id']==id for x in a['proposed_profile_items']),1)
        r=self.client.post(f"/api/ai/sessions/{self.session['id']}/profile-proposals/{id}/reject");self.assertEqual(r.status_code,200)
        self.assertEqual(self.client.post('/api/ai/career-profile/items',json={'session_id':self.session['id'],'proposal_id':id,'value':text,'confirmed':True}).status_code,409)
        self.assertEqual(cp.read(self.identity['uid'])['items'],[])
    def test_confirm_correction_preserves_saved_item_and_cross_owner(self):
        text='Em thích môi trường bệnh viện';old=self.add(text,[self.update(text,area='work_preferences')])[0]
        body={'session_id':self.session['id'],'proposal_id':old['id'],'value':text,'confirmed':True}
        r=self.client.post('/api/ai/career-profile/items',json=body);self.assertEqual(r.status_code,200);item=r.json()['items'][0]
        stale=copy.deepcopy(self.session)
        text2='Em không thích làm việc trong bệnh viện';new=self.add(text2,[self.update(text2,area='work_preferences',operation='correct',replaces=[old['id']])])[0]
        self.assertEqual(cp.read(self.identity['uid'])['items'][0]['value'],text)
        r=self.client.post('/api/ai/career-profile/items',json={**body,'proposal_id':new['id'],'value':text2});self.assertEqual(r.status_code,409)
        with self.assertRaises(HTTPException):cp.confirm(self.identity['uid'],'password',stale,old['id'],text)
        self.assertEqual(self.client.patch('/api/ai/career-profile/items/'+item['id'],json={'value':text2,'version':item['version']}).status_code,200)
        self.identity={'uid':'other-person','provider':'google.com'}
        self.assertEqual(self.client.get('/api/ai/sessions/'+self.session['id']+'/analysis').status_code,404)
        self.assertEqual(self.client.put('/api/ai/sessions/'+self.session['id']+'/exploration',json={'career_id':catalog().careers[0].career_id}).status_code,404)
    def test_journey_three_careers_original_history_and_quota_unchanged(self):
        self.identity['provider']='anonymous';sid=self.session['id'];before=copy.deepcopy(self.session['messages'])
        from advisor.guest_quota import get_guest_usage
        quota=get_guest_usage(self.identity['uid'])
        for c in catalog().careers[12:15]:
            r=self.client.put('/api/ai/sessions/'+sid+'/exploration',json={'career_id':c.career_id});self.assertEqual(r.status_code,200,r.text)
            row=r.json()['session'];self.assertEqual(row['id'],sid);self.assertEqual(row['messages'][1:],before[1:]);self.assertEqual(row['messages'][0]['survey'],before[0]['survey']);self.assertEqual(current_career(row)['career_id'],c.career_id)
            self.assertIn(c.name,public_search_plan(row,'Mức lương nghề này thế nào?')['query'])
        self.assertEqual(get_guest_usage(self.identity['uid']),quota)
        self.assertEqual(self.client.put('/api/ai/sessions/'+sid+'/exploration',json={'career_id':'unknown'}).status_code,422)
        self.assertEqual(self.client.put('/api/ai/sessions/'+sid+'/exploration',json={'career_id':catalog().careers[0].career_id,'owner':'victim'}).status_code,422)
        self.assertEqual(self.client.put('/api/ai/sessions/'+sid+'/exploration',json={'career_id':catalog().careers[0].career_id},headers={'Origin':'https://evil.test'}).status_code,403)
    def test_pipeline_all_roles_single_completion_stored_metadata_retry_free(self):
        for provider in ['anonymous','password','google.com']:
            self.identity['provider']=provider;text='Em biết sử dụng máy tính';rid=str(uuid4())
            arguments={'answer':'Đây là kỹ năng em tự chia sẻ, chưa phải đánh giá năng lực.','intent':'profile_update','basis':text,'actions':[],'profile_updates':[self.update(text,area='self_reported_skills')]}
            response=httpx.Response(200,json={'choices':[{'message':{'content':None,'tool_calls':[{'function':{'name':TOOL_NAME,'arguments':json.dumps(arguments)}}]},'finish_reason':'tool_calls'}]})
            with patch.dict(os.environ,{'AI_DEMO_MODE':'false','DEEPSEEK_API_KEY':'fixture-only'}),patch('advisor.graph.post_completion',AsyncMock(return_value=response)) as mock,patch('advisor.graph.compress_context',AsyncMock(return_value={})):
                body={'session_id':self.session['id'],'request_id':rid,'message':text}
                r=self.client.post('/api/ai/chat',json=body);self.assertEqual(r.status_code,200,r.text);row=r.json()['session'];self.assertTrue(row['messages'][-1]['profile_updates'])
                again=self.client.post('/api/ai/chat',json=body);self.assertEqual(again.status_code,200);self.assertTrue(again.json()['duplicate']);self.assertEqual(mock.await_count,1)
                self.assertEqual(self.client.get('/api/ai/sessions/'+self.session['id']+'/analysis').json()['result']['analysis_version'],2)
            self.session=get_store().get(self.identity['uid'],self.session['id'])
    def test_profile_access_controls_unchanged(self):
        with patch.dict(os.environ,{'ADVISOR_CONTROLLED_ROLLOUT':'true','ADVISOR_TEST_UIDS':'qa-only'}):
            self.assertFalse(self.client.get('/api/ai/config').json()['profile_enabled'])
            text='Em thích Sinh';proposal=self.add(text,[self.update(text,area='subjects')])[0]
            self.assertEqual(self.client.post('/api/ai/career-profile/items',json={'session_id':self.session['id'],'proposal_id':proposal['id'],'value':text,'confirmed':True}).status_code,404)
            self.assertEqual(self.client.get('/api/ai/sessions/'+self.session['id']+'/analysis').status_code,200)
    def test_exact_polarity_correction_cannot_leave_both_preferences_active(self):
        old=self.add('Em thích làm việc ngoài trời',[self.update('Em thích làm việc ngoài trời',area='work_preferences',value='Muốn làm việc ngoài trời')])[0]
        rows=self.add('Em không muốn làm việc ngoài trời',[self.update('Em không muốn làm việc ngoài trời',area='work_preferences',value='Không muốn làm việc ngoài trời')])
        self.assertEqual(rows[0]['operation'],'correct');self.assertEqual(rows[0]['replaces'],[old['id']])
        result=analysis_for_session(self.session);self.assertFalse(any(p['id']==old['id'] for p in result['proposed_profile_items']))
    def test_late_survey_result_cannot_resurrect_a_denied_preference(self):
        old={'id':str(uuid4()),'category':'work_preferences','value':'Muốn làm việc ngoài trời'}
        update={'id':str(uuid4()),'category':'work_preferences','value':'Không muốn làm việc ngoài trời','operation':'add','replaces':[],'evidence':[{'excerpt':'Em không muốn làm việc ngoài trời'}]}
        session={'id':self.session['id'],'messages':[{}, {'role':'assistant','profile_updates':[update]}]}
        result=p.merge(session,{'proposed_profile_items':[old]})
        self.assertEqual([x['id'] for x in result['proposed_profile_items']],[update['id']]);self.assertEqual(result['changes'][0]['replaces'],[old['id']]);self.assertEqual(update['replaces'],[])
    def test_quote_formatting_keeps_actual_user_text_without_paraphrase(self):
        text='Thật ra em không thích làm việc ngoài trời nữa.'
        rows=p.validate_updates([self.update('Em không thích làm việc ngoài trời',area='work_preferences')],self.state(text))
        self.assertEqual(rows[0]['evidence'][0]['excerpt'],'em không thích làm việc ngoài trời')
        self.assertEqual(p.validate_updates([self.update('Em không thích ngoài trời',area='work_preferences')],self.state(text)),[])

    def test_wrong_deictic_navigation_is_retried_before_save_and_charged_once(self):
        from advisor.guest_quota import get_guest_usage
        self.identity['provider']='anonymous';sid=self.session['id'];current,wrong=catalog().careers[22:24]
        self.assertEqual(self.client.put('/api/ai/sessions/'+sid+'/exploration',json={'career_id':current.career_id}).status_code,200)
        text='Nghề này làm gì? Cho em xem một ngày làm việc của nghề đó.'
        def response(career):
            arguments={'answer':'Nội dung minh họa từ model fixture.','intent':'navigate','basis':'Cho em xem một ngày làm việc của nghề đó','actions':[{'kind':'career_story','career_id':career.career_id}],'profile_updates':[]}
            return httpx.Response(200,json={'choices':[{'message':{'content':None,'tool_calls':[{'function':{'name':TOOL_NAME,'arguments':json.dumps(arguments)}}]},'finish_reason':'tool_calls'}]})
        before=get_guest_usage(self.identity['uid'])['used_questions']
        with patch.dict(os.environ,{'AI_DEMO_MODE':'false','DEEPSEEK_API_KEY':'fixture-only'}),patch('advisor.graph.post_completion',AsyncMock(side_effect=[response(wrong),response(current)])) as model:
            r=self.client.post('/api/ai/chat',json={'session_id':sid,'request_id':str(uuid4()),'message':text});self.assertEqual(r.status_code,200,r.text)
            self.assertEqual(model.await_count,2);self.assertEqual(r.json()['session']['messages'][-1]['navigation_actions'][0]['career_id'],current.career_id)
        self.assertEqual(get_guest_usage(self.identity['uid'])['used_questions'],before+1)
