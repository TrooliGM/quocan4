"""Synthetic survey/model cases + isolated local PG. No external AI or Neon."""
import asyncio
import copy
import json
import unittest
from unittest.mock import AsyncMock,patch
from uuid import uuid4

import httpx
from pydantic import ValidationError
from advisor import analysis_jobs as jobs
from advisor.store import get_store
from advisor.survey import SurveyInput
from advisor.survey_analysis import (AnalysisValidationError,ANALYSIS_SCHEMA_VERSION,
    analysis_trace,generate_analysis,validate_analysis)
import test_advisor30_profile as base


def response(raw,finish='stop'):
    return httpx.Response(200,json={'choices':[{'message':{'content':json.dumps(raw,ensure_ascii=False)},'finish_reason':finish}]})


def invalid_outputs():
    cases=[]
    missing=copy.deepcopy(base.RAW);missing.pop('proposed_profile_items');cases.append(('missing_field',missing,'missing'))
    missing=copy.deepcopy(base.RAW);missing['proposed_profile_items'][0].pop('evidence');cases.append(('missing_evidence',missing,'missing'))
    wrong=copy.deepcopy(base.RAW);wrong['summary']={'private':'not a string'};cases.append(('wrong_summary_type',wrong,'string_type'))
    wrong=copy.deepcopy(base.RAW);wrong['proposed_profile_items']='not a list';cases.append(('wrong_items_type',wrong,'list_type'))
    wrong=copy.deepcopy(base.RAW);wrong['proposed_profile_items'][0]['evidence'][0]['question_id']={};cases.append(('wrong_question_type',wrong,'int_type'))
    wrong=copy.deepcopy(base.RAW);wrong['proposed_profile_items'][0]['category']='PRIVATE_ENUM_DO_NOT_LOG';cases.append(('invalid_category',wrong,'literal_error'))
    wrong=copy.deepcopy(base.RAW);wrong['private-extra@example.invalid']='PRIVATE_EXTRA_VALUE';cases.append(('extra_field',wrong,'extra_forbidden'))
    cases.extend([('null_root',None,'model_type'),('list_root',[],'model_type'),('string_root','PRIVATE_ROOT','model_type')])
    return cases


class MatrixTests(unittest.TestCase):
    def survey(self,answers=None):return {'answers':list(answers or base.ANSWERS),'analysis_request_id':str(uuid4())}

    def test_complete_five_answers_and_grounded_output(self):
        s=self.survey();self.assertEqual(SurveyInput(answers=s['answers']).answers,s['answers'])
        result=validate_analysis(copy.deepcopy(base.RAW),s,'local-session');self.assertEqual(result['survey_id'],s['analysis_request_id']);self.assertTrue(result['proposed_profile_items'])

    def test_short_unknown_and_contradictory_answers_are_not_model_failures(self):
        cases=[('short',['?']*5),('unknown',['Chưa rõ','Chưa biết','Chưa biết','Chưa rõ','Muốn tìm hiểu']),
               ('contradiction',['Em thích ngoài trời','Em chỉ muốn ở trong nhà','Chưa biết','Cần tìm hiểu thêm','Muốn hiểu nghề'])]
        for name,answers in cases:
            with self.subTest(case=name):
                survey=self.survey(answers);SurveyInput(answers=answers)
                raw={'summary':'Chưa đủ dữ kiện để kết luận; cần làm rõ mong muốn qua một hoạt động an toàn.',
                     'proposed_profile_items':[],'clarification_questions':['Bạn muốn thử hoạt động nào trước?']}
                result=validate_analysis(raw,survey,'local-session');self.assertEqual(result['proposed_profile_items'],[])
        with self.assertRaises(ValidationError):SurveyInput(answers=['Chưa rõ']*4)
        with self.assertRaises(ValidationError):SurveyInput(answers=['']*5)

    def test_missing_wrong_types_and_nonconforming_json_have_sanitized_diagnostics(self):
        survey=self.survey()
        for name,raw,error_type in invalid_outputs():
            with self.subTest(case=name),patch('advisor.graph.post_completion',AsyncMock(return_value=response(raw))) as ai,self.assertLogs('advisor.survey_analysis',level='WARNING') as log:
                with self.assertRaises(AnalysisValidationError) as caught:asyncio.run(generate_analysis(survey,'local-session'))
                d=caught.exception.diagnostic;self.assertEqual(ai.await_count,2);self.assertEqual(d['error_code'],'analysis_schema');self.assertEqual(d['schema_version'],ANALYSIS_SCHEMA_VERSION);self.assertRegex(d['trace_id'],r'^[0-9a-f]{32}$');self.assertTrue(any(e['type']==error_type for e in d['errors']))
                lines=' '.join(log.output)
                for secret in ['PRIVATE_ENUM_DO_NOT_LOG','PRIVATE_EXTRA_VALUE','private-extra@example.invalid','PRIVATE_ROOT',*survey['answers']]:self.assertNotIn(secret,lines)

    def test_malformed_json_keeps_one_trace_across_bounded_repair(self):
        bad=httpx.Response(200,json={'choices':[{'message':{'content':'{"summary": PRIVATE_BROKEN'},'finish_reason':'stop'}]})
        with patch('advisor.graph.post_completion',AsyncMock(return_value=bad)) as ai,self.assertLogs('advisor.survey_analysis',level='WARNING') as log:
            with self.assertRaises(AnalysisValidationError):asyncio.run(generate_analysis(self.survey(),'local-session'))
        records=[json.loads(line.split('diagnostic=',1)[1]) for line in log.output];self.assertEqual(ai.await_count,2);self.assertEqual(len({d['trace_id'] for d in records}),1);self.assertTrue(all(d['error_code']=='analysis_json' for d in records));self.assertNotIn('PRIVATE_BROKEN',' '.join(log.output));self.assertIsNone(analysis_trace.get())
        self.assertNotIn('trace_id',ai.call_args.args[0]['messages'][-1]['content']);self.assertNotIn('frames',ai.call_args.args[0]['messages'][-1]['content'])

    def test_independent_tasks_do_not_share_trace_or_leave_context(self):
        async def run():
            return await asyncio.gather(generate_analysis(self.survey(),'local-a'),generate_analysis(self.survey(),'local-b'),return_exceptions=True)
        with patch('advisor.graph.post_completion',AsyncMock(return_value=response(None))),self.assertLogs('advisor.survey_analysis',level='WARNING'):
            errors=asyncio.run(run())
        self.assertTrue(all(isinstance(e,AnalysisValidationError) for e in errors));self.assertNotEqual(errors[0].diagnostic['trace_id'],errors[1].diagnostic['trace_id']);self.assertIsNone(analysis_trace.get())

    def test_markdown_fence_and_trailing_prose_are_not_valid_json(self):
        for text in ['```json\n'+json.dumps(base.RAW)+'\n```',json.dumps(base.RAW)+' PRIVATE_TRAILING_TEXT']:
            bad=httpx.Response(200,json={'choices':[{'message':{'content':text},'finish_reason':'stop'}]})
            with patch('advisor.graph.post_completion',AsyncMock(return_value=bad)),self.assertLogs('advisor.survey_analysis',level='WARNING') as log:
                with self.assertRaises(AnalysisValidationError) as error:asyncio.run(generate_analysis(self.survey(),'local-session'))
            self.assertEqual(error.exception.code,'analysis_json');self.assertEqual(error.exception.diagnostic['loc'],[]);self.assertNotIn('PRIVATE_TRAILING_TEXT',' '.join(log.output))


class MatrixStoreTests(unittest.TestCase):
    setUpClass=classmethod(base.ProfileTests.setUpClass.__func__)
    tearDownClass=classmethod(base.ProfileTests.tearDownClass.__func__)
    tearDown=base.ProfileTests.tearDown
    def setUp(self):
        base.ProfileTests.setUp(self)
        self.session['messages']=self.session['messages'][:1]
        self.session=get_store().write(self.identity['uid'],self.session)
        self.survey=self.session['messages'][0]['survey'];self.sid=self.session['id']
    def post(self,retry=False,**fields):return self.client.post('/api/ai/sessions/'+self.sid+'/analysis',json={'request_id':self.survey['analysis_request_id'],'retry':retry,**fields})
    def session_count(self):
        with self.connection() as db:return db.execute('SELECT (SELECT count(*) FROM advisor_sessions)+(SELECT count(*) FROM advisor_temporary_sessions) AS n').fetchone()['n']

    def test_validation_failure_keeps_survey_no_profile_session_or_chat_quota_change(self):
        self.identity['provider']='anonymous';quota=self.client.get('/api/ai/config').json()['guest_quota'];before=copy.deepcopy(self.session['messages']);count=self.session_count()
        with patch.dict('os.environ',{'DEEPSEEK_API_KEY':'local-fixture-key'}),patch('advisor.graph.post_completion',AsyncMock(return_value=response(None))) as ai,self.assertLogs(level='WARNING') as log:
            failed=self.post().json();self.assertEqual(failed['status'],'failed');self.assertEqual(failed['error_code'],'invalid_analysis');self.assertEqual(ai.await_count,2)
            trace=failed['trace_id'];self.assertRegex(trace,r'^[0-9a-f]{32}$');self.assertEqual(failed['schema_version'],ANALYSIS_SCHEMA_VERSION)
            self.assertEqual(self.post().json()['trace_id'],trace);self.assertEqual(ai.await_count,2)
        row=get_store().get(self.identity['uid'],self.sid);self.assertEqual(row['messages'][0]['survey'],before[0]['survey']);self.assertEqual(len(row['messages']),len(before));self.assertEqual(self.session_count(),count);self.assertEqual(self.client.get('/api/ai/career-profile').json()['items'],[]);self.assertEqual(self.client.get('/api/ai/config').json()['guest_quota'],quota)
        self.assertIn(trace,' '.join(log.output));self.assertIn('error_code=analysis_schema',' '.join(log.output))
        for answer in self.survey['answers']:self.assertNotIn(answer,' '.join(log.output))

    def test_explicit_retry_has_new_trace_same_request_and_cached_result(self):
        with patch.dict('os.environ',{'DEEPSEEK_API_KEY':'local-fixture-key'}),patch('advisor.graph.post_completion',AsyncMock(return_value=response(None))),self.assertLogs(level='WARNING'):
            first=self.post().json()
        with patch.dict('os.environ',{'DEEPSEEK_API_KEY':'local-fixture-key'}),patch('advisor.graph.post_completion',AsyncMock(return_value=response(base.RAW))) as ai:
            result=self.post(True).json();self.assertEqual(result['status'],'completed');self.assertNotEqual(result['trace_id'],first['trace_id']);self.assertEqual(result['request_id'],first['request_id']);self.assertEqual(self.post(True).json(),result);self.assertEqual(ai.await_count,1)
        self.assertEqual(self.client.get('/api/ai/career-profile').json()['items'],[])

    def test_client_cannot_supply_trace_or_replace_owner_request(self):
        with patch('advisor.graph.post_completion',AsyncMock()) as ai:
            self.assertEqual(self.post(trace_id='forged-trace').status_code,422)
            self.assertEqual(self.post(request_id=str(uuid4())).status_code,409);ai.assert_not_awaited()
        self.assertEqual(self.session_count(),1)

    def test_incomplete_survey_rejected_without_modifying_existing_survey(self):
        before=copy.deepcopy(self.survey)
        with patch('advisor.graph.post_completion',AsyncMock()) as ai:
            r=self.client.put('/api/ai/sessions/'+self.sid+'/survey',json={'answers':['Chưa rõ']*4});self.assertEqual(r.status_code,422);ai.assert_not_awaited()
        self.assertEqual(get_store().get(self.identity['uid'],self.sid)['messages'][0]['survey'],before)

    def test_old_cached_result_does_not_fabricate_a_historical_trace(self):
        self.session['messages'][0]['analysis_job']={'status':'completed','survey_hash':jobs.fingerprint(self.survey),
                'result':self.analysis,'attempts':1}
        get_store().write(self.identity['uid'],self.session)
        with patch('advisor.graph.post_completion',AsyncMock()) as ai:
            result=self.post(True).json();self.assertEqual(result['status'],'completed');self.assertIsNone(result['trace_id']);ai.assert_not_awaited()
