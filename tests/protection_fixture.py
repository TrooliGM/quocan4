"""Existing provider contract tests use local PG + explicit verified-user stub.

Security boundaries themselves are tested without dependency overrides in
test_shared_ai_protection; this helper does not stand in for live Firebase.
"""
import os
from unittest.mock import patch
from advisor import postgres_store as pg
from advisor.routes import require_user
from postgres_fixture import LocalPostgres
from app import app


class ProtectedAPIFixture:
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.protected_cluster=LocalPostgres().__enter__()

    @classmethod
    def tearDownClass(cls):
        cls.protected_cluster.__exit__(None,None,None)
        super().tearDownClass()

    def setUp(self):
        super().setUp()
        connection=self.protected_cluster.schema()
        self.protected_patches=[patch.dict(os.environ,{'DATABASE_URL':self.protected_cluster.url}),patch.object(pg,'postgres_connection',connection)]
        for item in self.protected_patches:item.start()
        app.dependency_overrides[require_user]=lambda:{'uid':'provider-contract-test','provider':'password'}

    def tearDown(self):
        app.dependency_overrides.pop(require_user,None)
        for item in reversed(self.protected_patches):item.stop()
        super().tearDown()
