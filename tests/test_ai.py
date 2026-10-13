import os
import unittest
from unittest.mock import patch

import httpx
from fastapi.testclient import TestClient
from app import app
from ai import advice_graph


class GraphTests(unittest.IsolatedAsyncioTestCase):
    async def test_graph_context_and_deepseek_request(self):
        seen = {}

        async def fake_post(client, url, **kwargs):
            seen.update({"url": url, **kwargs})
            return httpx.Response(200, json={"choices": [{"message": {"content": "Thử thiết kế một poster nhé."}}]}, request=httpx.Request("POST", url))

        with patch.dict(os.environ, {"DEEPSEEK_API_KEY": "test-key", "DEEPSEEK_MODEL": "deepseek-chat"}), patch.object(httpx.AsyncClient, "post", fake_post):
            result = await advice_graph.ainvoke({"question": "Em thích vẽ", "context": "", "answer": ""})
        self.assertIn("poster", result["answer"])
        self.assertEqual(seen["url"], "https://api.deepseek.com/chat/completions")
        self.assertIn("Nhà thiết kế", seen["json"]["messages"][0]["content"])
        self.assertEqual(seen["json"]["messages"][1]["content"], "Em thích vẽ")

    async def test_upstream_error_does_not_expose_credentials(self):
        async def fake_post(client, url, **kwargs):
            return httpx.Response(401, json={"error": "sensitive provider details"}, request=httpx.Request("POST", url))

        with patch.dict(os.environ, {"DEEPSEEK_API_KEY": "test-secret"}), patch.object(httpx.AsyncClient, "post", fake_post):
            with TestClient(app) as client:
                response = client.post("/api/advice", json={"question": "Em thích vẽ"})
        self.assertEqual(response.status_code, 502)
        self.assertNotIn("test-secret", response.text)
        self.assertNotIn("sensitive", response.text)
