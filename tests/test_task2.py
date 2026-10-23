import os
import json
import unittest
from pathlib import Path
from unittest.mock import patch, AsyncMock
from uuid import uuid4
from fastapi import Header, HTTPException
from fastapi.testclient import TestClient
from app import app
from advisor.routes import require_user
from advisor import postgres_store as pg
from advisor.guest_quota import get_guest_usage
from advisor.graph import retrieve_careers
from career_library import catalog, CATEGORIES
from postgres_fixture import LocalPostgres


def user(authorization: str | None = Header(default=None)):
    if authorization not in ('Bearer guest-a','Bearer guest-b','Bearer member'):
        raise HTTPException(401)
    uid=authorization.split()[1]
    return {'uid':uid,'provider':'anonymous' if uid.startswith('guest') else 'password'}


class LibraryTests(unittest.TestCase):
    def test_data_and_public_api(self):
        rows=catalog().careers
        self.assertEqual(len(rows),200)
        self.assertEqual(len(set(c.description for c in rows)),200)
        self.assertEqual(set(c.category_id for c in rows),set(CATEGORIES))
        from content import CAREERS
        by_name={c.name:c.career_id for c in rows}
        for legacy in CAREERS:self.assertEqual(by_name[legacy['name']],legacy['id'])
        with TestClient(app) as client:
            self.assertEqual(len(client.get('/api/career-library/categories').json()['items']),12)
            r=client.get('/api/career-library').json()
            self.assertEqual(r['total'],200);self.assertEqual(len(r['items']),12)
            ids=[]
            for i in range(0,200,24):ids.extend(c['career_id'] for c in client.get(f'/api/career-library?offset={i}&limit=24').json()['items'])
            self.assertEqual(len(set(ids)),200)
            self.assertEqual(client.get('/api/career-library?q=lap+trinh').json()['total'],client.get('/api/career-library?q=LẬP+TRÌNH').json()['total'])
            self.assertEqual(client.get('/api/career-library?category_id=invalid').status_code,422)
            self.assertEqual(client.get('/api/career-library?q=zxwkjq').json()['total'],0)
            self.assertEqual(client.get('/api/career-stories/bac-si').status_code,200)
            r=client.get('/api/career-stories/ky-su-du-lieu')
            self.assertEqual(r.status_code,404);self.assertIn('đang được cập nhật',r.json()['detail'])


class ModeTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):cls.cluster=LocalPostgres().__enter__()
    @classmethod
    def tearDownClass(cls):cls.cluster.__exit__(None,None,None)
    def setUp(self):
        self.env=patch.dict(os.environ,{'DATABASE_URL':self.cluster.url,'AI_DEMO_MODE':'true','DEEPSEEK_API_KEY':''})
        self.db=patch.object(pg,'postgres_connection',self.cluster.schema())
        self.env.start();self.db.start();app.dependency_overrides[require_user]=user;self.client=TestClient(app)
    def tearDown(self):
        self.client.close();app.dependency_overrides.pop(require_user,None);self.db.stop();self.env.stop()
    def test_guest_modes_survey_quota_and_isolation(self):
        for mode in ('career_discovery','career_exploration'):
            h={'Authorization':'Bearer guest-a'}
            body={'remember':mode=='career_exploration','mode':mode}
            if mode=='career_exploration':body['career_id']='bac-si'
            r=self.client.post('/api/ai/sessions',headers=h,json=body)
            self.assertEqual(r.status_code,201,r.text);session=r.json()['session'];sid=session['id']
            context=session['messages'][0]['career_context'];self.assertEqual(context['mode'],mode)
            for other in ('guest-b','member'):
                headers={'Authorization':'Bearer '+other}
                self.assertEqual(self.client.get('/api/ai/sessions/'+sid,headers=headers).status_code,404)
                self.assertEqual(self.client.put('/api/ai/sessions/'+sid+'/survey',headers=headers,json={'answers':['vẽ']*5}).status_code,404)
            self.assertEqual(self.client.put('/api/ai/sessions/'+sid+'/survey',headers=h,json={'answers':['vẽ và công nghệ']*5,'address':'anh'}).status_code,200)
            request={'session_id':sid,'request_id':str(uuid4()),'message':'Xin tìm hiểu'}
            r=self.client.post('/api/ai/chat',headers=h,json=request);self.assertEqual(r.status_code,200,r.text)
            loaded=self.client.get('/api/ai/sessions/'+sid,headers=h).json()['session']
            self.assertEqual(loaded['messages'][0]['career_context'],context)
            self.assertEqual(loaded['messages'][0]['survey']['address'],'anh')
            before=get_guest_usage('guest-a')['used_questions']
            self.assertTrue(self.client.post('/api/ai/chat',headers=h,json=request).json()['duplicate'])
            self.assertEqual(get_guest_usage('guest-a')['used_questions'],before)
            ref=retrieve_careers({'session':loaded,'message':'nghề','profile':{}})
            data=json.loads(ref['careers'])
            self.assertLessEqual(len(data),8)
            if mode=='career_exploration':self.assertEqual(data[0]['career_id'],'bac-si')
    def test_invalid_career_context_and_member(self):
        h={'Authorization':'Bearer member'}
        for body in ({'mode':'invalid'},{'mode':'career_exploration','career_id':'missing'},{'mode':'career_discovery','career_id':'bac-si'}):
            self.assertEqual(self.client.post('/api/ai/sessions',headers=h,json=body).status_code,422)
        r=self.client.post('/api/ai/sessions',headers=h,json={'mode':'career_exploration','career_id':'lap-trinh'})
        self.assertEqual(r.status_code,201)
    def test_live_payload_exploration_scope(self):
        import httpx
        h={'Authorization':'Bearer member'}
        session=self.client.post('/api/ai/sessions',headers=h,json={'mode':'career_exploration','career_id':'bac-si'}).json()['session']
        self.client.put('/api/ai/sessions/'+session['id']+'/survey',headers=h,json={'answers':['Thích tìm hiểu sinh học']*5,'address':'chị'})
        response=httpx.Response(200,json={'choices':[{'finish_reason':'stop','message':{'content':'Chị sẽ cùng em tìm hiểu công việc bác sĩ và cách quan sát thực tế.'}}]})
        with patch.dict(os.environ,{'AI_DEMO_MODE':'false','DEEPSEEK_API_KEY':'test-placeholder'}), patch('advisor.graph.post_completion',new_callable=AsyncMock,return_value=response) as provider:
            result=self.client.post('/api/ai/chat',headers=h,json={'session_id':session['id'],'request_id':str(uuid4()),'message':'Nghề bác sĩ có gì khó?'})
        self.assertEqual(result.status_code,200,result.text)
        payload=provider.call_args_list[0].args[0]
        text=json.dumps(payload,ensure_ascii=False)
        self.assertIn('Chế độ career_exploration',text)
        self.assertIn('Không chuyển thành bảng xếp hạng',text)
        self.assertIn('Thích tìm hiểu sinh học',text)
        self.assertNotIn('Kiến trúc sư',text)
