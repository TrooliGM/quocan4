"""Thử chat DeepSeek thật bằng hội thoại mẫu, không dùng dữ liệu/tài khoản học sinh.

Chạy chủ động: python scripts/check_chat_quality.py (có dùng quota API).
Firebase được thay trong tiến trình kiểm thử; lời gọi DeepSeek đi qua API chat và graph thật.
Phiên ở RAM, SQLite tạm. Kết quả mẫu lưu trong artifacts/chat-quality.json, không đưa lên Git.
"""
import json
import os
from pathlib import Path
import re
import sys
import tempfile
import time
from unittest.mock import patch
from uuid import uuid4

from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

CASES = [
    ("drawing", "Mình thích vẽ."),
    ("add_computers", "Mình còn biết một chút về máy tính nữa."),
    ("eight_careers", "tôi có sở thích vẽ bạn có thể cho tôi 1-8 ngành liên quan đến vẽ không"),
    ("follow_second", "Giải thích kỹ hơn nghề thứ hai trong danh sách vừa rồi, không cần liệt kê thêm nghề khác."),
    ("correct_fact", "Mình đính chính: mình chưa biết dùng máy tính, mình chỉ vẽ trên giấy."),
    ("two_careers", "Vậy cho mình đúng 2 nghề để thử và một việc nhỏ cuối tuần này."),
]


def run():
    load_dotenv(ROOT / ".env", override=True)
    if not os.getenv("DEEPSEEK_API_KEY", "").strip() or os.getenv("AI_DEMO_MODE", "false").lower() == "true":
        raise SystemExit("Cần khóa DeepSeek và AI_DEMO_MODE=false để kiểm tra thật.")
    from fastapi.testclient import TestClient
    from app import app
    from advisor.routes import require_user
    from advisor.store import get_store

    outputs = []
    old_override = app.dependency_overrides.get(require_user)
    app.dependency_overrides[require_user] = lambda: {"uid": "quality-check-synthetic"}
    try:
        with tempfile.TemporaryDirectory(prefix="laban-chat-check-") as directory, patch.dict(os.environ, {
            "DATABASE_URL": "sqlite:///" + str(Path(directory) / "check.sqlite3")
        }), TestClient(app) as client:
            session = client.post("/api/ai/sessions", json={"remember": False}).json()["session"]
            for name, question in CASES:
                start = time.monotonic()
                response = client.post("/api/ai/chat", json={"session_id": session["id"],
                    "request_id": str(uuid4()), "message": question})
                report = {"case": name, "status": response.status_code, "seconds": round(time.monotonic() - start, 1)}
                if response.is_success:
                    session = response.json()["session"]
                    reply = session["messages"][-1]
                    report.update(mode=reply.get("mode"), answer_characters=len(reply["content"]),
                        listed_careers=len(reply.get("recommendations", [])) or len(re.findall(r"^\s*\d+[.)]\s", reply["content"], re.M)))
                    outputs.append({**report, "question": question, "answer": reply["content"],
                                    "recommendations": reply.get("recommendations", []), "profile": session["profile"]})
                else:
                    outputs.append({**report, "question": question})
                # Không in khóa, token, phản hồi lỗi thô hoặc dữ liệu người dùng.
                print(json.dumps(report, ensure_ascii=True), flush=True)
                if not response.is_success:
                    break
            get_store().delete_all("quality-check-synthetic")
    finally:
        if old_override is None:
            app.dependency_overrides.pop(require_user, None)
        else:
            app.dependency_overrides[require_user] = old_override
    (ROOT / "artifacts").mkdir(exist_ok=True)
    (ROOT / "artifacts" / "chat-quality.json").write_text(json.dumps(outputs, ensure_ascii=False, indent=2), encoding="utf-8")
    if len(outputs) != len(CASES) or any(item["status"] != 200 or item.get("mode") != "live" for item in outputs):
        raise SystemExit(1)
    # Số lượng và chất lượng ngữ cảnh vẫn cần đọc lại câu trả lời mẫu.


if __name__ == "__main__":
    run()
