"""Hồi quy runtime Vercel, cấu hình database và lỗi dịch vụ; không dùng mạng."""
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest
from uuid import uuid4
from unittest.mock import patch

import httpx
import psycopg
from fastapi.testclient import TestClient
import app as application
from advisor.routes import require_user
from advisor.store import get_store, ConversationStore, StorageConfigurationError
from advisor.postgres_adapter import PostgresConversationStore
from protection_fixture import ProtectedAPIFixture

ROOT = Path(__file__).resolve().parents[1]


class ReleaseRuntimeTests(ProtectedAPIFixture, unittest.TestCase):
    def test_pages_alias_assets_and_unknown_route(self):
        with TestClient(application.app,client=('127.0.0.1',1)) as client:
            for url in ('/', '/ai-career-advisor?start=1', '/chat', '/mot-ngay-lam-viec'):
                response = client.get(url)
                self.assertEqual(response.status_code, 200)
                self.assertIn('text/html', response.headers['content-type'])
            for url in ('/assets/chat.js', '/assets/chat.css', '/assets/firebase-client.js', '/assets/compass.svg'):
                self.assertEqual(client.get(url).status_code, 200)
            self.assertEqual(client.get('/not-a-page').status_code, 404)

    def test_missing_html_is_controlled_without_disclosing_path(self):
        with tempfile.TemporaryDirectory() as directory, patch.object(application, 'ROOT', Path(directory)), TestClient(application.app,client=('127.0.0.1',1)) as client:
            with self.assertLogs('app', level='ERROR') as logs:
                response = client.get('/ai-career-advisor?start=1')
            self.assertEqual(response.status_code, 503)
            self.assertIn('href="/"', response.text)
            self.assertNotIn(directory, response.text + str(logs.output))
            self.assertEqual(response.headers['cache-control'], 'no-store')

    def test_store_selection_and_vercel_never_uses_sqlite(self):
        with patch.dict(os.environ, {'VERCEL': '', 'DATABASE_URL': ''}):
            self.assertIsInstance(get_store(), ConversationStore)
        for url in ('postgresql://example.invalid/db', '  postgres://example.invalid/db  '):
            with patch.dict(os.environ, {'VERCEL': '1', 'DATABASE_URL': url}):
                self.assertIsInstance(get_store(), PostgresConversationStore)
        for url in ('', '  ', 'sqlite:////tmp/advisor.sqlite3', 'unknown://user:secret@host/db'):
            with patch.dict(os.environ, {'VERCEL': '1', 'DATABASE_URL': url}):
                with self.assertRaises(StorageConfigurationError):get_store()

    def test_database_errors_are_classified_and_redacted(self):
        application.app.dependency_overrides[require_user] = lambda: {'uid': 'release-test', 'provider': 'password'}
        try:
            cases = [(StorageConfigurationError('never print this secret'), 'DATABASE_CONFIGURATION'),
                     (psycopg.OperationalError('never print this secret'), 'DATABASE_UNAVAILABLE'),
                     (psycopg.errors.UndefinedTable('never print this secret'), 'DATABASE_SCHEMA_MISSING'),
                     (psycopg.errors.UndefinedColumn('never print this secret'), 'DATABASE_SCHEMA_MISSING'),
                     (psycopg.errors.InsufficientPrivilege('never print this secret'), 'DATABASE_PERMISSION')]
            with TestClient(application.app,client=('127.0.0.1',1)) as client:
                for error, code in cases:
                    with self.subTest(code=code), patch('advisor.routes.get_store', side_effect=error), self.assertLogs('app', level='ERROR') as logs:
                        response = client.get('/api/ai/sessions')
                    self.assertEqual(response.status_code, 503)
                    self.assertEqual(response.json()['detail']['code'], code)
                    self.assertNotIn('never print this secret', response.text + str(logs.output))
        finally:
            application.app.dependency_overrides.pop(require_user, None)

    def test_failed_postgres_connection_cannot_fall_back(self):
        with patch.dict(os.environ, {'VERCEL': '1', 'DATABASE_URL': 'postgresql://example.invalid/db'}):
            with patch('advisor.postgres_store.psycopg.connect', side_effect=psycopg.OperationalError('private')) as connect:
                with self.assertRaises(psycopg.OperationalError):get_store().list('test')
                connect.assert_called_once()

    def test_runtime_without_public_folder_or_dotenv(self):
        # Mô phỏng Function bundle, không phải vercel build hay deployment thật.
        with tempfile.TemporaryDirectory() as directory:
            target = Path(directory)
            for path in ROOT.glob('*.py'):shutil.copy2(path, target/path.name)
            shutil.copytree(ROOT/'advisor', target/'advisor', ignore=shutil.ignore_patterns('__pycache__'))
            for name in ('index.html', 'chat.html', 'stories.html'):
                shutil.copy2(ROOT/name, target/name)
                self.assertEqual((ROOT/name).read_bytes(), (ROOT/'public'/name).read_bytes())
            (target/'data').mkdir()
            shutil.copy2(ROOT/'stable-chat.html',target/'stable-chat.html')
            for index in range(1, 5):
                shutil.copy2(ROOT/'data'/f'careers-{index}.json', target/'data'/f'careers-{index}.json')
            shutil.copytree(ROOT/'data'/'stories', target/'data'/'stories')
            shutil.copy2(ROOT/'data'/'career-videos.json',target/'data'/'career-videos.json')
            (target/'.env').write_text('LABAN_BUNDLE_SENTINEL=should-not-load\n', encoding='utf-8')
            script = '''
import os
from fastapi.testclient import TestClient
from app import app
assert not os.getenv('LABAN_BUNDLE_SENTINEL')
with TestClient(app,client=('127.0.0.1',1)) as client:
 for url in ('/','/chat','/ai-career-advisor?start=1','/mot-ngay-lam-viec'):
  assert client.get(url).status_code == 200,url
 assert client.get('/api/ai/sessions').status_code == 401
 assert client.get('/api/career-library').json()['total'] == 200
 assert len(client.get('/api/career-library/categories').json()['items']) == 12
 assert len(client.get('/api/career-stories').json()['items']) == 200
 assert len(client.get('/api/career-videos/lap-trinh').json()['items']) == 1
 assert len(client.get('/api/career-videos/dau-bep').json()['items']) == 0
 for career in ('lap-trinh','ky-su-co-khi','kiem-sat-vien','ky-thuat-vien-phong-thi-nghiem'):
  r=client.get('/api/career-stories/'+career)
  assert r.status_code==200 and len(r.json()['scenes'])==5
print('isolated-runtime-ok')
'''
            environment = {**os.environ, 'VERCEL': '1', 'VERCEL_ENV':'production','ADVISOR_CONTROLLED_ROLLOUT':'true', 'DATABASE_URL': '', 'DEEPSEEK_API_KEY': ''}
            environment.pop('LABAN_BUNDLE_SENTINEL', None)
            result = subprocess.run([sys.executable, '-c', script], cwd=directory, env=environment, capture_output=True, text=True, timeout=30)
            self.assertEqual(result.returncode, 0, result.stderr[-1500:])
            config = json.loads((ROOT/'vercel.json').read_text(encoding='utf-8'))
            self.assertEqual(config['framework'], 'fastapi')
            self.assertNotIn('rewrites', config)
            self.assertIn('advisor/*.txt', config['functions']['app.py']['includeFiles'])
            self.assertIn('data/stories/batch-*.json',config['functions']['app.py']['includeFiles'])
            self.assertLessEqual(len(config['functions']['app.py']['includeFiles']),256)
            self.assertIn('data/career-videos.json',config['functions']['app.py']['includeFiles'])

    def test_provider_failure_matrix_for_public_endpoints(self):
        for url in ('/api/advice', '/api/career-stories/bac-si/ask'):
            for upstream, expected in ((401,503),(403,503),(429,503),(500,503),(400,503),(404,503)):
                async def fake_post(client, endpoint, **kwargs):
                    return httpx.Response(upstream, json={'error':'private-body'}, request=httpx.Request('POST',endpoint))
                with self.subTest(url=url,upstream=upstream), patch.dict(os.environ, {'DEEPSEEK_API_KEY':'test-secret'}), patch.object(httpx.AsyncClient,'post',fake_post), TestClient(application.app,client=('127.0.0.1',1)) as client:
                    with self.assertLogs('deepseek_client', level='WARNING') as logs:
                        response=client.post(url,json={'question':'Em thích vẽ'})
                    self.assertEqual(response.status_code, expected)
                    self.assertIsInstance(response.json()['detail'], str)
                    self.assertNotIn('test-secret', response.text+str(logs.output))
                    self.assertNotIn('private-body', response.text+str(logs.output))

    def test_provider_timeout_and_malformed_output(self):
        for body in (None, {}, {'choices':[]}, {'choices':[None]}, {'choices':[{'message':{'content':'truncated'},'finish_reason':'length'}]}):
            async def fake_post(client, endpoint, **kwargs):
                if body is None:raise httpx.ReadTimeout('private-provider-detail')
                return httpx.Response(200,json=body,request=httpx.Request('POST',endpoint))
            for url in ('/api/advice','/api/career-stories/bac-si/ask'):
                with patch.dict(os.environ, {'DEEPSEEK_API_KEY':'test-key'}), patch.object(httpx.AsyncClient,'post',fake_post), TestClient(application.app,client=('127.0.0.1',1)) as client:
                    response=client.post(url,json={'question':'Em thích vẽ'})
                    self.assertEqual(response.status_code,504 if body is None else 502)
                    self.assertNotIn('private-provider-detail', response.text)

    def test_provider_config_normalization_and_invalid_url_not_sent(self):
        from deepseek_client import post_completion, model_name, ProviderConfigurationError
        import asyncio
        async def fake_post(client, endpoint, **kwargs):
            self.assertEqual(endpoint,'https://api.deepseek.com/v1/chat/completions')
            self.assertEqual(kwargs['headers']['Authorization'],'Bearer test-key')
            return httpx.Response(200,json={},request=httpx.Request('POST',endpoint))
        with patch.dict(os.environ, {'DEEPSEEK_API_KEY':' test-key ', 'DEEPSEEK_MODEL':' deepseek-chat ', 'DEEPSEEK_BASE_URL':' https://api.deepseek.com/v1/ '}), patch.object(httpx.AsyncClient,'post',fake_post):
            self.assertEqual(model_name(),'deepseek-chat')
            asyncio.run(post_completion({}))
        for url in ('https://key:secret@example.com/path','https://api.deepseek.com:bad','https://bad host/path'):
            with patch.dict(os.environ, {'DEEPSEEK_API_KEY':'test-key','DEEPSEEK_BASE_URL':url}), patch.object(httpx.AsyncClient,'post') as post:
                with self.assertRaises(ProviderConfigurationError):asyncio.run(post_completion({}))
                post.assert_not_called()

    def test_memory_file_or_timeout_cannot_discard_valid_answer(self):
        from advisor.graph import compress_context
        from advisor.store import empty_profile
        import asyncio
        state={'profile':empty_profile(),'session':{'summary':'','messages':[{'role':'user','content':'fixture'} for _ in range(5)]},'message':'Em thích vẽ',
               'reply':{'answer':'Hãy thử thiết kế một poster.'}}
        with patch.dict(os.environ, {'AI_DEMO_MODE':'false'}), patch('advisor.graph.Path.read_text',side_effect=FileNotFoundError('private-path')):
            self.assertEqual(asyncio.run(compress_context(state)),{})
        with patch.dict(os.environ, {'AI_DEMO_MODE':'false'}), patch('advisor.graph.post_completion',side_effect=TimeoutError('private-timeout')):
            self.assertEqual(asyncio.run(compress_context(state)),{})

    def test_authenticated_chat_provider_errors_do_not_save_broken_turns(self):
        application.app.dependency_overrides[require_user] = lambda: {'uid':'release-test','provider':'password'}
        try:
            with tempfile.TemporaryDirectory() as directory, patch.dict(os.environ, {
                'VERCEL':'','DATABASE_URL':self.protected_cluster.url,
                'AI_DEMO_MODE':'false','DEEPSEEK_API_KEY':'test-key','DEEPSEEK_BASE_URL':'https://api.deepseek.com'
            }), TestClient(application.app,client=('127.0.0.1',1)) as client:
                sid=client.post('/api/ai/sessions',json={'remember':True}).json()['session']['id']
                self.assertEqual(client.put('/api/ai/sessions/'+sid+'/survey',json={
                    'answers':['Vẽ và công nghệ']*5,'address':'chị'}).status_code,200)
                for upstream in (401,403,429,500,'timeout','invalid-json'):
                    async def fake_post(client, endpoint, **kwargs):
                        if upstream=='timeout':raise httpx.ReadTimeout('private-error')
                        if upstream=='invalid-json':return httpx.Response(200,text='not-json',request=httpx.Request('POST',endpoint))
                        return httpx.Response(upstream,json={'error':'private-error'},request=httpx.Request('POST',endpoint))
                    with self.subTest(upstream=upstream), patch.object(httpx.AsyncClient,'post',fake_post):
                        response=client.post('/api/ai/chat',json={'session_id':sid,'request_id':str(uuid4()),'message':'Em thích vẽ'})
                        self.assertEqual(response.status_code,504 if upstream=='timeout' else 502 if upstream=='invalid-json' else 503)
                        self.assertNotIn('private-error',response.text)
                        self.assertEqual(len(client.get('/api/ai/sessions/'+sid).json()['session']['messages']),1)
        finally:application.app.dependency_overrides.pop(require_user,None)

    def test_chat_success_is_saved_despite_memory_provider_failure(self):
        application.app.dependency_overrides[require_user] = lambda: {'uid':'release-test','provider':'password'}
        calls=0
        async def fake_post(client, endpoint, **kwargs):
            nonlocal calls
            calls+=1
            if calls>1:raise httpx.ReadTimeout('memory-timeout')
            return httpx.Response(200,json={'choices':[{'message':{'content':'Hãy thử **thiết kế poster**.'},'finish_reason':'stop'}]},request=httpx.Request('POST',endpoint))
        try:
            with tempfile.TemporaryDirectory() as directory, patch.dict(os.environ, {
                'VERCEL':'','DATABASE_URL':self.protected_cluster.url,
                'AI_DEMO_MODE':'false','DEEPSEEK_API_KEY':'test-key','DEEPSEEK_BASE_URL':'https://api.deepseek.com'
            }), patch.object(httpx.AsyncClient,'post',fake_post), TestClient(application.app,client=('127.0.0.1',1)) as client:
                sid=client.post('/api/ai/sessions',json={'remember':True}).json()['session']['id']
                self.assertEqual(client.put('/api/ai/sessions/'+sid+'/survey',json={
                    'answers':['Vẽ và công nghệ']*5,'address':'chị'}).status_code,200)
                # Compression now runs every sixth turn, not on every short message.
                store=get_store();row=store.get('release-test',sid)
                row['messages'] += [{'role':role,'content':'Synthetic previous turn'} for _ in range(5) for role in ('user','assistant')]
                store.write('release-test',row)
                body={'session_id':sid,'request_id':str(uuid4()),'message':'Em thích vẽ'}
                result=client.post('/api/ai/chat',json=body)
                self.assertEqual(result.status_code,200,result.text)
                self.assertEqual(len(result.json()['session']['messages']),13)
                self.assertIn('poster',result.json()['session']['messages'][-1]['content'])
                self.assertTrue(client.post('/api/ai/chat',json=body).json()['duplicate'])
                self.assertEqual(calls,2)
        finally:application.app.dependency_overrides.pop(require_user,None)

    def test_usage_metrics_are_aggregate_only_and_malformed_usage_is_nonfatal(self):
        import asyncio
        from deepseek_client import post_completion, message_text
        from advisor.performance import current, RequestPerformance
        async def run():
            for usage,expected in [({'prompt_tokens':123,'completion_tokens':45},(123,45)),
                                   ({'prompt_tokens':'private-body','completion_tokens':-1},(0,0)),(None,(0,0))]:
                async def fake_post(client,endpoint,**kwargs):
                    return httpx.Response(200,json={'choices':[{'message':{'content':'valid answer'}}],'usage':usage},request=httpx.Request('POST',endpoint))
                state=RequestPerformance();token=current.set(state)
                try:
                    with patch.dict(os.environ,{'DEEPSEEK_API_KEY':'test-key','DEEPSEEK_BASE_URL':'https://api.deepseek.com'}),patch.object(httpx.AsyncClient,'post',fake_post):
                        response=await post_completion({'messages':[{'role':'user','content':'private-body'}]})
                    self.assertEqual(message_text(response),'valid answer')
                    self.assertEqual((state.prompt_tokens,state.completion_tokens),expected)
                    self.assertEqual(state.provider_calls,1)
                    self.assertNotIn('private-body',state.header());self.assertNotIn('test-key',state.header())
                finally:current.reset(token)
        asyncio.run(run())


if __name__=='__main__':unittest.main()
