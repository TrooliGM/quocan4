"""SQLite cho lịch sử có đồng ý; bộ nhớ RAM cho phiên không lưu.

Không chứa audio, token hoặc khóa API. Mọi truy vấn đều nhận UID đã xác thực.
"""
import copy
import json
import os
import sqlite3
import threading
import time
from contextlib import contextmanager
from datetime import datetime, timezone
from functools import lru_cache
from pathlib import Path
from uuid import uuid4

from fastapi import HTTPException

GREETING = "Chào bạn, mình là La Bàn. Bạn có thể kể về một sở thích, hỏi về một nghề, hoặc nói điều đang băn khoăn. Mình sẽ cùng bạn tìm hiểu từng chút một."
PROFILE_KEYS = ("interests", "strengths", "growth_skills", "careers")


class StorageConfigurationError(RuntimeError):
    """Lỗi cấu hình an toàn; không chứa URL hoặc credentials database."""


def empty_profile():
    return {key: [] for key in PROFILE_KEYS}


def now():
    return datetime.now(timezone.utc).isoformat()


class ConversationStore:
    def __init__(self, database_url):
        if not database_url.startswith("sqlite:///"):
            raise RuntimeError("DATABASE_URL hiện hỗ trợ sqlite:///; cần adapter cho cơ sở dữ liệu khác.")
        self.path = Path(database_url.removeprefix("sqlite:///"))
        self.lock = threading.RLock()
        self.temporary = {}
        self.initialized = False

    @contextmanager
    def connect(self):
        self.path.parent.mkdir(parents=True, exist_ok=True)
        db = sqlite3.connect(self.path, timeout=5)
        db.row_factory = sqlite3.Row
        try:
            if not self.initialized:
                db.execute("""CREATE TABLE IF NOT EXISTS advisor_sessions (
                    id TEXT PRIMARY KEY, owner TEXT NOT NULL, title TEXT NOT NULL,
                    created_at TEXT NOT NULL, updated_at TEXT NOT NULL,
                    messages TEXT NOT NULL, profile TEXT NOT NULL, summary TEXT NOT NULL)""")
                db.execute("CREATE INDEX IF NOT EXISTS advisor_owner ON advisor_sessions(owner, updated_at)")
                db.execute("PRAGMA user_version=1")
                db.commit()
                self.initialized = True
            with db:
                yield db
        finally:
            db.close()

    def prune(self):
        deadline = time.monotonic() - 7200
        for key in [key for key, row in self.temporary.items() if row["touched"] < deadline]:
            del self.temporary[key]

    @staticmethod
    def decode(row):
        data = dict(row)
        for key in ("messages", "profile"):
            data[key] = json.loads(data[key])
        data["remember"] = True
        return data

    @staticmethod
    def public(row):
        return {key: copy.deepcopy(row[key]) for key in
                ("id", "title", "created_at", "updated_at", "remember", "messages", "profile", "summary")}

    def get(self, uid, session_id):
        with self.lock:
            self.prune()
            row = self.temporary.get(session_id)
            if row and row["owner"] == uid:
                row["touched"] = time.monotonic()
                return self.public(row)
            with self.connect() as db:
                row = db.execute("SELECT * FROM advisor_sessions WHERE id=? AND owner=?", (session_id, uid)).fetchone()
            if row is None:
                raise HTTPException(404, "Không tìm thấy cuộc trò chuyện của bạn.")
            return self.public(self.decode(row))

    def list(self, uid):
        with self.lock:
            self.prune()
            with self.connect() as db:
                rows = [{**dict(row), "remember": True} for row in db.execute(
                    "SELECT id, title, created_at, updated_at FROM advisor_sessions WHERE owner=? ORDER BY updated_at DESC", (uid,)).fetchall()]
            rows += [row for row in self.temporary.values() if row["owner"] == uid]
            return [{key: row[key] for key in ("id", "title", "created_at", "updated_at", "remember")}
                    for row in sorted(rows, key=lambda row: row["updated_at"], reverse=True)]

    def create(self, uid, remember, context=None):
        with self.lock:
            if len(self.list(uid)) >= 100:
                raise HTTPException(409, "Bạn đã có 100 cuộc trò chuyện. Hãy xóa bớt lịch sử trước nhé.")
            row = {"id": str(uuid4()), "owner": uid, "title": "Một hướng đi mới", "remember": remember,
                   "created_at": now(), "updated_at": now(), "messages": [
                       {"id": str(uuid4()), "role": "assistant", "content": GREETING, "survey_required": True, "career_context": context or {"mode":"career_discovery","career_id":None}}],
                   "profile": empty_profile(), "summary": ""}
            if remember:
                with self.connect() as db:
                    db.execute("INSERT INTO advisor_sessions VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
                               (row["id"], uid, row["title"], row["created_at"], row["updated_at"],
                                json.dumps(row["messages"], ensure_ascii=False), json.dumps(row["profile"]), ""))
            else:
                row["touched"] = time.monotonic()
                self.temporary[row["id"]] = row
            return self.public(row)

    def write(self, uid, row):
        with self.lock:
            current = self.get(uid, row["id"])
            row["updated_at"] = now()
            if current["remember"]:
                with self.connect() as db:
                    db.execute("UPDATE advisor_sessions SET title=?, updated_at=?, messages=?, profile=?, summary=? WHERE id=? AND owner=?",
                               (row["title"], row["updated_at"], json.dumps(row["messages"], ensure_ascii=False),
                                json.dumps(row["profile"], ensure_ascii=False), row["summary"], row["id"], uid))
            else:
                self.temporary[row["id"]] = {**copy.deepcopy(row), "owner": uid, "touched": time.monotonic()}
            return self.public(row)

    def rename(self, uid, session_id, title):
        with self.lock:
            row = self.get(uid, session_id)
            row["title"] = title
            from .titles import mark_manual
            mark_manual(row['messages'])
            return self.write(uid, row)

    def delete(self, uid, session_id):
        with self.lock:
            row = self.get(uid, session_id)
            if row["remember"]:
                with self.connect() as db:
                    db.execute("DELETE FROM advisor_sessions WHERE id=? AND owner=?", (session_id, uid))
            else:
                self.temporary.pop(session_id, None)

    def profile(self, uid):
        with self.lock:
            with self.connect() as db:
                rows = db.execute("SELECT profile FROM advisor_sessions WHERE owner=? ORDER BY updated_at DESC", (uid,)).fetchall()
            result = empty_profile()
            for row in rows:
                profile = json.loads(row["profile"])
                for key in PROFILE_KEYS:
                    for value in profile.get(key, []):
                        if value not in result[key] and len(result[key]) < 20:
                            result[key].append(value)
            return result

    def delete_all(self, uid):
        with self.lock:
            with self.connect() as db:
                db.execute("DELETE FROM advisor_sessions WHERE owner=?", (uid,))
            for key in [key for key, row in self.temporary.items() if row["owner"] == uid]:
                del self.temporary[key]


@lru_cache(maxsize=4)
def _store(database_url):
    if database_url.startswith(("postgresql://", "postgres://")):
        from advisor.postgres_adapter import PostgresConversationStore
        return PostgresConversationStore()

    if not database_url.startswith('sqlite:///'):
        raise StorageConfigurationError('DATABASE_URL_UNSUPPORTED')
    return ConversationStore(database_url)


def get_store():
    database_url = os.getenv('DATABASE_URL', '').strip()
    if os.getenv('VERCEL') and not database_url.startswith(('postgresql://', 'postgres://')):
        raise StorageConfigurationError('POSTGRES_REQUIRED')
    default = 'sqlite:///' + str(Path(__file__).resolve().parents[1] / 'data' / 'advisor.sqlite3')
    return _store(database_url or default)
