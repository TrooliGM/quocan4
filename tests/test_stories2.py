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
    def test_all_200_ids_scenes_and_unique_editorial_content(self):
        result=validate();self.assertEqual(result['stories'],200);self.assertEqual(result['scenes'],1000)
        self.assertEqual(result['decisions'],400);self.assertEqual(result['verified_videos'],0)

    def test_every_story_public_and_bounded_payload(self):
        with TestClient(app) as client:
            for c in catalog().careers:
                with self.subTest(career=c.career_id):
                    r=client.get('/api/career-stories/'+c.career_id)
                    self.assertEqual(r.status_code,200);self.assertEqual(r.json()['name'],c.name)
                    self.assertLess(len(r.content),20000)

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

    def test_preview_readonly_label_does_not_weaken_security(self):
        import os
        with patch.dict(os.environ,{'STORIES_PREVIEW_READ_ONLY':'true','VERCEL':'1','DATABASE_URL':'','DEEPSEEK_API_KEY':'','AI_DEMO_MODE':'false'}), TestClient(app) as client:
            self.assertTrue(client.get('/api/career-stories').json()['preview_read_only'])
            self.assertEqual(client.post('/api/ai/chat',json={'message':'test','session_id':'00000000-0000-0000-0000-000000000000'}).status_code,401)
            self.assertEqual(client.post('/api/advice',json={'question':'Hỏi về nghề'}).status_code,401)
            self.assertEqual(client.post('/api/career-stories/bac-si/ask',json={'question':'Hỏi về nghề'}).status_code,401)
            self.assertEqual(client.post('/api/ai/guest/session').status_code,503)

    def test_art_keys_exist_and_non_health_is_not_a_doctor(self):
        import re
        from pathlib import Path
        keys=set(re.findall(r'^  (\w+):',Path('public/assets/story-art.js').read_text(encoding='utf8'),re.M))
        for c in catalog().careers:
            story=get_story(c.career_id)
            self.assertTrue({s['art'] for s in story['scenes']}.issubset(keys))
            if c.category_id!='health':self.assertFalse({s['art'] for s in story['scenes']}&{'analysis','consult','conference','prescription','emergency'})

    def test_domain_review_samples_in_twelve_groups(self):
        samples={'lap-trinh':'lỗi','bac-si':'thuốc','giao-vien':'học sinh','ky-su-co-khi':'rung',
                 'chuyen-vien-nhan-su':'chính sách','ke-toan-vien':'chứng từ','hoa-si-truyen-tranh':'khung',
                 'nha-bao':'nguồn','kiem-sat-vien':'gỡ tội','chuyen-vien-bao-ton-da-dang-sinh-hoc':'vị trí',
                 'phi-cong':'thời tiết','nha-toan-hoc':'chứng minh'}
        groups=set()
        for cid,word in samples.items():
            s=get_story(cid);groups.add(s['category_id'])
            self.assertIn(word,' '.join([s['intro'],s['takeaway'],*[p['caption'] for p in s['scenes']]]).lower())
        self.assertEqual(len(groups),12)

if __name__=='__main__': unittest.main()
