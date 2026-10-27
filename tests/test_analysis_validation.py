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
