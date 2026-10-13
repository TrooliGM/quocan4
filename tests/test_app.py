import os
import unittest
from unittest.mock import patch

from fastapi.testclient import TestClient
from app import app


class HomepageTests(unittest.TestCase):
    def setUp(self):
        self.client = TestClient(app)

    def test_home_and_assets(self):
        response = self.client.get("/")
        self.assertEqual(response.status_code, 200)
        self.assertIn("Tương lai của bạn", response.text)
        for path in ["/assets/style.css", "/assets/app.js", "/assets/compass.svg"]:
            self.assertEqual(self.client.get(path).status_code, 200)

    def test_vietnamese_search_and_category(self):
        for query in ["bac si", "BÁC SĨ"]:
            self.assertEqual(self.client.get("/api/careers", params={"q": query}).json()["items"][0]["id"], "bac-si")
        items = self.client.get("/api/careers", params={"category": "Sáng tạo"}).json()["items"]
        self.assertEqual(len(items), 2)
        self.assertEqual(self.client.get("/api/careers?q=khongtimthay").json()["items"], [])

    def test_articles_have_full_content(self):
        items = self.client.get("/api/articles").json()["items"]
        self.assertEqual(len(items), 3)
        self.assertTrue(all(a["body"] for a in items))

    def test_ai_configuration_and_validation(self):
        with patch.dict(os.environ, {"DEEPSEEK_API_KEY": ""}):
            self.assertFalse(self.client.get("/api/health").json()["ai_configured"])
            self.assertEqual(self.client.post("/api/advice", json={"question": "Em thích vẽ"}).status_code, 503)
        for q in ["  ", "hi", "a" * 601]:
            self.assertEqual(self.client.post("/api/advice", json={"question": q}).status_code, 422)


if __name__ == "__main__":
    unittest.main()
