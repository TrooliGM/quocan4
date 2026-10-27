"""Schema/grounding contracts with synthetic data; never log student content."""
import asyncio,copy,json,unittest
from unittest.mock import AsyncMock,patch
import httpx
from pydantic import ValidationError
from advisor.survey_analysis import generate_analysis,validate_analysis,AnalysisValidationError,validation_diagnostic
from test_advisor30_profile import RAW,ANSWERS

class AnalysisValidationTests(unittest.TestCase):
    def setUp(self):self.survey={'answers':list(ANSWERS),'analysis_request_id':'fixture-survey'}
    def test_schema_failure_has_safe_trace_without_input_or_extra_field_name(self):
        raw=copy.deepcopy(RAW);raw['proposed_profile_items'][0]['category']='subjects'
        raw['private marker student@example.invalid']='do not log student text'
        response=httpx.Response(200,json={'choices':[{'message':{'content':json.dumps(raw)},'finish_reason':'stop'}]})
        with patch('advisor.graph.post_completion',AsyncMock(return_value=response)),self.assertLogs('advisor.survey_analysis',level='WARNING') as log:
            with self.assertRaises(AnalysisValidationError) as caught:asyncio.run(generate_analysis(self.survey,'synthetic-session'))
        d=caught.exception.diagnostic;self.assertEqual(d['schema'],'Analysis');self.assertEqual(d['exception'],'pydantic.ValidationError');self.assertTrue(d['frames'])
        self.assertTrue(any(r['type']=='literal_error' and r.get('known_enum_value')=='subjects' for r in d['errors']))
        logged=' '.join(log.output);self.assertNotIn('student@example.invalid',logged);self.assertNotIn('do not log student text',logged)
        for answer in ANSWERS:self.assertNotIn(answer,logged)
    def test_grounding_remains_strict(self):
        raw=copy.deepcopy(RAW);raw['proposed_profile_items'][0]['evidence'][0]['excerpt']='fabricated evidence'
        with self.assertRaisesRegex(ValueError,'ungrounded_survey_evidence'):validate_analysis(raw,self.survey,'synthetic-session')
    def test_unknown_enum_and_too_long_excerpt_are_not_silently_coerced(self):
        for field,value in [('confidence','high'),('excerpt','x'*201)]:
            raw=copy.deepcopy(RAW)
            if field=='excerpt':raw['proposed_profile_items'][0]['evidence'][0][field]=value
            else:raw['proposed_profile_items'][0][field]=value
            with self.assertRaises(ValidationError):validate_analysis(raw,self.survey,'synthetic-session')
    def test_schema_error_is_repaired_once_with_original_answers_and_unchanged_rules(self):
        bad=copy.deepcopy(RAW);bad['proposed_profile_items'][0]['category']='subjects'
        def response(raw):return httpx.Response(200,json={'choices':[{'message':{'content':json.dumps(raw)},'finish_reason':'stop'}]})
        before=copy.deepcopy(self.survey)
        with patch('advisor.graph.post_completion',AsyncMock(side_effect=[response(bad),response(RAW)])) as ai:
            result=asyncio.run(generate_analysis(self.survey,'synthetic-session'));self.assertTrue(result['proposed_profile_items']);self.assertEqual(ai.await_count,2)
            messages=ai.call_args.args[0]['messages'];self.assertIn('category',messages[-1]['content']);self.assertIn(ANSWERS[0],messages[1]['content'])
        self.assertEqual(self.survey,before)
    def test_grounding_error_is_not_accepted_by_repair(self):
        bad=copy.deepcopy(RAW);bad['proposed_profile_items'][0]['evidence'][0]['excerpt']='made up student evidence'
        response=httpx.Response(200,json={'choices':[{'message':{'content':json.dumps(bad)},'finish_reason':'stop'}]})
        with patch('advisor.graph.post_completion',AsyncMock(return_value=response)) as ai,self.assertLogs('advisor.survey_analysis',level='WARNING') as log:
            with self.assertRaises(AnalysisValidationError) as error:asyncio.run(generate_analysis(self.survey,'synthetic-session'))
        self.assertEqual(ai.await_count,2);self.assertEqual(error.exception.code,'ungrounded_survey_evidence');self.assertFalse(error.exception.diagnostic['case_whitespace_equivalent']);self.assertNotIn('made up student evidence',' '.join(log.output))
    def test_format_difference_is_diagnosed_but_not_silently_accepted(self):
        bad=copy.deepcopy(RAW);e=bad['proposed_profile_items'][0]['evidence'][0];e['excerpt']=e['excerpt'].upper()
        with self.assertRaises(AnalysisValidationError) as error:validate_analysis(bad,self.survey,'synthetic-session')
        self.assertTrue(error.exception.diagnostic['case_whitespace_equivalent'])
    def test_valid_first_result_does_not_add_model_call(self):
        response=httpx.Response(200,json={'choices':[{'message':{'content':json.dumps(RAW)},'finish_reason':'stop'}]})
        with patch('advisor.graph.post_completion',AsyncMock(return_value=response)) as ai:
            result=asyncio.run(generate_analysis(self.survey,'synthetic-session'));self.assertTrue(result['proposed_profile_items']);self.assertEqual(ai.await_count,1)
