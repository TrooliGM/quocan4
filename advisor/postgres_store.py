
"""Kết nối PostgreSQL (Neon) cho La Bàn."""

import os
from contextlib import contextmanager

import psycopg
from psycopg.rows import dict_row


@contextmanager
def postgres_connection():
    database_url = os.getenv("DATABASE_URL", "").strip()

    if not database_url.startswith(("postgresql://", "postgres://")):
        raise RuntimeError("DATABASE_URL chưa được cấu hình cho PostgreSQL.")

    with psycopg.connect(
        database_url,
        row_factory=dict_row,
        connect_timeout=10,
    ) as connection:
        yield connection


def initialize_postgres():
    """Tạo bảng lưu lịch sử trò chuyện nếu chưa tồn tại."""

    with postgres_connection() as db:
        db.execute("""
            CREATE TABLE IF NOT EXISTS advisor_sessions (
                id TEXT PRIMARY KEY,
                owner TEXT NOT NULL,
                title TEXT NOT NULL,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL,
                messages TEXT NOT NULL,
                profile TEXT NOT NULL,
                summary TEXT NOT NULL
            )
        """)

        db.execute("""
            CREATE INDEX IF NOT EXISTS advisor_owner
            ON advisor_sessions(owner, updated_at)
        """)

def get_postgres_session(uid, session_id):
    """Đọc một cuộc trò chuyện thuộc đúng người dùng."""
    import json
    from fastapi import HTTPException

    with postgres_connection() as db:
        row = db.execute(
            """
            SELECT id, title, created_at, updated_at,
                   messages, profile, summary
            FROM advisor_sessions
            WHERE id = %s AND owner = %s
            """,
            (session_id, uid),
        ).fetchone()

    if row is None:
        raise HTTPException(
            status_code=404,
            detail="Không tìm thấy cuộc trò chuyện của bạn."
        )

    row["messages"] = json.loads(row["messages"])
    row["profile"] = json.loads(row["profile"])
    row["remember"] = True

    return row

def create_postgres_session(uid):
    """Tạo cuộc trò chuyện mới trên Neon PostgreSQL."""
    import json
    from uuid import uuid4
    from advisor.store import GREETING, empty_profile, now

    session_id = str(uuid4())
    timestamp = now()

    row = {
        "id": session_id,
        "title": "Một hướng đi mới",
        "created_at": timestamp,
        "updated_at": timestamp,
        "messages": [
            {
                "id": str(uuid4()),
                "role": "assistant",
                "content": GREETING,
            }
        ],
        "profile": empty_profile(),
        "summary": "",
        "remember": True,
    }

    with postgres_connection() as db:
        db.execute(
            """
            INSERT INTO advisor_sessions
            (id, owner, title, created_at, updated_at,
             messages, profile, summary)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            """,
            (
                session_id,
                uid,
                row["title"],
                timestamp,
                timestamp,
                json.dumps(row["messages"], ensure_ascii=False),
                json.dumps(row["profile"], ensure_ascii=False),
                "",
            ),
        )

    return row

def save_messages_atomic(uid, session_id, request_id, message, reply, mode, guest_reservation_token=None):
    """Lưu cặp tin nhắn an toàn, chống trùng request_id."""
    import json
    from uuid import uuid4
    from fastapi import HTTPException
    from advisor.store import now

    from .guest_quota import lock_request_for_save, settle_locked
    with postgres_connection() as db:
        guest_request = lock_request_for_save(db, uid, session_id, request_id, message, guest_reservation_token)
        row = db.execute(
            """
            SELECT id, title, created_at, updated_at,
                   messages, profile, summary
            FROM advisor_sessions
            WHERE id = %s AND owner = %s
            FOR UPDATE
            """,
            (session_id, uid),
        ).fetchone()

        remember = row is not None

        if row is None:
            row = db.execute(
                """
                SELECT id, title, created_at, updated_at,
                       messages, profile, summary
                FROM advisor_temporary_sessions
                WHERE id = %s
                  AND owner = %s
                  AND expires_at > NOW()
                FOR UPDATE
                """,
                (session_id, uid),
            ).fetchone()

        if row is None:
            raise HTTPException(
                status_code=404,
                detail="Cuộc trò chuyện không tồn tại hoặc đã hết hạn.",
            )


        messages = json.loads(row["messages"])

        for item in messages:
            if item.get("request_id") == request_id and item.get("role") == "user":
                if item["content"] != message:
                    raise HTTPException(
                        status_code=409,
                        detail="Mã tin nhắn đã được sử dụng cho nội dung khác.",
                    )
                if not any(m.get('request_id') == request_id and m.get('role') == 'assistant' for m in messages):
                    raise HTTPException(409, 'Tin nhắn cũ chưa có câu trả lời; chưa thể xác nhận lượt thành công.')
                row["messages"] = messages
                row["profile"] = json.loads(row["profile"])
                row["remember"] = remember
                if guest_request:
                    settle_locked(db, uid, guest_request, True)
                return row

        if guest_request and guest_request['status'] == 'completed':
            raise HTTPException(409, 'Yêu cầu đã hoàn thành trước đó; không gọi lại AI cho mã này.')

        messages.append({
            "id": str(uuid4()),
            "role": "user",
            "content": message,
            "request_id": request_id,
        })

        messages.append({
            "id": str(uuid4()),
            "role": "assistant",
            "content": reply["answer"],
            "recommendations": reply["recommendations"],
            "request_id": request_id,
            "mode": mode,
            **({"story_navigation": reply["story_navigation"]} if reply.get("story_navigation") else {}),
        })

        title = row["title"]
        if len(messages) == 3 and title == "Một hướng đi mới":
            title = message[:60]

        timestamp = now()

        table = "advisor_sessions" if remember else "advisor_temporary_sessions"

        db.execute(
            f"""
            UPDATE {table}
            SET title = %s,
                updated_at = %s,
                messages = %s,
                profile = %s,
                summary = %s
            WHERE id = %s AND owner = %s
            """,
            (
                title,
                timestamp,
                json.dumps(messages, ensure_ascii=False),
                json.dumps(reply["profile"], ensure_ascii=False),
                reply["summary"],
                session_id,
                uid,
            ),
        )


        row["title"] = title
        if not remember:
            db.execute(
                """
                UPDATE advisor_temporary_sessions
                SET expires_at = NOW() + INTERVAL '2 hours'
                WHERE id = %s AND owner = %s
                  AND expires_at > NOW()
                """,
                (session_id, uid),
            )

        row["updated_at"] = timestamp
        row["messages"] = messages
        row["profile"] = reply["profile"]
        row["summary"] = reply["summary"]
        row["remember"] = remember

        if guest_request:
            # Cùng transaction với UPDATE messages; không có khoảng trống giữa
            # lưu thành công và xác nhận quota.
            settle_locked(db, uid, guest_request, True)

        return row



def update_postgres_session(uid, row):
    """Cập nhật cuộc trò chuyện trên Neon, chỉ với đúng chủ sở hữu."""
    import json
    from fastapi import HTTPException
    from advisor.store import now

    timestamp = now()

    with postgres_connection() as db:
        result = db.execute(
            """
            UPDATE advisor_sessions
            SET title = %s,
                updated_at = %s,
                messages = %s,
                profile = %s,
                summary = %s
            WHERE id = %s AND owner = %s
            """,
            (
                row["title"],
                timestamp,
                json.dumps(row["messages"], ensure_ascii=False),
                json.dumps(row["profile"], ensure_ascii=False),
                row["summary"],
                row["id"],
                uid,
            ),
        )

        if result.rowcount != 1:
            raise HTTPException(
                status_code=404,
                detail="Không tìm thấy cuộc trò chuyện của bạn.",
            )

    row["updated_at"] = timestamp
    row["remember"] = True
    return row

def list_postgres_sessions(uid):
    """Lấy danh sách cuộc trò chuyện của một người dùng."""

    with postgres_connection() as db:
        rows = db.execute(
            """
            SELECT id, title, created_at, updated_at
            FROM advisor_sessions
            WHERE owner = %s
            ORDER BY updated_at DESC
            """,
            (uid,),
        ).fetchall()

    return [
        {**row, "remember": True}
        for row in rows
    ]

def rename_postgres_session(uid, session_id, title):
    """Đổi tên cuộc trò chuyện trên Neon PostgreSQL."""
    from fastapi import HTTPException

    title = title.strip()
    if not title or len(title) > 80:
        raise HTTPException(422, "Tên cuộc trò chuyện không hợp lệ.")

    with postgres_connection() as db:
        row = db.execute(
            """
            UPDATE advisor_sessions
            SET title = %s,
                updated_at = %s
            WHERE id = %s AND owner = %s
            RETURNING id
            """,
            (
                title,
                __import__("datetime").datetime.now(
                    __import__("datetime").timezone.utc
                ).isoformat(),
                session_id,
                uid,
            ),
        ).fetchone()

        if row is None:
            raise HTTPException(
                404,
                "Không tìm thấy cuộc trò chuyện của bạn.",
            )

    return get_postgres_session(uid, session_id)

def delete_postgres_session(uid, session_id):
    """Xóa cuộc trò chuyện thuộc đúng người dùng trên Neon."""
    from fastapi import HTTPException

    with postgres_connection() as db:
        result = db.execute(
            """
            DELETE FROM advisor_sessions
            WHERE id = %s AND owner = %s
            """,
            (session_id, uid),
        )

        if result.rowcount == 0:
            raise HTTPException(
                status_code=404,
                detail="Không tìm thấy cuộc trò chuyện của bạn.",
            )

def get_postgres_profile(uid):
    """Tổng hợp hồ sơ hướng nghiệp từ lịch sử đã lưu."""
    import json
    from advisor.store import PROFILE_KEYS, empty_profile

    result = empty_profile()

    with postgres_connection() as db:
        rows = db.execute(
            """
            SELECT profile
            FROM advisor_sessions
            WHERE owner = %s
            ORDER BY updated_at DESC
            """,
            (uid,),
        ).fetchall()

    for row in rows:
        profile = json.loads(row["profile"])

        for key in PROFILE_KEYS:
            for value in profile.get(key, []):
                if value not in result[key] and len(result[key]) < 20:
                    result[key].append(value)

    return result

def delete_all_postgres_sessions(uid):
    """Xóa toàn bộ lịch sử trò chuyện của một người dùng."""

    with postgres_connection() as db:
        db.execute(
            """
            DELETE FROM advisor_sessions
            WHERE owner = %s
            """,
            (uid,),
        )

def reserve_guest_question(uid):
    """Giữ một lượt hỏi AI, tối đa 8 lượt cho mỗi Firebase UID."""
    from fastapi import HTTPException

    with postgres_connection() as db:
        row = db.execute(
            """
            INSERT INTO guest_ai_usage (uid, used_questions, updated_at)
            VALUES (%s, 1, NOW())
            ON CONFLICT (uid)
            DO UPDATE SET
                used_questions = guest_ai_usage.used_questions + 1,
                updated_at = NOW()
            WHERE guest_ai_usage.used_questions < 8
            RETURNING used_questions
            """,

            (uid,),
        ).fetchone()

    return row["used_questions"] if row else 0

# Public API giu nguyen ten; logic quota/fencing nam trong module rieng.
from .guest_quota import reserve_guest_request, finish_guest_request


def cleanup_expired_sessions():
    """Xóa các cuộc trò chuyện tạm đã hết hạn."""


    with postgres_connection() as db:
        result = db.execute(
            """
            DELETE FROM advisor_temporary_sessions
            WHERE expires_at <= NOW()
            """
        )

        return result.rowcount

def create_temporary_session(uid):
    """Tạo cuộc trò chuyện tạm, hết hạn sau 2 giờ."""
    import json
    from datetime import datetime, timedelta, timezone
    from uuid import uuid4
    from advisor.store import GREETING, empty_profile

    session_id = str(uuid4())
    created_at = datetime.now(timezone.utc)
    expires_at = created_at + timedelta(hours=2)

    row = {
        "id": session_id,
        "owner": uid,
        "title": "Một hướng đi mới",
        "created_at": created_at.isoformat(),
        "updated_at": created_at.isoformat(),
        "remember": False,
        "messages": [
            {
                "id": str(uuid4()),
                "role": "assistant",
                "content": GREETING,
            }
        ],
        "profile": empty_profile(),
        "summary": "",
    }

    with postgres_connection() as db:
        db.execute(
            """
            INSERT INTO advisor_temporary_sessions
            (id, owner, title, created_at, updated_at,
             messages, profile, summary, expires_at)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            """,
            (
                row["id"],
                uid,
                row["title"],
                row["created_at"],
                row["updated_at"],
                json.dumps(row["messages"], ensure_ascii=False),
                json.dumps(row["profile"], ensure_ascii=False),
                row["summary"],
                expires_at,
            ),
        )

    return row

def get_temporary_session(uid, session_id):
    """Đọc phiên tạm còn hạn và xác thực chủ sở hữu."""
    import json
    from fastapi import HTTPException

    with postgres_connection() as db:
        row = db.execute(
            """
            SELECT id, owner, title, created_at, updated_at,
                   messages, profile, summary
            FROM advisor_temporary_sessions
            WHERE id = %s
              AND owner = %s
              AND expires_at > NOW()
            """,
            (session_id, uid),
        ).fetchone()

    if row is None:
        raise HTTPException(
            status_code=404,
            detail="Cuộc trò chuyện không tồn tại hoặc đã hết hạn.",
        )

    result = dict(row)
    result["messages"] = json.loads(result["messages"])
    result["profile"] = json.loads(result["profile"])
    result["remember"] = False

    return result

def update_temporary_session(uid, row):
    """Cập nhật phiên tạm còn hạn và gia hạn thêm 2 giờ."""
    import json
    from fastapi import HTTPException
    from advisor.store import now

    updated_at = now()

    with postgres_connection() as db:
        result = db.execute(
            """
            UPDATE advisor_temporary_sessions
            SET title = %s,
                updated_at = %s,
                messages = %s,
                profile = %s,
                summary = %s,
                expires_at = NOW() + INTERVAL '2 hours'
            WHERE id = %s
              AND owner = %s
              AND expires_at > NOW()
            RETURNING id
            """,
            (
                row["title"],
                updated_at,
                json.dumps(row["messages"], ensure_ascii=False),
                json.dumps(row["profile"], ensure_ascii=False),
                row["summary"],
                row["id"],
                uid,
            ),
        ).fetchone()

    if result is None:
        raise HTTPException(
            status_code=404,
            detail="Cuộc trò chuyện tạm không tồn tại hoặc đã hết hạn.",
        )

    return {
        **row,
        "updated_at": updated_at,
        "remember": False,
    }

def list_temporary_sessions(uid):
    """Liệt kê các cuộc trò chuyện tạm còn hạn của người dùng."""

    with postgres_connection() as db:
        rows = db.execute(
            """
            SELECT id, title, created_at, updated_at
            FROM advisor_temporary_sessions
            WHERE owner = %s
              AND expires_at > NOW()
            ORDER BY updated_at DESC
            """,
            (uid,),
        ).fetchall()

    return [
        {
            **dict(row),
            "remember": False,
        }
        for row in rows
    ]

def delete_temporary_session(uid, session_id):
    """Xóa cuộc trò chuyện tạm của đúng người sở hữu."""
    from fastapi import HTTPException

    with postgres_connection() as db:
        result = db.execute(
            """
            DELETE FROM advisor_temporary_sessions
            WHERE id = %s AND owner = %s
            RETURNING id
            """,
            (session_id, uid),
        ).fetchone()

    if result is None:
        raise HTTPException(
            status_code=404,
            detail="Không tìm thấy cuộc trò chuyện tạm.",
        )
