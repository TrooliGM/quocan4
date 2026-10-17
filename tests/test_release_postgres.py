"""Migration thật trên cluster chỉ dành kiểm thử; không truy cập Neon."""
import json
import os
from pathlib import Path
import subprocess
import sys
import unittest
from unittest.mock import patch
from urllib.parse import quote

from advisor import postgres_store as pg
from advisor.schema_check import inspect_schema
from postgres_fixture import LocalPostgres

ROOT = Path(__file__).resolve().parents[1]


class ReleasePostgresTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):cls.cluster=LocalPostgres().__enter__()

    @classmethod
    def tearDownClass(cls):cls.cluster.__exit__(None,None,None)

    def migrate(self, connection, filename):
        with connection() as db:
            db.autocommit=True
            db.execute((ROOT/'migrations'/filename).read_text(encoding='utf-8'))

    def test_fresh_and_repeated_migrations_keep_saved_history(self):
        connection=self.cluster.schema(initialize=False)
        with connection() as db:self.assertEqual(len(inspect_schema(db)['missing_tables']),6)
        self.migrate(connection,'001_conversations.sql')
        self.migrate(connection,'002_guest_quota.sql')
        with patch.object(pg,'postgres_connection',connection):
            saved=pg.create_postgres_session('migration-test')
            temporary=pg.create_temporary_session('migration-test')
        for _ in range(2):
            self.migrate(connection,'001_conversations.sql')
            self.migrate(connection,'002_guest_quota.sql')
        with connection() as db:self.assertTrue(inspect_schema(db)['ready'])
        with patch.object(pg,'postgres_connection',connection):
            self.assertEqual(pg.get_postgres_session('migration-test',saved['id'])['messages'],saved['messages'])
            self.assertEqual(pg.get_temporary_session('migration-test',temporary['id'])['messages'],temporary['messages'])

    def test_legacy_quota_gets_additive_columns_without_losing_usage(self):
        connection=self.cluster.schema(initialize=False)
        self.migrate(connection,'001_conversations.sql')
        with connection() as db:
            db.execute('''CREATE TABLE guest_ai_usage(uid TEXT PRIMARY KEY, used_questions INTEGER NOT NULL DEFAULT 0, updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW());
                CREATE TABLE guest_ai_requests(request_id TEXT PRIMARY KEY,uid TEXT NOT NULL,session_id TEXT NOT NULL,status TEXT NOT NULL,updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW())''')
            db.execute("INSERT INTO guest_ai_usage(uid,used_questions) VALUES('legacy-test',7)")
        self.migrate(connection,'002_guest_quota.sql')
        with connection() as db:
            self.assertTrue(inspect_schema(db)['ready'])
            self.assertEqual(db.execute("SELECT used_questions FROM guest_ai_usage WHERE uid='legacy-test'").fetchone()['used_questions'],7)

    def test_incompatible_schema_is_reported_not_coerced(self):
        connection=self.cluster.schema(initialize=False)
        with connection() as db:db.execute('CREATE TABLE advisor_sessions(id UUID PRIMARY KEY)')
        with connection() as db:
            report=inspect_schema(db)
            self.assertFalse(report['ready'])
            self.assertIn('advisor_sessions.id',report['incompatible_columns'])
            self.assertIn('advisor_sessions.messages',report['missing_columns'])

    def test_readonly_check_script_with_test_database(self):
        connection=self.cluster.schema()
        url=self.cluster.url+'?options='+quote('-c search_path='+connection.schema_name)
        result=subprocess.run([sys.executable,str(ROOT/'scripts/check_storage.py')],cwd=ROOT,
                              env={**os.environ,'LABAN_CHECK_DATABASE_URL':url},capture_output=True,text=True,timeout=20)
        self.assertEqual(result.returncode,0,result.stderr)
        self.assertTrue(json.loads(result.stdout)['ready'])
        self.assertNotIn(url,result.stdout)

    def test_runtime_connection_uses_bounded_database_waits(self):
        connection=self.cluster.schema()
        url=self.cluster.url+'?options='+quote('-c search_path='+connection.schema_name)
        with patch.dict(os.environ,{'DATABASE_URL':'  '+url+'  '}), pg.postgres_connection() as db:
            for setting,value in (('statement_timeout','10s'),('lock_timeout','3s'),('idle_in_transaction_session_timeout','15s')):
                self.assertEqual(db.execute('SHOW '+setting).fetchone()[setting],value)
            self.assertTrue(inspect_schema(db)['ready'])
