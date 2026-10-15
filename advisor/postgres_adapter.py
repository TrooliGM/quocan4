

"""Adapter PostgreSQL cho ConversationStore."""

import threading
from fastapi import HTTPException
from advisor import postgres_store
from advisor.postgres_store import (

    get_postgres_session,
    list_postgres_sessions,
    create_postgres_session,
    update_postgres_session,
    get_postgres_profile,
    delete_postgres_session,
    create_temporary_session,
    get_temporary_session,
    update_temporary_session,
    list_temporary_sessions,
    delete_temporary_session,
)


class PostgresConversationStore:
    def __init__(self):
        self.lock = threading.RLock()

    def get(self, uid, session_id):
        try:
            return get_postgres_session(uid, session_id)
        except HTTPException as error:
            if error.status_code != 404:
                raise

        return get_temporary_session(uid, session_id)

    def list(self, uid):
        saved = list_postgres_sessions(uid)
        temporary = list_temporary_sessions(uid)

        return sorted(
            saved + temporary,
            key=lambda row: row["updated_at"],
            reverse=True,
        )

    def create(self, uid, remember):
        if len(self.list(uid)) >= 100:
            raise HTTPException(
                status_code=409,
                detail="Bạn đã có 100 cuộc trò chuyện. Hãy xóa bớt nhé.",
            )

        if remember:
            return create_postgres_session(uid)

        return create_temporary_session(uid)

    def write(self, uid, row):
        current = self.get(uid, row["id"])

        if current["remember"]:
            return update_postgres_session(uid, row)

        return update_temporary_session(uid, row)

    def rename(self, uid, session_id, title):
        row = self.get(uid, session_id)
        table = 'advisor_sessions' if row['remember'] else 'advisor_temporary_sessions'
        # Chỉ đổi title, tránh ghi đè messages vừa được chat commit đồng thời.
        with postgres_store.postgres_connection() as db:
            db.execute(f'UPDATE {table} SET title=%s WHERE id=%s AND owner=%s', (title, session_id, uid))
        return self.get(uid, session_id)

    def delete(self, uid, session_id):
        row = self.get(uid, session_id)

        if row["remember"]:
            return delete_postgres_session(uid, session_id)

        return delete_temporary_session(uid, session_id)

    def profile(self, uid):
        return get_postgres_profile(uid)

    def delete_all(self, uid):
        with postgres_store.postgres_connection() as db:
            db.execute(
                "DELETE FROM advisor_sessions WHERE owner = %s",
                (uid,),
            )
            db.execute(
                "DELETE FROM advisor_temporary_sessions WHERE owner = %s",
                (uid,),
            )
