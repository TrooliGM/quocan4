import copy
import unittest
from unittest.mock import patch
from fastapi.testclient import TestClient
from pydantic import ValidationError
from app import app
from career_library import catalog
from career_stories import get_legacy_story
from story_library import Story, get_story, batch
from scripts.validate_stories import validate

class Stories2Tests(unittest.TestCase):
    def test_first_editorial_batch(self):
        self.assertEqual(validate([1])['stories'],50)

    def test_reject_broken_sequence_name_and_decision(self):
        original=get_story('lap-trinh')
        base={k:v for k,v in original.items() if k in Story.model_fields}
        for mutation in ('name','next','choice'):
            row=copy.deepcopy(base)
            if mutation=='name': row['name']='Một nghề khác'
            elif mutation=='next': row['scenes'][0]['next_scene_id']='missing'
            else: row['scenes'][1]['choices'][1]['choice_id']=row['scenes'][1]['choices'][0]['choice_id']
            with self.assertRaises(ValidationError): Story.model_validate(row)

    def test_public_routes_no_identity_or_model_calls(self):
        with patch('app.require_user',side_effect=AssertionError('Must be public')), TestClient(app) as client:
            rows=client.get('/api/career-stories').json()['items']
            self.assertEqual({r['id'] for r in rows},{c.career_id for c in catalog().careers})
            self.assertTrue(all('scenes' in r and 'caption' not in str(r) for r in rows))
            r=client.get('/api/career-stories/lap-trinh')
            self.assertEqual(r.status_code,200);self.assertEqual(r.json()['version'],2)
            self.assertEqual(client.get('/api/career-stories/not-real').status_code,404)
            self.assertEqual(client.get('/api/career-stories/../../.env').status_code,404)
            self.assertEqual(client.get('/api/career-stories/lap-trinh?version=3').status_code,422)

    def test_six_legacy_stories_retained_exactly(self):
        from content import CAREERS
        with TestClient(app) as client:
            for c in CAREERS:
                self.assertEqual(client.get('/api/career-stories/'+c['id']+'?version=1').json(),get_legacy_story(c['id']))

    def test_one_batch_loaded_per_story(self):
        batch.cache_clear();get_story('lap-trinh')
        self.assertEqual(batch.cache_info().misses,1)
        get_story('bac-si');self.assertEqual(batch.cache_info().misses,1)

if __name__=='__main__': unittest.main()
