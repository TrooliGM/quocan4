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
        # Seed historical confirmed data for compatibility/deletion tests only.
        body=self.body()
        return cp.confirm(self.identity['uid'],self.identity['provider'],self.session,body['proposal_id'],body['value'])['items'][0]
    def test_retired_profile_endpoints_do_not_read_or_create_items(self):
        self.assertEqual(self.client.get('/api/ai/career-profile').status_code,410)
        self.assertEqual(self.client.post('/api/ai/career-profile/items',json=self.body()).status_code,410)
        self.assertEqual(cp.read(self.identity['uid'])['items'],[])
    def test_legacy_data_preserved_and_not_loaded_even_when_opted_in(self):
        item=self.accept();self.session['messages'][0]['use_confirmed_profile']=True
        get_store().write(self.identity['uid'],self.session)
        state={'uid':self.identity['uid'],'session_id':self.session['id'],'confirmed_profile_access':True}
        with patch('advisor.confirmed_profile.context_items',side_effect=AssertionError('must not read')):self.assertEqual(load_profile(state)['confirmed_profile'],[])
        self.assertEqual(cp.read(self.identity['uid'])['items'][0]['id'],item['id'])
    def test_legacy_guest_claim_preserves_history_and_profile_without_enabling_usage(self):
        self.identity['provider']='anonymous';item=self.accept();claim_guest_history('owner-one','account-new')
        moved=cp.read('account-new')['items'][0];self.assertEqual(moved['id'],item['id']);self.assertIsNotNone(moved['expires_at'])
        self.identity={'uid':'account-new','provider':'google.com'}
        self.assertEqual(self.client.get('/api/ai/sessions/'+self.session['id']).status_code,200)
        self.assertEqual(self.client.put('/api/ai/sessions/'+self.session['id']+'/profile-use',json={'use_profile':True}).status_code,410)
    def test_retain_conversation_preserves_id_and_survey(self):
        sid=self.session['id'];r=self.client.post('/api/ai/sessions/'+sid+'/retain');self.assertEqual(r.status_code,200)
        self.assertTrue(r.json()['session']['remember']);self.assertEqual(r.json()['session']['id'],sid);self.assertEqual(r.json()['session']['messages'],self.session['messages'])
    def test_delete_all_removes_legacy_confirmed_data_even_when_disabled(self):
        self.accept()
        with patch.dict(os.environ,{'ADVISOR_PROFILE_ENABLED':'false'}):self.assertEqual(self.client.delete('/api/ai/data').status_code,204)
        self.assertEqual(cp.read('owner-one')['items'],[])
    def test_controlled_profile_rollout_does_not_restrict_new_chat_pipeline(self):
        with patch.dict(os.environ,{'ADVISOR_CONTROLLED_ROLLOUT':'true','ADVISOR_TEST_UIDS':'different-qa','AI_DEMO_MODE':'true'}),patch('advisor.stable_graph.advisor_graph.ainvoke',side_effect=AssertionError('legacy graph must never run')):
            result=self.client.post('/api/ai/chat',json={'session_id':self.session['id'],'request_id':str(uuid4()),'message':'Thích vẽ'})
        self.assertEqual(result.status_code,200,result.text)
        self.assertEqual(result.json()['pipeline'],'task41')

if __name__=='__main__':unittest.main()
