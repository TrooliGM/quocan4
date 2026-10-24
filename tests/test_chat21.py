"""Focused Chat 2.1/editorial contracts. Providers mocked; PostgreSQL loopback only."""
import json
import hashlib
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
from uuid import uuid4

from career_library import catalog, find_career
from advisor.store import ConversationStore, empty_profile
from advisor.titles import first_chat_title, DEFAULT_TITLE
from advisor.survey import SurveyInput, save_survey, ANALYSIS_MESSAGE
from advisor import graph, postgres_store as pg
from advisor.postgres_adapter import PostgresConversationStore
from postgres_fixture import LocalPostgres

ROOT=Path(__file__).resolve().parents[1]
REPLY={'answer':'Lời đáp thử nghiệm','profile':empty_profile(),'summary':'','recommendations':[]}
IDENTITY_HASHES=['3eb9f09424b10cc343056fa1e364529bcd4aa8d18f3ffc03e800a3813f4c4631','564e8b32a8297d355906a675017afb8f74aca1e9370b1b8656b0eb862e0dafa7','ea43912146c90c262a76a82cd940f99298b48e27f94f7e5c262d18b58b1f4432','68a8cc20d35d5a1d54065f951b9b008c02db216f9bb295301f33c5d22cf00d50']

class EditorialTests(unittest.TestCase):
    def test_all_four_batches_complete_and_identity_unchanged(self):
        careers=catalog().careers
        self.assertEqual(len(careers),200)
        self.assertEqual(len({c.category_id for c in careers}),12)
        for batch in range(1,5):
            current=json.loads((ROOT/f'data/careers-{batch}.json').read_text(encoding='utf8'))
            identity='\n'.join('|'.join(c[k] for k in ('career_id','name','category_id')) for c in current)
            self.assertEqual(hashlib.sha256(identity.encode('utf8')).hexdigest(),IDENTITY_HASHES[batch-1])
        for c in careers:
            with self.subTest(career=c.career_id):
                self.assertEqual(c.profile_version,2)
                self.assertTrue(5<=len(c.daily_tasks)<=8)
                self.assertEqual(len(c.daily_tasks),len(set(c.daily_tasks)))
                self.assertGreaterEqual(len(c.challenges),3)
                self.assertEqual(len(c.typical_day),3)
                self.assertEqual({d['skill'] for d in c.skill_details},set(c.skills))
                self.assertTrue(all(len(d['reason'])>30 for d in c.skill_details))
                self.assertEqual(len(c.learning_path),3)
                self.assertTrue(c.professional_requirements['note'])
                self.assertNotIn('Cơ quan, tổ chức chuyên môn',c.work_environment)
        self.assertEqual(len({c.description for c in careers}),200)
        self.assertEqual(len({tuple(c.daily_tasks) for c in careers}),200)
        self.assertEqual(len({c.work_environment for c in careers}),200)

    def test_representative_professional_boundaries(self):
        prosecutor=find_career('kiem-sat-vien')
        text=prosecutor.description+' '.join(prosecutor.daily_tasks+prosecutor.challenges)
        self.assertIn('quyền công tố',text); self.assertIn('gỡ tội',text)
        self.assertIn('không thay thẩm phán',text)
        self.assertNotIn('Kiểm sát viên quyết định hình phạt',text)
        self.assertTrue(any('chinhphu.vn' in s['url'] for s in prosecutor.sources))
        for cid,term in [('lap-trinh','log'),('chuyen-vien-nhan-su','lao động'),('ky-su-moi-truong','ô nhiễm'),('thiet-ke','bố cục'),('phi-cong','kiểm soát không lưu')]:
            c=find_career(cid);self.assertIn(term,c.description+' '.join(c.daily_tasks))
        self.assertIn('không đồng nhất',find_career('duoc-si').professional_requirements['note'])
        self.assertIn('lâm sàng',find_career('chuyen-vien-tam-ly').professional_requirements['note'])

    def test_ai_reference_excludes_verbose_editorial_sections(self):
        ref=graph.career_reference(find_career('bac-si'))
        self.assertIn('daily_tasks',ref)
        for key in ('typical_day','learning_path','sources','professional_requirements'):self.assertNotIn(key,ref)

class TitleTests(unittest.TestCase):
    def session(self,mode='career_discovery',career=None):
        return {'title':DEFAULT_TITLE,'messages':[{'role':'assistant','career_context':{'mode':mode,'career_id':career},'survey':{'analysis_request_id':'analysis'}},{'role':'user','content':'x'}]}
    def test_internal_and_survey_never_become_title(self):
        for message,rid in [(ANALYSIS_MESSAGE,'other'),('Em thích vẽ và thích máy tính','analysis'),('Hãy phân tích khảo sát cũ...','other')]:
            self.assertEqual(first_chat_title(self.session(),message,rid),'Khám phá nghề phù hợp')
    def test_career_and_real_day_topic(self):
        self.assertEqual(first_chat_title(self.session('career_exploration','chuyen-vien-nhan-su'),'Xin tìm hiểu','1'),'Tìm hiểu nghề Chuyên viên nhân sự')
        self.assertEqual(first_chat_title(self.session(),'Một ngày làm Bác sĩ có gì?','1'),'Một ngày làm Bác sĩ')
    def test_manual_even_default_and_existing_titles_preserved(self):
        s=self.session();s['messages'][0]['manually_renamed']=True
        self.assertEqual(first_chat_title(s,'Bác sĩ','1'),DEFAULT_TITLE)
        s=self.session();s['title']='Tên học sinh đã chọn'
        self.assertEqual(first_chat_title(s,ANALYSIS_MESSAGE,'analysis'),s['title'])
        s=self.session();s['messages'] += [{'role':'assistant'},{'role':'user'}]
        self.assertEqual(first_chat_title(s,ANALYSIS_MESSAGE,'analysis'),DEFAULT_TITLE)

class PostgresChat21Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):cls.cluster=LocalPostgres().__enter__()
    @classmethod
    def tearDownClass(cls):cls.cluster.__exit__(None,None,None)
    def test_manual_and_automatic_titles_atomic_both_storage_modes(self):
        with patch.object(pg,'postgres_connection',self.cluster.schema()):
            store=PostgresConversationStore()
            for remember in (False,True):
                for manual in (False,True):
                    s=store.create('owner',remember,{'mode':'career_exploration','career_id':'bac-si'})
                    save_survey(store,'owner',s['id'],SurveyInput(answers=['Tìm hiểu nghề']*5))
                    if manual:store.rename('owner',s['id'],DEFAULT_TITLE)
                    result=pg.save_messages_atomic('owner',s['id'],str(uuid4()),ANALYSIS_MESSAGE,REPLY,'demo')
                    self.assertEqual(result['title'],DEFAULT_TITLE if manual else 'Tìm hiểu nghề Bác sĩ')
                    self.assertEqual(len(store.get('owner',s['id'])['messages']),3)
                    with self.assertRaises(Exception):store.rename('other',s['id'],'Không được sửa')
    def test_sqlite_fallback_manual_marker_survives_write(self):
        with tempfile.TemporaryDirectory() as folder:
            store=ConversationStore('sqlite:///'+str(Path(folder)/'test.sqlite3'))
            for remember in (False,True):
                s=store.create('owner',remember);store.rename('owner',s['id'],DEFAULT_TITLE)
                self.assertTrue(store.get('owner',s['id'])['messages'][0]['manually_renamed'])
