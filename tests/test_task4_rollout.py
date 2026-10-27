"""QA-only rollout is retired; server-verified Guest and Member share public features."""
import os
import unittest
from unittest.mock import patch
from fastapi import HTTPException
from fastapi.testclient import TestClient
from app import app
from advisor.routes import require_user
from advisor.rollout import allowed, uid_allowed, controlled, require


class RolloutTests(unittest.TestCase):
    def test_public_guest_and_member_ignore_legacy_qa_allowlist(self):
        with patch.dict(os.environ, {
            'VERCEL_ENV': 'production',
            'ADVISOR_CONTROLLED_ROLLOUT': 'true',
            'ADVISOR_TEST_UIDS': 'other-qa',
        }):
            self.assertFalse(controlled())
            for provider in ('anonymous', 'google.com', 'password'):
                self.assertTrue(allowed({'uid': 'ordinary-user', 'provider': provider}))
            self.assertTrue(uid_allowed('ordinary-member'))

    def test_missing_identity_or_unknown_provider_is_not_granted(self):
        for identity in ({}, {'uid': 'x'}, {'uid': '', 'provider': 'anonymous'},
                         {'uid': 'x', 'provider': 'custom'}, {'uid': None, 'provider': 'password'},
                         None):
            self.assertFalse(allowed(identity))
            with self.assertRaises(HTTPException):
                require(identity)
        self.assertFalse(uid_allowed(''))

    def test_query_uid_and_header_cannot_override_authenticated_identity(self):
        app.dependency_overrides[require_user] = lambda: {'uid': 'regular-member', 'provider': 'password'}
        try:
            with TestClient(app) as c:
                response = c.get('/api/ai/task4-shell?uid=someone-else',
                                 headers={'X-User-Id': 'someone-else'})
                self.assertEqual(response.status_code, 200)
                self.assertIn('Trợ lý hướng nghiệp', response.text)
        finally:
            app.dependency_overrides.pop(require_user, None)

    def test_shell_rejects_unrecognized_server_identity(self):
        app.dependency_overrides[require_user] = lambda: {'uid': 'x', 'provider': 'unknown'}
        try:
            with TestClient(app) as c:
                self.assertEqual(c.get('/api/ai/task4-shell').status_code, 404)
        finally:
            app.dependency_overrides.pop(require_user, None)
