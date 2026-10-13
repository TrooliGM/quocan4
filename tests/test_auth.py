import json
import os
import time
import unittest
from types import SimpleNamespace
from unittest.mock import patch

import httpx
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from fastapi.testclient import TestClient
from google.auth import crypt, jwt

from app import app
import firebase_auth


class FirebaseAuthTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
        private_pem = key.private_bytes(serialization.Encoding.PEM, serialization.PrivateFormat.PKCS8, serialization.NoEncryption())
        cls.public_pem = key.public_key().public_bytes(serialization.Encoding.PEM, serialization.PublicFormat.SubjectPublicKeyInfo).decode()
        cls.signer = crypt.RSASigner.from_string(private_pem, key_id="test-key")

    def setUp(self):
        self.client = TestClient(app)
        self.env = patch.dict(os.environ, {"FIREBASE_PROJECT_ID": "test-project", "FIREBASE_API_KEY": "public-web-key", "FIREBASE_AUTH_DOMAIN": "test-project.firebaseapp.com", "FIREBASE_APP_ID": "1:test:web:app", "DEEPSEEK_API_KEY": "server-only-secret"})
        self.env.start()
        self.addCleanup(self.env.stop)

    def token(self, **changes):
        now = int(time.time())
        claims = {"aud": "test-project", "iss": "https://securetoken.google.com/test-project", "sub": "student-1", "iat": now - 10, "exp": now + 3600, "auth_time": now - 20, "email": "student@example.com", "name": "Học sinh", "email_verified": True, "firebase": {"sign_in_provider": "password"}}
        claims.update(changes)
        return jwt.encode(self.signer, claims).decode()

    def certificate_transport(self, url, **kwargs):
        self.assertEqual(url, firebase_auth.CERT_URL)
        return SimpleNamespace(status=200, data=json.dumps({"test-key": self.public_pem}).encode())

    def me(self, token):
        with patch.object(firebase_auth, "_certificate_request", self.certificate_transport):
            return self.client.get("/api/auth/me", headers={"Authorization": "Bearer " + token})

    def test_config_only_exposes_web_fields(self):
        response = self.client.get("/api/auth/config")
        self.assertTrue(response.json()["configured"])
        self.assertEqual(response.headers["cache-control"], "no-store")
        self.assertNotIn("server-only-secret", response.text)
        self.assertEqual(set(response.json()["config"]), {"apiKey", "authDomain", "projectId", "appId", "messagingSenderId"})

    def test_missing_config_and_token(self):
        with patch.dict(os.environ, {"FIREBASE_API_KEY": ""}):
            self.assertEqual(self.client.get("/api/auth/config").json(), {"configured": False, "config": None})
        for header in [None, "Basic abc", "Bearer", "Bearer a b", "Bearer " + "a" * 12001]:
            kwargs = {"headers": {"Authorization": header}} if header else {}
            response = self.client.get("/api/auth/me", **kwargs)
            self.assertEqual(response.status_code, 401)
            self.assertEqual(response.headers["cache-control"], "no-store")
        with patch.dict(os.environ, {"FIREBASE_PROJECT_ID": ""}):
            self.assertEqual(self.me(self.token()).status_code, 503)

    def test_valid_signature_returns_minimal_profile(self):
        response = self.me(self.token())
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.headers["cache-control"], "no-store")
        self.assertEqual(response.json()["user"], {"uid": "student-1", "email": "student@example.com", "display_name": "Học sinh", "email_verified": True, "provider": "password"})
        self.assertNotIn("auth_time", response.text)

    def test_invalid_claims_are_rejected(self):
        cases = [{"aud": "another-project"}, {"iss": "https://attacker.example"}, {"exp": int(time.time()) - 60}, {"iat": int(time.time()) + 3600}, {"sub": ""}, {"sub": "a" * 129}, {"auth_time": int(time.time()) + 3600}, {"auth_time": None}, {"auth_time": True}]
        for changes in cases:
            with self.subTest(changes=changes):
                response = self.me(self.token(**changes))
                self.assertEqual(response.status_code, 401)
                self.assertEqual(response.headers["www-authenticate"], "Bearer")

    def test_tampered_and_unsigned_tokens_are_rejected(self):
        token = self.token()
        header, body, signature = token.split(".")
        tampered = ".".join([header, body, ("A" if signature[0] != "A" else "B") + signature[1:]])
        for invalid in ["not-a-token", tampered, "eyJhbGciOiJub25lIn0.e30.", "W10.e30."]:
            self.assertEqual(self.me(invalid).status_code, 401)

    def test_certificate_cache_and_outage(self):
        with patch.dict(firebase_auth._certificate_cache, {"data": b"", "expires": 0.0}):
            response = httpx.Response(200, json={"test-key": self.public_pem}, headers={"cache-control": "public, max-age=3600"}, request=httpx.Request("GET", firebase_auth.CERT_URL))
            with patch.object(httpx, "get", return_value=response) as request:
                for _ in range(2):
                    self.assertEqual(self.client.get("/api/auth/me", headers={"Authorization": "Bearer " + self.token()}).status_code, 200)
                self.assertEqual(request.call_count, 1)
        with patch.dict(firebase_auth._certificate_cache, {"data": b"", "expires": 0.0}), patch.object(httpx, "get", side_effect=httpx.ConnectError("private network details")):
            response = self.client.get("/api/auth/me", headers={"Authorization": "Bearer " + self.token()})
            self.assertEqual(response.status_code, 503)
            self.assertNotIn("private network details", response.text)


if __name__ == "__main__":
    unittest.main()
