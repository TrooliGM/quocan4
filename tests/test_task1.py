import json
import os
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch, AsyncMock
from uuid import uuid4

from fastapi import Header, HTTPException
from fastapi.testclient import TestClient
from app import app
from advisor.routes import require_user
from advisor.store import get_store
from advisor.survey import SurveyInput, save_survey, survey_data

ANSWERS = ['Vẽ và công nghệ', 'Làm poster', 'Kiên nhẫn', 'Được sáng tạo', 'Nghề nên thử']


def identity(authorization: str | None = Header(default=None)):
    if authorization not in ('Bearer a', 'Bearer b'):
        raise HTTPException(401)
    return {'uid': authorization[-1], 'provider': 'password'}


class SurveyTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.env = patch.dict(os.environ, {'DATABASE_URL':'sqlite:///'+str(Path(self.temp.name)/'test.db'),
            'AI_DEMO_MODE':'false', 'DEEPSEEK_API_KEY':'test-placeholder'})
        self.env.start()
        app.dependency_overrides[require_user] = identity
        self.client = TestClient(app,client=('127.0.0.1',1))
        self.headers = {'Authorization':'Bearer a'}

    def tearDown(self):
        self.client.close()
        app.dependency_overrides.pop(require_user, None)
        self.env.stop()
        self.temp.cleanup()

    def create(self, remember=False):
        r = self.client.post('/api/ai/sessions', headers=self.headers, json={'remember':remember})
        self.assertEqual(r.status_code, 201)
        return r.json()['session']

    def submit(self, session, **overrides):
        return self.client.put('/api/ai/sessions/'+session['id']+'/survey', headers=self.headers,
            json={'answers':ANSWERS, 'address':'anh', **overrides})

    def test_persistence_both_modes_immutable_and_idempotent(self):
        for remember in (False, True):
            session = self.create(remember)
            result = self.submit(session)
            self.assertEqual(result.status_code, 200, result.text)
            stored = result.json()['session']['messages'][0]['survey']
            self.assertEqual(stored['answers'], ANSWERS)
            self.assertEqual(self.submit(session).json()['session']['messages'][0]['survey'], stored)
            self.assertEqual(self.submit(session, address='chị').status_code, 409)
            loaded = self.client.get('/api/ai/sessions/'+session['id'], headers=self.headers).json()['session']
            self.assertEqual(survey_data(loaded), stored)
            other = self.create(remember)
            self.assertIsNone(survey_data(other))

    def test_auth_and_ownership(self):
        s = self.create(True); url = '/api/ai/sessions/'+s['id']+'/survey'
        body = {'answers':ANSWERS, 'address':'chị'}
        self.assertEqual(self.client.put(url,json=body).status_code,401)
        self.assertEqual(self.client.put(url,headers={'Authorization':'Bearer b'},json=body).status_code,404)
        self.assertIsNone(survey_data(get_store().get('a',s['id'])))

    def test_validation(self):
        session = self.create()
        for body in ({'answers':[]}, {'answers':[' ']*5}, {'answers':['x'*401]*5}, {'address':'system'}):
            self.assertEqual(self.submit(session, **body).status_code,422)

    def test_required_before_ai_and_legacy_compatibility(self):
        session = self.create()
        payload = {'session_id':session['id'],'request_id':str(uuid4()),'message':'Xin tư vấn'}
        with patch('advisor.routes.advisor_graph.ainvoke', new_callable=AsyncMock) as mock:
            self.assertEqual(self.client.post('/api/ai/chat',headers=self.headers,json=payload).status_code,409)
            mock.assert_not_called()
        # A pre-existing conversation remains usable, without survey backfill.
        session['messages'][0].pop('survey_required')
        get_store().write('a',session)
        with patch.dict(os.environ, {'AI_DEMO_MODE':'true'}):
            self.assertEqual(self.client.post('/api/ai/chat',headers=self.headers,json=payload).status_code,200)

    @patch('advisor.routes.check_ai_rate', lambda *args, **kwargs: None)
    def test_real_graph_payload_includes_survey_and_address(self):
        session = self.create(True); self.submit(session)
        payload = {'session_id':session['id'],'request_id':str(uuid4()),'message':'Phân tích khảo sát'}
        import httpx
        response = httpx.Response(200,json={'choices':[{'finish_reason':'stop','message':{'content':'Ba nhóm nghề đáng tìm hiểu: thiết kế, công nghệ và truyền thông.'}}]})
        with patch('advisor.graph.post_completion', new_callable=AsyncMock, return_value=response) as provider:
            result = self.client.post('/api/ai/chat',headers=self.headers,json=payload)
        self.assertEqual(result.status_code,200,result.text)
        sent = provider.call_args_list[0].args[0]
        text = json.dumps(sent,ensure_ascii=False)
        self.assertIn('xưng anh',text)
        self.assertIn(ANSWERS[0],text)
        self.assertIn('khoảng 3',text)
        self.assertEqual(survey_data(result.json()['session'])['answers'],ANSWERS)

    def test_home_routes_and_removed_corner(self):
        for path in ('/','/ai-career-advisor','/mot-ngay-lam-viec','/api/careers'):
            self.assertEqual(self.client.get(path).status_code,200,path)
        self.assertEqual(self.client.get('/api/articles').status_code,404)
        home = self.client.get('/').text
        self.assertNotIn('Góc hướng nghiệp',home)
        self.assertIn('href="/ai-career-advisor?mode=career_discovery" class="btn btn-coral">Bắt đầu',home)


class PostgresSurveyTests(unittest.TestCase):
    def test_row_lock_surveys_both_modes_and_ownership(self):
        from postgres_fixture import LocalPostgres
        from advisor import postgres_store as pg
        from advisor.postgres_adapter import PostgresConversationStore
        from concurrent.futures import ThreadPoolExecutor
        with LocalPostgres() as cluster:
            with patch.object(pg,'postgres_connection',cluster.schema()):
                store = PostgresConversationStore()
                for remember in (False,True):
                    row = store.create('owner',remember)
                    def submit(address):
                        try:
                            save_survey(store,'owner',row['id'],SurveyInput(answers=ANSWERS,address=address))
                            return 200
                        except HTTPException as exc:
                            return exc.status_code
                    with ThreadPoolExecutor(2) as pool:
                        self.assertEqual(sorted(pool.map(submit,['anh','chị'])),[200,409])
                    self.assertEqual(survey_data(store.get('owner',row['id']))['answers'],ANSWERS)
                    with self.assertRaises(HTTPException) as caught:
                        save_survey(store,'other',row['id'],SurveyInput(answers=ANSWERS))
                    self.assertEqual(caught.exception.status_code,404)


if __name__ == '__main__': unittest.main()
