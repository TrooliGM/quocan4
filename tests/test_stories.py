import os
import unittest
from unittest.mock import patch

import httpx
from fastapi.testclient import TestClient
from app import app
from content import CAREERS
from story_ai import story_graph
from protection_fixture import ProtectedAPIFixture


class StoryTests(ProtectedAPIFixture, unittest.TestCase):
    def test_catalog_and_every_career_has_complete_story(self):
        with TestClient(app) as client:
            self.assertEqual(client.get('/mot-ngay-lam-viec').status_code, 200)
            items = client.get('/api/career-stories').json()['items']
            self.assertEqual({c['id'] for c in items}, {c['id'] for c in CAREERS})
            for career in items:
                story = client.get('/api/career-stories/' + career['id']).json()
                self.assertEqual(len(story['scenes']), 4)
                self.assertEqual(len({s['art'] for s in story['scenes']}), 4)
                self.assertTrue(story['source_url'].startswith('https://www.bls.gov/'))
                for scene in story['scenes']:
                    self.assertEqual(len(scene['choices']), len(scene['feedback']))
                    self.assertIn(scene['correct'], range(len(scene['choices'])))
                    self.assertTrue(scene['caption'] and scene['speech'] and scene['skill'])
            self.assertEqual(client.get('/api/career-stories/unknown').status_code, 404)

    def test_question_validation_and_missing_provider(self):
        with patch.dict(os.environ, {'DEEPSEEK_API_KEY': ''}), TestClient(app,client=('127.0.0.1',1)) as client:
            url = '/api/career-stories/bac-si/ask'
            self.assertEqual(client.post(url, json={'question': '   '}).status_code, 422)
            self.assertEqual(client.post(url, json={'question': 'Hỏi về nghề', 'scene_index': 4}).status_code, 422)
            self.assertEqual(client.post(url, json={'question': 'Hỏi về nghề', 'scene_index': -1}).status_code, 422)
            self.assertEqual(client.post('/api/career-stories/unknown/ask', json={'question': 'Hỏi về nghề'}).status_code, 404)
            self.assertEqual(client.post(url, json={'question': 'Hỏi về nghề'}).status_code, 503)

    def test_ask_endpoint_and_provider_failure(self):
        async def fake_post(client, url, **kwargs):
            return httpx.Response(200, json={'choices': [{'message': {'content': 'Hãy thử lắng nghe một người bạn.'}}]}, request=httpx.Request('POST', url))
        with patch.dict(os.environ, {'DEEPSEEK_API_KEY': 'test-key'}), patch.object(httpx.AsyncClient, 'post', fake_post), TestClient(app,client=('127.0.0.1',1)) as client:
            response = client.post('/api/career-stories/bac-si/ask', json={'question': 'Em cần rèn kỹ năng gì?', 'scene_index': 1})
            self.assertEqual(response.status_code, 200)
            self.assertIn('lắng nghe', response.json()['answer'])
            self.assertEqual(response.headers['Cache-Control'], 'no-store')
        async def fail(client, url, **kwargs):
            return httpx.Response(401, json={'error': 'private_provider_error'}, request=httpx.Request('POST', url))
        with patch.dict(os.environ, {'DEEPSEEK_API_KEY': 'test-secret'}), patch.object(httpx.AsyncClient, 'post', fail), TestClient(app,client=('127.0.0.1',1)) as client:
            response = client.post('/api/career-stories/bac-si/ask', json={'question': 'Hỏi về nghề'})
            self.assertEqual(response.status_code, 503)
            self.assertNotIn('test-secret', response.text)
            self.assertNotIn('private_provider_error', response.text)


class StoryGraphTests(unittest.IsolatedAsyncioTestCase):
    async def test_deepseek_receives_selected_scene(self):
        captured = {}
        async def fake_post(client, url, **kwargs):
            captured.update(kwargs['json'])
            return httpx.Response(200, json={'choices': [{'message': {'content': 'Cùng kiểm tra dữ liệu nhé.'}}]}, request=httpx.Request('POST', url))
        with patch.dict(os.environ, {'DEEPSEEK_API_KEY': 'test-key'}), patch.object(httpx.AsyncClient, 'post', fake_post):
            await story_graph.ainvoke({'career_id': 'ky-su-moi-truong', 'scene_index': 1, 'question': 'Vì sao phải kiểm tra lại?', 'context': '', 'answer': ''})
        self.assertIn('Đọc điều dữ liệu kể', captured['messages'][0]['content'])
        self.assertIn('Kỹ sư môi trường', captured['messages'][0]['content'])
        self.assertEqual(captured['messages'][1]['content'], 'Vì sao phải kiểm tra lại?')
