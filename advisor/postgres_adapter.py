

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
        import json
        with postgres_store.postgres_connection() as db:
            row=db.execute('''SELECT id,title,created_at,updated_at,messages,profile,summary,TRUE AS remember
                FROM advisor_sessions WHERE id=%s AND owner=%s
                UNION ALL SELECT id,title,created_at,updated_at,messages,profile,summary,FALSE AS remember
                FROM advisor_temporary_sessions WHERE id=%s AND owner=%s AND expires_at>NOW()
                ORDER BY remember DESC LIMIT 1''',(session_id,uid,session_id,uid)).fetchone()
        if row is None:raise HTTPException(404,'Không tìm thấy cuộc trò chuyện hoặc phiên đã hết hạn.')
        row=dict(row);row['messages']=json.loads(row['messages']);row['profile']=json.loads(row['profile'])
        return row

    def list(self, uid):
        with postgres_store.postgres_connection() as db:
            return [dict(row) for row in db.execute('''SELECT id,title,created_at,updated_at,TRUE AS remember
                FROM advisor_sessions WHERE owner=%s
                UNION ALL SELECT id,title,created_at,updated_at,FALSE AS remember
                FROM advisor_temporary_sessions WHERE owner=%s AND expires_at>NOW()
                ORDER BY updated_at DESC''',(uid,uid)).fetchall()]

    def create(self, uid, remember, context=None):
        with postgres_store.postgres_connection() as db:
            db.execute("SELECT pg_advisory_xact_lock(hashtextextended(%s,0))",('conversation-create:'+uid,))
            count=db.execute('''SELECT (SELECT COUNT(*) FROM advisor_sessions WHERE owner=%s)
                +(SELECT COUNT(*) FROM advisor_temporary_sessions WHERE owner=%s AND expires_at>NOW()) AS total''',(uid,uid)).fetchone()['total']
            if count>=100:raise HTTPException(409,'Bạn đã có 100 cuộc trò chuyện. Hãy xóa bớt nhé.')
            return (create_postgres_session if remember else create_temporary_session)(uid,context,connection=db)

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
            import json
            from .titles import mark_manual
            locked=db.execute(f'SELECT messages FROM {table} WHERE id=%s AND owner=%s FOR UPDATE',(session_id,uid)).fetchone()
            if not locked:
                raise HTTPException(404,'Không tìm thấy cuộc trò chuyện của bạn.')
            messages=json.loads(locked['messages'])
            mark_manual(messages)
            db.execute(f'UPDATE {table} SET title=%s,messages=%s WHERE id=%s AND owner=%s', (title,json.dumps(messages,ensure_ascii=False), session_id, uid))
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
            from .confirmed_profile import enabled,owner_lock
            from .rollout import uid_allowed
            if enabled() and uid_allowed(uid):
                owner_lock(db,uid)
                db.execute('DELETE FROM advisor_profile_items WHERE owner=%s',(uid,))
            db.execute(
                "DELETE FROM advisor_sessions WHERE owner = %s",
                (uid,),
            )
            db.execute(
                "DELETE FROM advisor_temporary_sessions WHERE owner = %s",
                (uid,),
            )
