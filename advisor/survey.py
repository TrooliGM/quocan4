"""Khảo sát theo phiên, dùng metadata JSON hiện có; không cần đổi schema."""
import copy
from uuid import uuid4

from fastapi import HTTPException
from pydantic import BaseModel, ConfigDict, Field, field_validator
from typing import Literal

QUESTIONS = (
    'Em yêu thích lĩnh vực nào?', 'Em thích làm những hoạt động gì?',
    'Em nhận thấy điểm mạnh của mình là gì?',
    'Em mong muốn công việc tương lai như thế nào?', 'Em muốn AI tư vấn điều gì?',
)
ANALYSIS_MESSAGE = 'Hãy phân tích khảo sát của em, gợi ý khoảng 3 nhóm nghề cùng lý do, môn học, kỹ năng và trải nghiệm để thử.'


class SurveyInput(BaseModel):
    model_config = ConfigDict(extra='forbid')
    answers: list[str] = Field(min_length=5, max_length=5)
    address: Literal['anh', 'chị'] = 'chị'

    @field_validator('answers')
    @classmethod
    def validate_answers(cls, answers):
        answers = [value.strip() for value in answers]
        if any(not value or len(value) > 400 for value in answers):
            raise ValueError('Mỗi câu trả lời cần từ 1 đến 400 ký tự.')
        return answers


def survey_data(session):
    return session['messages'][0].get('survey') if session['messages'] else None


def needs_survey(session):
    return bool(session['messages'] and session['messages'][0].get('survey_required') and not survey_data(session))


def apply_survey(session, payload):
    existing = survey_data(session)
    if existing:
        if existing['answers'] != payload.answers or existing['address'] != payload.address:
            raise HTTPException(409, 'Khảo sát của cuộc trò chuyện đã hoàn tất.')
        return session
    if any(m['role'] == 'user' for m in session['messages']):
        raise HTTPException(409, 'Cuộc trò chuyện này đã bắt đầu tư vấn.')
    row = copy.deepcopy(session)
    row['messages'][0]['survey'] = {**payload.model_dump(), 'version': 1, 'analysis_request_id': str(uuid4())}
    return row


def save_survey(store, uid, session_id, payload):
    # PostgreSQL khóa hàng và chỉ sửa messages; không ghi đè title/profile đồng thời.
    from .postgres_adapter import PostgresConversationStore
    if isinstance(store, PostgresConversationStore):
        import json
        from .postgres_store import postgres_connection
        with postgres_connection() as db:
            for table in ('advisor_sessions', 'advisor_temporary_sessions'):
                expiry = ' AND expires_at > NOW()' if table == 'advisor_temporary_sessions' else ''
                row = db.execute(f'SELECT messages FROM {table} WHERE id=%s AND owner=%s{expiry} FOR UPDATE',
                                 (session_id, uid)).fetchone()
                if row:
                    session = {'messages': json.loads(row['messages'])}
                    updated = apply_survey(session, payload)
                    db.execute(f'UPDATE {table} SET messages=%s WHERE id=%s AND owner=%s',
                               (json.dumps(updated['messages'], ensure_ascii=False), session_id, uid))
                    break
            else:
                raise HTTPException(404, 'Không tìm thấy cuộc trò chuyện của em.')
        return store.get(uid, session_id)
    with store.lock:
        row = store.get(uid, session_id)
        return store.write(uid, apply_survey(row, payload))
