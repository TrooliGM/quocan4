"""FastAPI + PostgreSQL riêng trên localhost; không Neon, không AI/Firebase thật."""
import copy,json,os,unittest,asyncio
from concurrent.futures import ThreadPoolExecutor
from uuid import uuid4
from unittest.mock import patch,AsyncMock
import httpx
import test_advisor30_profile as base
from advisor.store import get_store
from advisor import confirmed_profile as cp
from advisor.graph import load_profile,generate_response
from advisor.survey_analysis import validate_analysis,AnalysisValidationError
from advisor.navigation import TOOL_NAME,tool
from advisor.profile_context import profile_message


class RemovalTests(unittest.TestCase):
    setUpClass=classmethod(base.ProfileTests.setUpClass.__func__)
    tearDownClass=classmethod(base.ProfileTests.tearDownClass.__func__)
    setUp=base.ProfileTests.setUp
    tearDown=base.ProfileTests.tearDown

    def test_retired_api_all_roles_never_reads_or_writes_even_with_old_flags(self):
        paths=[('get','/api/ai/career-profile'),('post','/api/ai/career-profile/items'),('patch','/api/ai/career-profile/items/'+str(uuid4())),('delete','/api/ai/career-profile/items/'+str(uuid4())),('put','/api/ai/sessions/'+self.session['id']+'/profile-use'),('post','/api/ai/sessions/'+self.session['id']+'/profile-proposals/'+str(uuid4())+'/reject')]
        with patch('advisor.confirmed_profile.confirm',side_effect=AssertionError('must not write')),patch('advisor.confirmed_profile.read',side_effect=AssertionError('must not read')):
            for provider in ('anonymous','password','google.com'):
                self.identity['provider']=provider
                self.assertFalse(self.client.get('/api/ai/config').json()['profile_enabled'])
                for method,path in paths:self.assertEqual(self.client.request(method,path,json={'uid':'victim'}).status_code,410)

    def test_member_retain_independent_of_profile_flag_same_id_and_survey(self):
        sid=self.session['id'];before=copy.deepcopy(self.session)
        with patch.dict(os.environ,{'ADVISOR_PROFILE_ENABLED':'false'}),ThreadPoolExecutor(max_workers=2) as pool:
            responses=list(pool.map(lambda _:self.client.post('/api/ai/sessions/'+sid+'/retain'),range(2)))
        self.assertEqual([r.status_code for r in responses],[200,200])
        row=get_store().get(self.identity['uid'],sid);self.assertTrue(row['remember']);self.assertEqual(row['id'],sid);self.assertEqual(row['messages'],before['messages'])
        with self.connection() as db:
            self.assertEqual(db.execute('SELECT count(*) AS n FROM advisor_sessions WHERE id=%s',(sid,)).fetchone()['n'],1)
            self.assertEqual(db.execute('SELECT count(*) AS n FROM advisor_temporary_sessions WHERE id=%s',(sid,)).fetchone()['n'],0)

    def test_retain_and_delete_work_without_profile_migration_006(self):
        from advisor import postgres_store as pg
        connection=self.cluster.schema()
        with patch.object(pg,'postgres_connection',connection):
            sid=get_store().create('owner-one',False)['id']
            self.assertEqual(self.client.post('/api/ai/sessions/'+sid+'/retain').status_code,200)
            self.assertEqual(self.client.delete('/api/ai/data').status_code,204)
            self.assertEqual(self.client.get('/api/ai/sessions/'+sid).status_code,404)
            with connection() as db:self.assertIsNone(db.execute("SELECT to_regclass('advisor_profile_items') AS name").fetchone()['name'])

    def test_guest_cannot_retain_or_create_persistent_session(self):
        self.identity['provider']='anonymous';before=self.client.get('/api/ai/config').json()['guest_quota']
        self.assertEqual(self.client.post('/api/ai/sessions/'+self.session['id']+'/retain').status_code,403)
        self.assertEqual(self.client.post('/api/ai/sessions',json={'remember':True}).status_code,403)
        self.assertEqual(self.client.get('/api/ai/config').json()['guest_quota'],before)

    def test_foreign_session_and_origin_blocked_for_retain_and_delete(self):
        sid=self.session['id'];self.identity['uid']='other-owner'
        self.assertEqual(self.client.post('/api/ai/sessions/'+sid+'/retain',headers={'X-User-Id':'owner-one'}).status_code,404)
        self.identity['uid']='owner-one'
        for method,path in [('POST','/api/ai/sessions/'+sid+'/retain'),('DELETE','/api/ai/data')]:self.assertEqual(self.client.request(method,path,headers={'Origin':'https://evil.invalid'}).status_code,403)
        self.assertEqual(get_store().get('owner-one',sid)['id'],sid)

    def test_explicit_delete_cleans_only_owner_including_old_profile_when_flag_off(self):
        proposal=self.analysis['proposed_profile_items'][0]
        cp.confirm('owner-one','password',self.session,proposal['id'],proposal['value'])
        other=get_store().create('other-owner',True)
        with patch.dict(os.environ,{'ADVISOR_PROFILE_ENABLED':'false'}):self.assertEqual(self.client.delete('/api/ai/data?uid=other-owner').status_code,204)
        self.assertEqual(get_store().get('other-owner',other['id'])['id'],other['id'])
        self.assertEqual(self.client.get('/api/ai/sessions/'+self.session['id']).status_code,404)
        with self.connection() as db:self.assertEqual(db.execute('SELECT count(*) AS n FROM advisor_profile_items WHERE owner=%s',('owner-one',)).fetchone()['n'],0)

    def test_account_writes_still_rate_limited_no_untrusted_proxy_bypass(self):
        with patch.dict(os.environ,{'PROFILE_USER_WRITES_PER_MINUTE':'1','AI_TRUSTED_PROXY_CIDRS':''}):
            self.assertEqual(self.client.post('/api/ai/sessions/'+self.session['id']+'/retain').status_code,200)
            self.assertEqual(self.client.post('/api/ai/sessions/'+self.session['id']+'/retain',headers={'X-Forwarded-For':'203.0.113.9'}).status_code,429)

    def test_confirmed_profile_not_loaded_but_session_context_is_preserved(self):
        self.session['messages'][0]['use_confirmed_profile']=True;get_store().write('owner-one',self.session)
        with patch('advisor.confirmed_profile.context_items',side_effect=AssertionError('private profile must not load')):
            state=load_profile({'uid':'owner-one','session_id':self.session['id'],'confirmed_profile_access':True})
        self.assertEqual(state['confirmed_profile'],[]);self.assertEqual(state['session']['messages'][0]['survey']['answers'],base.ANSWERS)
        self.assertNotIn('PRIVATE_SENTINEL',profile_message(self.session,[{'category':'interests','value':'PRIVATE_SENTINEL'}],True)['content'])

    def test_pipeline_ignores_legacy_profile_updates_keeps_navigation_and_one_charge(self):
        for provider in ('anonymous','password','google.com'):
            self.identity['provider']=provider;rid=str(uuid4());text='Mở truyện nghề lập trình viên'
            args={'answer':'Cùng khám phá công việc lập trình viên nhé.','intent':'navigate','basis':text,'actions':[{'kind':'career_story','career_id':'lap-trinh'}],'profile_updates':[{'value':'do not save'}]}
            response=httpx.Response(200,json={'choices':[{'finish_reason':'tool_calls','message':{'content':None,'tool_calls':[{'function':{'name':TOOL_NAME,'arguments':json.dumps(args)}}]}}]})
            async def review(state,answer,actions):return actions,'accepted'
            with patch.dict(os.environ,{'AI_DEMO_MODE':'false','DEEPSEEK_API_KEY':'fixture-only'}),patch('advisor.graph.post_completion',AsyncMock(return_value=response)) as model,patch('advisor.graph.compress_context',AsyncMock(return_value={})),patch('advisor.navigation_review.review_navigation',review):
                body={'session_id':self.session['id'],'request_id':rid,'message':text}
                r=self.client.post('/api/ai/chat',json=body);self.assertEqual(r.status_code,200,r.text);msg=r.json()['session']['messages'][-1]
                self.assertEqual(msg['profile_updates'],[]);self.assertEqual(msg['navigation_actions'][0]['career_id'],'lap-trinh')
                self.assertTrue(self.client.post('/api/ai/chat',json=body).json()['duplicate']);self.assertEqual(model.await_count,1)
        self.assertEqual(tool()['function']['parameters']['properties']['profile_updates']['maxItems'],0)

    def test_direction_grounding_and_legacy_analysis_compatibility(self):
        survey=self.session['messages'][0]['survey'];raw=copy.deepcopy(base.RAW)
        raw['career_directions']=[{'career_id':id,'reason':'Một hướng đáng thử vì sở thích đã chia sẻ, chưa phải kết luận phù hợp.','evidence':[{'question_id':1,'excerpt':'Tin học và vẽ'}],'subjects':['Tin học'],'skills':['Giải quyết vấn đề'],'activities':['Thử mô phỏng dự án nhỏ trên giấy']} for id in ('lap-trinh','thiet-ke','bac-si')]
        result=validate_analysis(raw,survey,self.session['id']);self.assertEqual(len(result['career_directions']),3)
        self.assertEqual(validate_analysis(base.RAW,survey,self.session['id'])['career_directions'],[])
        raw['career_directions'][0]['evidence'][0]['excerpt']='Thông tin chưa từng chia sẻ'
        with self.assertRaises(AnalysisValidationError):validate_analysis(raw,survey,self.session['id'])

if __name__=='__main__':unittest.main()
