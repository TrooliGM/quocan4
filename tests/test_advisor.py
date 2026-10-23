import io
import json
import os
import struct
import tempfile
import unittest
import wave
from pathlib import Path
from unittest.mock import patch
from uuid import uuid4

import httpx
from fastapi import Header, HTTPException
from fastapi.testclient import TestClient

from app import app
from advisor.routes import require_user
from advisor.store import ConversationStore, empty_profile, get_store
from advisor import voice


def fake_user(authorization: str | None = Header(default=None)):
    if authorization not in ("Bearer user-a", "Bearer user-b"):
        raise HTTPException(401, "Unauthorized")
    return {"uid": authorization.removeprefix("Bearer ")}


def live_reply():
    return "Bạn thích **vẽ** và biết một chút máy tính. Có thể thử **thiết kế đồ họa**."


def wav_audio(silent=False):
    buffer = io.BytesIO()
    with wave.open(buffer, "wb") as audio:
        audio.setnchannels(1); audio.setsampwidth(2); audio.setframerate(16000)
        audio.writeframes(struct.pack("<h", 0 if silent else 1000) * 16000)
    return buffer.getvalue()


class AdvisorTests(unittest.TestCase):
    def setUp(self):
        self.directory = tempfile.TemporaryDirectory()
        self.database = Path(self.directory.name) / "advisor.sqlite3"
        self.environment = patch.dict(os.environ, {"DATABASE_URL": "sqlite:///" + str(self.database),
            "AI_DEMO_MODE": "true", "DEEPSEEK_API_KEY": ""})
        self.environment.start()
        app.dependency_overrides[require_user] = fake_user
        self.client = TestClient(app)
        self.a = {"Authorization": "Bearer user-a"}
        self.b = {"Authorization": "Bearer user-b"}

    def tearDown(self):
        self.client.close()
        app.dependency_overrides.pop(require_user, None)
        self.environment.stop()
        self.directory.cleanup()

    def session(self, remember=False):
        response = self.client.post("/api/ai/sessions", headers=self.a, json={"remember": remember})
        self.assertEqual(response.status_code, 201, response.text)
        self.client.put('/api/ai/sessions/'+response.json()['session']['id']+'/survey', headers=self.a,
                        json={'answers':['Chưa rõ']*5,'address':'chị'}).raise_for_status()
        return response.json()["session"]

    def send(self, session, text="Mình thích Toán", request_id=None):
        return self.client.post("/api/ai/chat", headers=self.a, json={"session_id": session["id"],
                               "request_id": request_id or str(uuid4()), "message": text})

    def test_authenticated_apis_and_page_shell(self):
        for path in ("/api/ai/config", "/api/ai/sessions", "/api/ai/career-profile"):
            self.assertEqual(self.client.get(path).status_code, 401)
        self.assertEqual(self.client.post("/api/ai/sessions", json={}).status_code, 401)
        self.assertEqual(self.client.get("/ai-career-advisor").status_code, 200)
        response = self.client.get("/api/ai/config", headers=self.a)
        self.assertEqual(response.headers["cache-control"], "no-store")
        self.assertEqual(response.json()["mode"], "demo")
        self.assertNotIn("api_key", response.text.lower())
        self.assertIn("google", response.json()["microphone"])

    def test_account_isolation_for_every_session_operation(self):
        session = self.session(True)
        path = "/api/ai/sessions/" + session["id"]
        self.assertEqual(self.client.get(path, headers=self.b).status_code, 404)
        self.assertEqual(self.client.patch(path, headers=self.b, json={"title": "other"}).status_code, 404)
        self.assertEqual(self.client.delete(path, headers=self.b).status_code, 404)
        self.assertEqual(self.client.get("/api/ai/sessions", headers=self.b).json()["items"], [])
        body = {"session_id": session["id"], "request_id": str(uuid4()), "message": "Other user"}
        self.assertEqual(self.client.post("/api/ai/chat", headers=self.b, json=body).status_code, 404)

    def test_demo_retry_is_idempotent_and_input_is_validated(self):
        session = self.session()
        request_id = str(uuid4())
        response = self.send(session, request_id=request_id)
        self.assertEqual(response.status_code, 200, response.text)
        messages = response.json()["session"]["messages"]
        self.assertEqual(len(messages), 3)
        self.assertEqual(messages[-1]["mode"], "demo")
        self.assertIn("chưa gọi DeepSeek", messages[-1]["content"])
        duplicate = self.send(session, request_id=request_id)
        self.assertTrue(duplicate.json()["duplicate"])
        self.assertEqual(duplicate.json()["session"]["messages"], messages)
        self.assertEqual(self.send(session, "Nội dung khác", request_id).status_code, 409)
        self.assertEqual(self.send(session, " ").status_code, 422)
        self.assertEqual(self.send(session, "x" * 2001).status_code, 422)

    def test_consent_controls_disk_persistence(self):
        temporary = self.session(False)
        self.send(temporary, "Thông tin trong phiên tạm")
        other_store = ConversationStore("sqlite:///" + str(self.database))
        with self.assertRaises(HTTPException):
            other_store.get("user-a", temporary["id"])
        durable = self.session(True)
        self.send(durable, "Tin nhắn đã đồng ý lưu")
        restored = other_store.get("user-a", durable["id"])
        self.assertEqual(restored["messages"][1]["content"], "Tin nhắn đã đồng ý lưu")
        with other_store.connect() as db:
            self.assertEqual(db.execute("SELECT COUNT(*) FROM advisor_sessions").fetchone()[0], 1)
            self.assertNotIn("Thông tin trong phiên tạm", " ".join(db.iterdump()))

    def test_rename_delete_and_delete_all_do_not_affect_other_account(self):
        session = self.session(True)
        other = self.client.post("/api/ai/sessions", headers=self.b, json={"remember": True}).json()["session"]
        path = "/api/ai/sessions/" + session["id"]
        renamed = self.client.patch(path, headers=self.a, json={"title": "  Sở thích của mình  "})
        self.assertEqual(renamed.json()["session"]["title"], "Sở thích của mình")
        self.assertEqual(self.client.delete(path, headers=self.a).status_code, 204)
        self.assertEqual(self.client.get(path, headers=self.a).status_code, 404)
        self.session(True)
        self.session(False)
        self.assertEqual(self.client.delete("/api/ai/data", headers=self.a).status_code, 204)
        self.assertEqual(self.client.get("/api/ai/sessions", headers=self.a).json()["items"], [])
        self.assertEqual(self.client.get("/api/ai/career-profile", headers=self.a).json()["profile"], empty_profile())
        self.assertEqual(self.client.get("/api/ai/sessions/" + other["id"], headers=self.b).status_code, 200)

    def test_missing_provider_is_explicit(self):
        session = self.session()
        with patch.dict(os.environ, {"AI_DEMO_MODE": "false", "DEEPSEEK_API_KEY": ""}):
            self.assertEqual(self.send(session).status_code, 503)
        self.assertEqual(self.client.post("/api/voice/transcribe", headers=self.a, content=wav_audio()).status_code, 503)

    @patch('advisor.routes.check_ai_rate', lambda *args, **kwargs: None)
    def test_live_request_uses_history_and_private_profile(self):
        seen = []
        async def fake_post(client, url, **kwargs):
            seen.append((url, kwargs["json"]))
            memory = 'bộ nén ngữ cảnh' in kwargs["json"]["messages"][0]["content"]
            content = json.dumps({"profile": {**empty_profile(), "interests": ["vẽ"], "strengths": ["biết chút máy tính"]},
                                  "summary": "Thích vẽ và biết chút máy tính."}) if memory else live_reply()
            return httpx.Response(200, json={"choices": [{"finish_reason": "stop", "message": {"content": content}}]}, request=httpx.Request("POST", url))
        session = self.session(True)
        with patch.dict(os.environ, {"AI_DEMO_MODE": "false", "DEEPSEEK_API_KEY": "fake-test-key", "DEEPSEEK_MODEL": "deepseek-flash",
                                    "DEEPSEEK_BASE_URL": "https://api.deepseek.com"}), patch.object(httpx.AsyncClient, "post", fake_post):
            first = self.send(session, "Mình thích vẽ")
            self.assertEqual(first.status_code, 200, first.text)
            self.assertIn("thiết kế đồ họa", first.json()["session"]["messages"][-1]["content"])
            self.assertEqual(self.send(session, "Mình còn biết một chút máy tính").status_code, 200)
        self.assertEqual(len(seen), 4)
        self.assertEqual(seen[0][0], "https://api.deepseek.com/chat/completions")
        self.assertEqual(seen[0][1]["model"], "deepseek-flash")
        self.assertEqual(seen[0][1]["response_format"]["type"], "text")
        self.assertIn("Mình thích vẽ", [message["content"] for message in seen[2][1]["messages"]])
        self.assertEqual(self.client.get("/api/ai/career-profile", headers=self.a).json()["profile"]["interests"], ["vẽ"])
        self.assertEqual(self.client.get("/api/ai/career-profile", headers=self.b).json()["profile"], empty_profile())

    @patch('advisor.routes.check_ai_rate', lambda *args, **kwargs: None)
    def test_invalid_memory_does_not_discard_good_answer_and_empty_answer_retries(self):
        calls = []
        async def fake_post(client, url, **kwargs):
            calls.append(kwargs["json"])
            content = "" if len(calls) == 1 else "Có thể thử **minh họa số**." if len(calls) == 2 else "{invalid metadata"
            return httpx.Response(200, json={"choices": [{"finish_reason": "stop", "message": {"content": content}}]}, request=httpx.Request("POST", url))
        session = self.session(True)
        with patch.dict(os.environ, {"AI_DEMO_MODE": "false", "DEEPSEEK_API_KEY": "fake-test-key"}), patch.object(httpx.AsyncClient, "post", fake_post):
            result = self.send(session, "Mình thích vẽ")
        self.assertEqual(result.status_code, 200, result.text)
        self.assertEqual(len(calls), 3)
        self.assertIn("minh họa số", result.json()["session"]["messages"][-1]["content"])
        self.assertEqual(len(result.json()["session"]["messages"]), 3)

    @patch('advisor.routes.check_ai_rate', lambda *args, **kwargs: None)
    def test_bad_answer_never_saves_user_message(self):
        async def fake_post(client, url, **kwargs):
            return httpx.Response(200, json={"choices": [{"finish_reason": "stop", "message": {"content": ""}}]}, request=httpx.Request("POST", url))
        session = self.session(True)
        with patch.dict(os.environ, {"AI_DEMO_MODE": "false", "DEEPSEEK_API_KEY": "fake-test-key"}), patch.object(httpx.AsyncClient, "post", fake_post):
            response = self.send(session, "Mình thích vẽ")
        self.assertEqual(response.status_code, 502)
        self.assertNotIn("fake-test-key", response.text)
        self.assertEqual(len(get_store().get("user-a", session["id"])["messages"]), 1)

    @patch('advisor.routes.check_ai_rate', lambda *args, **kwargs: None)
    def test_google_transcription_auth_wav_and_no_automatic_chat_send(self):
        async def fake_transcribe(audio):
            self.assertEqual(audio, wav_audio())
            return "Mình thích vẽ."
        with patch("advisor.voice.google_stt_configured", return_value=True), patch("advisor.voice.transcribe", side_effect=fake_transcribe):
            self.assertEqual(self.client.post("/api/voice/transcribe", content=wav_audio()).status_code, 401)
            self.assertEqual(self.client.post("/api/voice/transcribe", headers=self.a, content=wav_audio(silent=True)).status_code, 422)
            response = self.client.post("/api/voice/transcribe", headers=self.a, content=wav_audio())
            self.assertEqual(response.status_code, 200, response.text)
            self.assertEqual(response.json()["transcript"], "Mình thích vẽ.")
            self.assertEqual(response.json()["provider"], "google")
            self.assertEqual(self.client.post("/api/voice/transcribe", headers=self.a, content=b"x" * 2_000_001).status_code, 413)
        self.assertEqual(self.client.get("/api/ai/sessions", headers=self.a).json()["items"], [])

if __name__ == "__main__":
    unittest.main()
