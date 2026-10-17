import json
import os
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
from uuid import uuid4

import httpx
from fastapi.testclient import TestClient

from advisor.story_intent import suggest_story, validated_intent
from advisor.routes import require_user
from advisor.store import empty_profile, get_store
from app import app


def state(message, previous=None, semantic=None):
    return {'message': message, 'session': {'messages': previous or []},
            'story_intent': semantic, 'reply': {'answer': 'Cùng tìm hiểu nhé!',
            'profile': empty_profile(), 'summary': '', 'recommendations': []}}


class StoryIntentTests(unittest.TestCase):
    def test_equivalent_daily_questions(self):
        for message, expected in [
            ('Một ngày làm việc của bác sĩ như thế nào?', 'bac-si'),
            ('Cho mình trải nghiệm một ngày làm lập trình viên.', 'lap-trinh'),
            ('Giáo viên thường làm những gì mỗi ngày?', 'giao-vien'),
            ('Lập trình viên thường làm gì từ sáng đến tối?', 'lap-trinh'),
            ('Nếu làm kỹ sư phần mềm thì một ngày của mình sẽ ra sao?', 'lap-trinh'),
            ('Mình muốn biết công việc hằng ngày của nhà thiết kế đồ họa.', 'thiet-ke'),
        ]:
            with self.subTest(message=message):
                nav = suggest_story(state(message))['reply']['story_navigation']
                self.assertEqual(nav['choices'][0]['career_id'], expected)
                self.assertEqual(nav['intent'], 'career_day_experience')

    def test_semantic_intent_not_dependent_on_daily_keywords(self):
        semantic = {'intent':'career_day_experience', 'career_names':['Kỹ sư phần mềm'], 'confidence':.97,
                    'url':'https://evil.example/'}
        result = suggest_story(state('Nếu mai nhận việc, từng buổi ở chỗ làm mình sẽ trải qua những gì?', semantic=semantic))['reply']
        self.assertEqual(result['story_navigation']['choices'][0]['career_id'], 'lap-trinh')
        self.assertNotIn('evil', json.dumps(result))

    def test_missing_unknown_multiple_and_alias_disambiguation(self):
        missing = suggest_story(state('Mình muốn xem một ngày làm việc'))['reply']
        self.assertEqual(missing['story_navigation']['kind'], 'clarify')
        self.assertEqual(missing['answer'], 'Bạn muốn khám phá một ngày làm việc của nghề nào?')
        for text in ['Mình muốn biết lịch trình của kiến trúc sư.', 'Một ngày của bác sĩ thú y thế nào?', 'Một ngày làm người chăm sóc kỳ lân?']:
            nav = suggest_story(state(text))['reply']['story_navigation']
            self.assertEqual(nav['choices'], [])
            self.assertEqual(nav['kind'], 'unavailable')
        nav = suggest_story(state('Một ngày làm việc của bác sĩ và kỹ sư phần mềm khác nhau thế nào?'))['reply']['story_navigation']
        self.assertEqual(nav['kind'], 'choices')
        self.assertEqual({c['career_id'] for c in nav['choices']}, {'bac-si','lap-trinh'})

    def test_no_redirect_for_unrelated_or_declined_message(self):
        semantic = {'intent':'career_day_experience','career_names':['Bác sĩ'],'confidence':.99}
        for message in ['Lương của lập trình viên bao nhiêu?', 'Cơ hội việc làm của giáo viên?', 'Kỹ năng của bác sĩ?',
                        'Không muốn xem truyện, nói về một ngày làm bác sĩ ngay trong chat thôi.', 'Đừng chuyển trang']:
            self.assertNotIn('story_navigation', suggest_story(state(message, semantic=semantic))['reply'])
        self.assertNotIn('story_navigation', suggest_story(state('Mình thích vẽ'))['reply'])
        self.assertNotIn('story_navigation', suggest_story(state('Chỉ giải thích trong chat về một ngày làm bác sĩ.',
            semantic={'intent':'none','career_names':[],'confidence':.99}))['reply'])

    def test_model_career_names_cannot_inject_links_or_html(self):
        semantic={'intent':'career_day_experience','career_names':['[click](https://evil.example/)', '<img src=x>'],'confidence':.99}
        result=suggest_story(state('Cho mình xem trải nghiệm nghề nhé',semantic=semantic))['reply']
        self.assertNotIn('evil',json.dumps(result))
        self.assertEqual(result['story_navigation']['choices'],[])

    def test_clarification_and_pronoun_use_current_conversation(self):
        question = suggest_story(state('Mình muốn xem một ngày làm việc'))['reply']
        previous = [{'role':'assistant','content':question['answer'],'story_navigation':question['story_navigation']}]
        nav = suggest_story(state('Bác sĩ',previous))['reply']['story_navigation']
        self.assertEqual(nav['choices'][0]['career_id'],'bac-si')
        previous = [{'role':'user','content':'Mình thích làm giáo viên'}]
        nav = suggest_story(state('Nghề đó mỗi ngày ra sao?',previous))['reply']['story_navigation']
        self.assertEqual(nav['choices'][0]['career_id'],'giao-vien')

    def test_invalid_metadata_is_not_trusted(self):
        for raw in [None, [], {'intent':'career_day_experience','confidence':True},
                    {'intent':'career_day_experience','confidence':2},
                    {'intent':'career_day_experience','confidence':.2},
                    {'intent':'career_day_experience','confidence':.9,'career_names':'bác sĩ'}]:
            self.assertIsNone(validated_intent(raw))


class StoryIntentGraphTests(unittest.TestCase):
    def setUp(self):
        self.directory=tempfile.TemporaryDirectory()
        self.env=patch.dict(os.environ, {'DATABASE_URL':'sqlite:///'+str(Path(self.directory.name)/'test.sqlite3'),
            'AI_DEMO_MODE':'false','DEEPSEEK_API_KEY':'fake-test-key'})
        self.env.start()
        app.dependency_overrides[require_user]=lambda:{'uid':'story-test'}
        self.client=TestClient(app)

    def tearDown(self):
        self.client.close()
        app.dependency_overrides.pop(require_user,None)
        self.env.stop()
        self.directory.cleanup()

    def test_semantic_metadata_saved_and_restored_without_extra_model_call(self):
        calls=[]
        async def post(client,url,**kwargs):
            payload=kwargs['json'];calls.append(payload)
            memory='bộ nén ngữ cảnh' in payload['messages'][0]['content']
            data={'profile':empty_profile(),'summary':'Hỏi trải nghiệm nghề.',
                  'story_intent':{'intent':'career_day_experience','career_names':['Lập trình viên'],'confidence':.96}}
            content=json.dumps(data) if memory else 'Một công việc có nhiều hoạt động khác nhau.'
            return httpx.Response(200,json={'choices':[{'finish_reason':'stop','message':{'content':content}}]},request=httpx.Request('POST',url))
        session=self.client.post('/api/ai/sessions',json={'remember':True}).json()['session']
        message={'session_id':session['id'],'request_id':str(uuid4()),'message':'Nếu mai nhận việc, từng buổi ở chỗ làm mình sẽ trải qua những gì?'}
        with patch.object(httpx.AsyncClient,'post',post):
            result=self.client.post('/api/ai/chat',json=message)
            self.assertEqual(result.status_code,200,result.text)
            repeated=self.client.post('/api/ai/chat',json=message)
            self.assertEqual(repeated.status_code,200)
        self.assertEqual(len(calls),2)
        self.assertIn('recent_conversation',json.loads(calls[1]['messages'][1]['content']))
        last=result.json()['session']['messages'][-1]
        self.assertEqual(last['story_navigation']['choices'][0]['career_id'],'lap-trinh')
        restored=self.client.get('/api/ai/sessions/'+session['id']).json()['session']
        self.assertEqual(restored['messages'][-1],last)
        self.assertEqual(len(restored['messages']),3)

    def test_metadata_failure_keeps_answer_and_rule_fallback(self):
        async def post(client,url,**kwargs):
            memory='bộ nén ngữ cảnh' in kwargs['json']['messages'][0]['content']
            return httpx.Response(200,json={'choices':[{'message':{'content':'invalid JSON' if memory else 'Một ngày của bác sĩ.'}}]},request=httpx.Request('POST',url))
        session=self.client.post('/api/ai/sessions',json={}).json()['session']
        with patch.object(httpx.AsyncClient,'post',post):
            result=self.client.post('/api/ai/chat',json={'session_id':session['id'],'request_id':str(uuid4()),'message':'Một ngày làm việc của bác sĩ như thế nào?'})
        self.assertEqual(result.status_code,200,result.text)
        last=result.json()['session']['messages'][-1]
        self.assertIn('Một ngày của bác sĩ.',last['content'])
        self.assertEqual(last['story_navigation']['choices'][0]['career_id'],'bac-si')


if __name__=='__main__':
    unittest.main()
