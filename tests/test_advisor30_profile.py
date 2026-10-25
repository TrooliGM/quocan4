"""PostgreSQL local thật + LLM stub có nhãn; KHÔNG kết nối Neon/Firebase/AI thật."""
import asyncio,copy,json,os,unittest
from pathlib import Path
from unittest.mock import patch,AsyncMock
from concurrent.futures import ThreadPoolExecutor
from uuid import uuid4
from fastapi.testclient import TestClient
from app import app
from advisor.routes import require_user
from advisor.store import get_store
from advisor import postgres_store as pg,confirmed_profile as cp
from advisor.survey import SurveyInput,save_survey
from advisor.survey_analysis import validate_analysis,analyze_survey
from advisor.graph import load_profile
from advisor.guest_quota import claim_guest_history
from postgres_fixture import LocalPostgres

ANSWERS=['Em thích Tin học và vẽ','Em vẽ tranh trên máy tính','Em tự nhận kiên nhẫn','Em muốn môi trường sáng tạo','Em muốn tìm hiểu nghề thiết kế']
RAW={'summary':'Sở thích Tin học và vẽ gắn với mong muốn sáng tạo; kiên nhẫn là điểm mạnh tự nhận, chưa đánh giá được kỹ năng thiết kế.',
     'proposed_profile_items':[{'category':'interests','value':'Tin học và vẽ','evidence':[{'question_id':1,'excerpt':'Tin học và vẽ'}],'confidence':'rõ ràng','inference_type':'diễn giải','proposed_action':'confirm'},
     {'category':'strengths','value':'Kiên nhẫn (tự nhận)','evidence':[{'question_id':3,'excerpt':'tự nhận kiên nhẫn'}],'confidence':'cần xác nhận','inference_type':'trực tiếp','proposed_action':'confirm'}],
     'clarification_questions':['Bạn muốn thử vẽ minh họa hay thiết kế giao diện trước?']}

class AnalysisTests(unittest.TestCase):
    def survey(self):return {'answers':ANSWERS,'analysis_request_id':str(uuid4())}
    def test_all_questions_grounding_and_distinct_categories(self):
        result=validate_analysis(RAW,self.survey(),'s1');self.assertEqual(result['interests'],['Tin học và vẽ']);self.assertIn('tự nhận',result['strengths'][0])
        self.assertEqual(result['proposed_profile_items'][0]['evidence_question_ids'],[1]);self.assertNotIn('\n'.join(ANSWERS),result['summary'])
    def test_short_uncertain_and_contradictory_survey(self):
        survey=self.survey();survey['answers']=['Chưa rõ','Chưa rõ','Chưa biết','Thích ở nhà nhưng muốn đi nhiều nơi','Cần làm rõ']
        raw=copy.deepcopy(RAW);raw['proposed_profile_items']=[{'category':'uncertainties','value':'Cần làm rõ môi trường mong muốn','evidence':[{'question_id':4,'excerpt':survey['answers'][3]}],'confidence':'chưa đủ dữ liệu','inference_type':'diễn giải','proposed_action':'clarify'}]
        self.assertEqual(validate_analysis(raw,survey,'s')['proposed_profile_items'][0]['proposed_action'],'clarify')
        bad=copy.deepcopy(RAW);bad['proposed_profile_items'][1]['evidence']=[{'question_id':3,'excerpt':'Chưa biết'}]
        with self.assertRaises(ValueError):validate_analysis(bad,survey,'s')
    def test_cannot_invent_evidence_or_strength_from_interest(self):
        for changes in [{'evidence':[{'question_id':1,'excerpt':'giỏi lập trình'}]},{'category':'strengths'},{'category':'careers','inference_type':'suy luận'}]:
            raw=copy.deepcopy(RAW);raw['proposed_profile_items'][0].update(changes)
            with self.assertRaises(ValueError):validate_analysis(raw,self.survey(),'s')
    def test_invalid_model_analysis_does_not_change_survey_or_call_on_modal(self):
        survey=self.survey();state={'session_id':'s','message':'analyze','session':{'messages':[{'role':'assistant','content':'hi','survey':survey}]}}
        before=copy.deepcopy(state)
        import httpx
        response=httpx.Response(200,json={'choices':[{'message':{'content':'invalid json'},'finish_reason':'stop'}]})
        with patch.dict(os.environ,{'AI_DEMO_MODE':'false'}),patch('advisor.graph.post_completion',AsyncMock(return_value=response)):
            self.assertEqual(asyncio.run(analyze_survey(state)),{'analysis_status':'unavailable'})
        self.assertEqual(state,before)

class ProfileTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):cls.cluster=LocalPostgres().__enter__()
    @classmethod
    def tearDownClass(cls):cls.cluster.__exit__(None,None,None)
    def setUp(self):
        self.connection=self.cluster.schema()
        self.patches=[patch.dict(os.environ,{'DATABASE_URL':self.cluster.url,'ADVISOR_PROFILE_ENABLED':'true'}),patch.object(pg,'postgres_connection',self.connection)]
        for p in self.patches:p.start()
        with self.connection() as db:
            db.execute("SET laban.profile_migration_target='task4-staging-approved'")
            db.execute((Path(__file__).resolve().parents[1]/'migrations/006_confirmed_career_profile.sql').read_text(encoding='utf8'))
        self.identity={'uid':'owner-one','provider':'password'}
        app.dependency_overrides[require_user]=lambda:self.identity
        self.client=TestClient(app,client=('127.0.0.1',41011));self.client.__enter__()
        self.session=get_store().create(self.identity['uid'],False)
        self.session=save_survey(get_store(),self.identity['uid'],self.session['id'],SurveyInput(answers=ANSWERS))
        survey=self.session['messages'][0]['survey'];self.analysis=validate_analysis(RAW,survey,self.session['id'])
        self.session['messages'].append({'role':'assistant','content':'analysis','survey_analysis':self.analysis})
        self.session=get_store().write(self.identity['uid'],self.session)
    def tearDown(self):
        self.client.__exit__(None,None,None);app.dependency_overrides.pop(require_user,None)
        for p in reversed(self.patches):p.stop()
    def body(self):return {'session_id':self.session['id'],'proposal_id':self.analysis['proposed_profile_items'][0]['id'],'value':'Vẽ và Tin học (mình xác nhận)','confirmed':True}
    def accept(self):
        response=self.client.post('/api/ai/career-profile/items',json=self.body());self.assertEqual(response.status_code,200,response.text);return response.json()['items'][0]
    def test_survey_does_not_implicitly_save_and_only_one_accepted(self):
        self.assertEqual(self.client.get('/api/ai/career-profile').json()['items'],[])
        item=self.accept();self.assertEqual(item['value'],self.body()['value']);self.assertTrue(item['metadata']['edited_by_user'])
        self.assertEqual(len(self.client.get('/api/ai/career-profile').json()['items']),1)
    def test_duplicate_accept_does_not_overwrite_user_edit(self):
        item=self.accept();r=self.client.patch('/api/ai/career-profile/items/'+item['id'],json={'value':'Đã tự sửa thông tin','version':item['version']});self.assertEqual(r.status_code,200)
        self.client.post('/api/ai/career-profile/items',json=self.body())
        items=cp.read(self.identity['uid'])['items'];self.assertEqual(len(items),1);self.assertEqual(items[0]['value'],'Đã tự sửa thông tin')
    def test_persistence_and_delete_one(self):
        item=self.accept();self.assertEqual(cp.read('owner-one')['items'][0]['id'],item['id'])
        self.assertEqual(self.client.delete('/api/ai/career-profile/items/'+item['id']).status_code,204)
        self.assertEqual(cp.read('owner-one')['items'],[])
    def test_owner_is_server_verified_not_client_uid(self):
        item=self.accept();self.identity={'uid':'other-account','provider':'google.com'}
        self.assertEqual(self.client.get('/api/ai/career-profile').json()['items'],[])
        self.assertEqual(self.client.post('/api/ai/career-profile/items',json=self.body()).status_code,404)
        self.assertEqual(self.client.patch('/api/ai/career-profile/items/'+item['id'],json={'value':'attack','version':1}).status_code,409)
        self.client.delete('/api/ai/career-profile/items/'+item['id']);self.assertEqual(len(cp.read('owner-one')['items']),1)
        self.assertEqual(self.client.post('/api/ai/career-profile/items',json={**self.body(),'owner':'owner-one'}).status_code,422)
    def test_profile_opt_out_backend_and_confirmed_context_only(self):
        self.accept();state={'uid':'owner-one','session_id':self.session['id'],'confirmed_profile_access':True}
        with patch('advisor.confirmed_profile.context_items',side_effect=AssertionError('must not read profile')):self.assertEqual(load_profile(state)['confirmed_profile'],[])
        r=self.client.put('/api/ai/sessions/'+self.session['id']+'/profile-use',json={'use_profile':True});self.assertEqual(r.status_code,200)
        self.assertEqual(load_profile(state)['confirmed_profile'][0]['value'],self.body()['value'])
        self.client.put('/api/ai/sessions/'+self.session['id']+'/profile-use',json={'use_profile':False});self.assertEqual(load_profile(state)['confirmed_profile'],[])
    def test_guest_claim_moves_only_verified_owner_and_keeps_ttl_until_consent(self):
        self.identity['provider']='anonymous';item=self.accept();self.assertIsNotNone(item['expires_at'])
        claim_guest_history('owner-one','account-new');self.assertEqual(cp.read('owner-one')['items'],[])
        moved=cp.read('account-new')['items'][0];self.assertIsNotNone(moved['expires_at']);self.assertEqual(moved['confirmed_by'],'owner-one')
        self.identity={'uid':'account-new','provider':'google.com'}
        r=self.client.patch('/api/ai/career-profile/items/'+moved['id'],json={'value':moved['value'],'version':moved['version'],'retain':True});self.assertEqual(r.status_code,200);self.assertIsNone(r.json()['items'][0]['expires_at'])
        with self.assertRaises(Exception):claim_guest_history('owner-one','wrong-account')
    def test_concurrent_confirm_is_idempotent(self):
        def one(_):return cp.confirm('owner-one','password',self.session,self.body()['proposal_id'],self.body()['value'])
        with ThreadPoolExecutor(max_workers=2) as pool:list(pool.map(one,range(2)))
        self.assertEqual(len(cp.read('owner-one')['items']),1)
    def test_stale_edit_and_explicit_confirmation(self):
        item=self.accept();body={'value':'Thay đổi hợp lệ','version':1}
        self.assertEqual(self.client.patch('/api/ai/career-profile/items/'+item['id'],json=body).status_code,200)
        self.assertEqual(self.client.patch('/api/ai/career-profile/items/'+item['id'],json=body).status_code,409)
        request=self.body();request.pop('confirmed');self.assertEqual(self.client.post('/api/ai/career-profile/items',json=request).status_code,422)
    def test_retain_conversation_preserves_id_and_survey(self):
        sid=self.session['id'];r=self.client.post('/api/ai/sessions/'+sid+'/retain');self.assertEqual(r.status_code,200,r.text)
        self.assertTrue(r.json()['session']['remember']);self.assertEqual(r.json()['session']['id'],sid);self.assertEqual(r.json()['session']['messages'],self.session['messages'])
        self.assertEqual(self.client.post('/api/ai/sessions/'+sid+'/retain').status_code,200)
    def test_delete_all_removes_confirmed_data_too(self):
        self.accept();self.assertEqual(self.client.delete('/api/ai/data').status_code,204);self.assertEqual(cp.read('owner-one')['items'],[])
    def test_disabled_profile_cannot_import_legacy_inference(self):
        with patch.dict(os.environ,{'ADVISOR_PROFILE_ENABLED':'false'}):
            self.assertEqual(self.client.get('/api/ai/career-profile').json()['items'],[])
            self.assertEqual(self.client.post('/api/ai/career-profile/items',json=self.body()).status_code,503)
    def test_expired_guest_content_is_not_returned_and_is_cleaned(self):
        self.identity['provider']='anonymous';self.accept()
        with self.connection() as db:db.execute("UPDATE advisor_profile_items SET expires_at=NOW()-INTERVAL '1 minute' WHERE owner=%s",('owner-one',))
        self.assertEqual(cp.read('owner-one')['items'],[])
        with self.connection() as db:self.assertEqual(db.execute('SELECT count(*) AS n FROM advisor_profile_items').fetchone()['n'],0)
    def test_migration_guard_rolls_back_without_altering_old_rows(self):
        import psycopg
        def counts():
            with self.connection() as db:return [db.execute('SELECT count(*) AS n FROM '+t).fetchone()['n'] for t in ('advisor_sessions','advisor_temporary_sessions','guest_ai_requests','guest_ai_usage')]
        before=counts()
        with self.assertRaises(psycopg.Error):
            with self.connection() as db:db.execute((Path(__file__).resolve().parents[1]/'migrations/006_confirmed_career_profile.sql').read_text(encoding='utf8'))
        self.assertEqual(counts(),before)
    def test_rejection_survives_reload_and_cannot_modify_other_session(self):
        sid=self.session['id'];pid=self.analysis['proposed_profile_items'][1]['id']
        r=self.client.post(f'/api/ai/sessions/{sid}/profile-proposals/{pid}/reject');self.assertEqual(r.status_code,200)
        self.assertIn(pid,self.client.get('/api/ai/sessions/'+sid).json()['session']['messages'][0]['profile_rejections'])
        self.identity={'uid':'other','provider':'password'}
        self.assertEqual(self.client.post(f'/api/ai/sessions/{sid}/profile-proposals/{pid}/reject').status_code,404)
    def test_bounded_expiry_cleanup_does_not_remove_account_items(self):
        self.accept()
        self.identity['uid']='other-owner'
        with self.connection() as db:
            db.execute('''INSERT INTO advisor_profile_items(id,owner,category,value,confirmed_by,source_session_id,source_proposal_id,metadata,expires_at)
                VALUES(%s,'expired','interests','Vẽ tranh','expired','s','p','{}',NOW()-INTERVAL '1 minute')''',(str(uuid4()),))
        self.assertEqual(cp.purge_expired(1),1);self.assertEqual(len(cp.read('owner-one')['items']),1)
        self.assertEqual(cp.purge_expired(1),0)
    def test_profile_write_rate_uses_shared_state_without_charging_chat_quota(self):
        with patch.dict(os.environ,{'PROFILE_USER_WRITES_PER_MINUTE':'1'}):
            self.accept()
            self.assertEqual(self.client.post('/api/ai/career-profile/items',json=self.body()).status_code,429)
        with self.connection() as db:
            self.assertEqual(db.execute('SELECT count(*) AS n FROM guest_ai_requests').fetchone()['n'],0)
    def test_controlled_profile_rollout_does_not_restrict_new_chat_pipeline(self):
        with patch.dict(os.environ,{'ADVISOR_CONTROLLED_ROLLOUT':'true','ADVISOR_TEST_UIDS':'different-qa','AI_DEMO_MODE':'true'}),patch('advisor.stable_graph.advisor_graph.ainvoke',side_effect=AssertionError('legacy graph must never run')):
            result=self.client.post('/api/ai/chat',json={'session_id':self.session['id'],'request_id':str(uuid4()),'message':'Thích vẽ'})
        self.assertEqual(result.status_code,200,result.text)
        self.assertEqual(result.json()['pipeline'],'task41')

if __name__=='__main__':unittest.main()
