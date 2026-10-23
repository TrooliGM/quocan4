import asyncio
import os
import logging
import weakref
from uuid import UUID
from typing import Literal

import httpx
import psycopg
import google.auth.exceptions
from fastapi import APIRouter, Depends, Header, HTTPException, Request, Response
from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

from career_library import find_career
from firebase_auth import verify_user
from deepseek_client import provider_http_error, ProviderConfigurationError, model_name
from .graph import advisor_graph, demo_mode
from .survey import SurveyInput, save_survey, needs_survey
from .store import get_store
from . import voice
from .postgres_adapter import PostgresConversationStore
from .guest_quota import (reserve_guest_request, finish_guest_request, get_guest_usage,
                          check_chat_rate, claim_guest_history)

logger = logging.getLogger(__name__)
router = APIRouter()
slots = asyncio.Semaphore(4)
voice_slots = asyncio.Semaphore(3)
session_locks = weakref.WeakValueDictionary()


def require_user(authorization: str | None = Header(default=None)):
    parts = authorization.split() if authorization else []
    if len(parts) != 2 or parts[0].lower() != "bearer" or len(parts[1]) > 12000:
        raise HTTPException(401, "Bạn cần đăng nhập để trò chuyện.", headers={"WWW-Authenticate": "Bearer"})
    return verify_user(parts[1])


def lock_for(session_id):
    lock = session_locks.get(session_id)
    if lock is None:
        lock = asyncio.Lock()
        session_locks[session_id] = lock
    return lock


class SessionInput(BaseModel):
    model_config = ConfigDict(extra="forbid")
    remember: bool = False
    mode: Literal['career_discovery','career_exploration'] = 'career_discovery'
    career_id: str | None = Field(default=None,max_length=80)

    @model_validator(mode='after')
    def valid_context(self):
        from career_library import find_career
        if self.mode == 'career_exploration':
            if not self.career_id or not find_career(self.career_id):
                raise ValueError('Nghề được chọn không hợp lệ')
        elif self.career_id is not None:
            raise ValueError('Discovery không nhận nghề cố định')
        return self


class RenameInput(BaseModel):
    title: str = Field(min_length=1, max_length=80)

    @field_validator("title", mode="before")
    @classmethod
    def strip_title(cls, value):
        return value.strip() if isinstance(value, str) else value


class ChatInput(BaseModel):
    model_config = ConfigDict(extra="forbid")
    session_id: UUID
    request_id: UUID
    message: str = Field(min_length=1, max_length=2000)

    @field_validator("message", mode="before")
    @classmethod
    def strip_message(cls, value):
        return value.strip() if isinstance(value, str) else value


@router.get("/api/ai/config")
def config(user=Depends(require_user)):
    return {"mode": "demo" if demo_mode() else "live", "configured": demo_mode() or bool(os.getenv("DEEPSEEK_API_KEY", "").strip()),
            "model": "demo" if demo_mode() else model_name(),
            "microphone": {"google": voice.google_stt_configured()},
            "is_guest": user.get('provider') == 'anonymous',
            "guest_quota": guest_usage(user)}


def guest_usage(user):
    if user.get('provider') != 'anonymous':
        return None
    if not isinstance(get_store(), PostgresConversationStore):
        raise HTTPException(503, 'Chế độ khách cần PostgreSQL và migration quota. Bạn vẫn có thể đăng nhập để dùng bản local.')
    return get_guest_usage(user['uid'])


class GuestClaimInput(BaseModel):
    model_config = ConfigDict(extra='forbid')
    guest_id_token: str = Field(min_length=20, max_length=12000, repr=False)


@router.post('/api/ai/guest/claim')
def claim_guest(payload: GuestClaimInput, user=Depends(require_user)):
    if user.get('provider') not in ('password', 'google.com'):
        raise HTTPException(403, 'Đăng nhập Google hoặc email trước khi giữ lịch sử khách.')
    source = verify_user(payload.guest_id_token)
    if source.get('provider') != 'anonymous':
        raise HTTPException(403, 'Chỉ chuyển lịch sử từ phiên khách đã được xác thực.')
    if not isinstance(get_store(), PostgresConversationStore):
        raise HTTPException(503, 'Chuyển lịch sử khách cần PostgreSQL.')
    return claim_guest_history(source['uid'], user['uid'])


@router.post("/api/ai/sessions", status_code=201)
def create_session(payload: SessionInput, user=Depends(require_user)):
    guest_usage(user)  # Chặn UID khách đã được chuyển sang tài khoản khác.
    return {"session": get_store().create(user["uid"], payload.remember, {"mode":payload.mode,"career_id":payload.career_id,"career_name": find_career(payload.career_id).name if payload.career_id else None})}


@router.get("/api/ai/sessions")
def list_sessions(user=Depends(require_user)):
    return {"items": get_store().list(user["uid"])}


@router.get("/api/ai/sessions/{session_id}")
def session(session_id: UUID, user=Depends(require_user)):
    return {"session": get_store().get(user["uid"], str(session_id))}


@router.put("/api/ai/sessions/{session_id}/survey")
async def submit_survey(session_id: UUID, payload: SurveyInput, user=Depends(require_user)):
    async with lock_for(str(session_id)):
        return {"session": await asyncio.to_thread(save_survey, get_store(), user['uid'], str(session_id), payload)}


@router.patch("/api/ai/sessions/{session_id}")
def rename_session(session_id: UUID, payload: RenameInput, user=Depends(require_user)):
    return {"session": get_store().rename(user["uid"], str(session_id), payload.title)}


@router.delete("/api/ai/sessions/{session_id}", status_code=204)
def delete_session(session_id: UUID, user=Depends(require_user)):
    get_store().delete(user["uid"], str(session_id))
    return Response(status_code=204)


@router.get("/api/ai/career-profile")
def profile(user=Depends(require_user)):
    return {"profile": get_store().profile(user["uid"])}


@router.delete("/api/ai/data", status_code=204)
def delete_data(user=Depends(require_user)):
    get_store().delete_all(user["uid"])
    return Response(status_code=204)


def completed_answer(session, request_id, message):
    previous = next((m for m in session["messages"] if m.get("request_id") == request_id and m["role"] == "user"), None)
    if previous and previous["content"] != message:
        raise HTTPException(409, "Mã tin nhắn đã được sử dụng cho nội dung khác.")
    return previous and any(m.get("request_id") == request_id and m["role"] == "assistant" for m in session["messages"])


@router.post("/api/ai/chat")
async def chat(payload: ChatInput, user=Depends(require_user)):
    session_id, request_id = str(payload.session_id), str(payload.request_id)
    uid = user["uid"]
    is_guest = user.get("provider") == "anonymous"
    store = get_store()
    reservation = None
    store.get(uid, session_id)  # Ownership before rate/quota/provider calls.
    try:
        async with asyncio.timeout(90):
            async with lock_for(session_id):
                current = store.get(uid, session_id)
                if needs_survey(current):
                    raise HTTPException(409, "Em hãy hoàn thành khảo sát trước khi tư vấn nhé.")
                if completed_answer(current, request_id, payload.message):
                    return {"session": current, "duplicate": True, "guest_quota": guest_usage(user)}
                if len(current["messages"]) >= 501:
                    raise HTTPException(409, "Phiên đã dài. Bạn hãy tạo cuộc trò chuyện mới nhé.")
                if not demo_mode() and not os.getenv("DEEPSEEK_API_KEY", "").strip():
                    raise HTTPException(503, "Chưa có khóa DeepSeek. Nhóm dự án cần cấu hình trước khi tư vấn thật.")
                async with slots:
                    if isinstance(store, PostgresConversationStore):
                        await asyncio.to_thread(check_chat_rate, uid)
                    if is_guest:
                        if not isinstance(store, PostgresConversationStore):
                            raise HTTPException(503, "Chế độ khách cần PostgreSQL và migration quota.")
                        reservation = await asyncio.to_thread(reserve_guest_request, uid, session_id, request_id, payload.message)
                        if not reservation["new_reservation"]:
                            current = store.get(uid, session_id)
                            if completed_answer(current, request_id, payload.message):
                                return {"session": current, "duplicate": True, "guest_quota": guest_usage(user)}
                            raise HTTPException(409, {"code": "GUEST_REQUEST_PENDING" if reservation['status'] == 'reserved' else "GUEST_REQUEST_COMPLETED",
                                "message": "Yêu cầu này đang xử lý hoặc đã hoàn thành. Hãy tải lại cuộc trò chuyện trước khi thử gửi lại."})
                    state = {"uid": uid, "session_id": session_id, "request_id": request_id, "message": payload.message}
                    if reservation and reservation['new_reservation']:
                        state['guest_reservation_token'] = reservation['reservation_token']
                    result = await advisor_graph.ainvoke(state)
                return {"session": result["session"], "duplicate": False, "guest_quota": guest_usage(user)}
    except BaseException as error:
        # Lỗi sau COMMIT có thể xảy ra do mạng/response/graph. Đọc lại trước khi
        # hoàn lượt; câu trả lời và status completed đã được commit nguyên tử.
        if reservation and reservation.get('new_reservation'):
            try:
                await asyncio.shield(asyncio.to_thread(finish_guest_request, uid, request_id, False, reservation['reservation_token']))
                current = store.get(uid, session_id)
                if completed_answer(current, request_id, payload.message):
                    if isinstance(error, asyncio.CancelledError):
                        raise error
                    return {"session": current, "duplicate": True, "guest_quota": guest_usage(user)}
            except asyncio.CancelledError:
                raise
            except Exception as settlement_error:
                # Không đoán kết quả COMMIT khi database không truy cập được.
                # Lease sẽ phục hồi bằng transaction sau; không in DSN/token.
                logger.warning('guest_settlement_unavailable type=%s', type(settlement_error).__name__)
        if isinstance(error, (HTTPException, asyncio.CancelledError)):
            raise
        if isinstance(error, psycopg.Error):
            raise  # Handler chung phân biệt kết nối, quyền và schema, không lộ DSN.
        if isinstance(error, (TimeoutError, httpx.HTTPError, ProviderConfigurationError)):
            raise provider_http_error(error) from None
        if isinstance(error, (httpx.HTTPError, ValueError, KeyError, IndexError, TypeError, RuntimeError)):
            logger.warning('advisor_reply_failed type=%s', type(error).__name__)
            raise HTTPException(502, "Chưa xác nhận được câu trả lời. Bạn thử gửi lại cùng tin nhắn nhé.") from None
        raise


@router.post("/api/voice/transcribe")
async def transcribe(request: Request, user=Depends(require_user)):
    if not voice.google_stt_configured():
        raise HTTPException(503, "Google Speech-to-Text chưa được cấu hình. Bạn có thể gõ hoặc dùng mic trình duyệt nếu có hỗ trợ.")
    audio = bytearray()
    async for chunk in request.stream():
        audio.extend(chunk)
        if len(audio) > 2_000_000:
            raise HTTPException(413, "Bản ghi quá dài. Bạn hãy nói dưới 55 giây mỗi lượt.")
    try:
        voice.check_wav(audio)
    except ValueError:
        raise HTTPException(422, "Mic chưa ghi được lời nói hợp lệ. Bạn thử nói rõ trong tối đa 55 giây.") from None
    try:
        async with asyncio.timeout(40):
            async with voice_slots:
                transcript = await voice.transcribe(bytes(audio))
        if not transcript:
            raise HTTPException(422, "Chưa nhận ra lời nói. Bạn thử lại hoặc gõ câu hỏi nhé.")
        return {"transcript": transcript, "provider": "google", "language": "vi-VN"}
    except (TimeoutError, httpx.TimeoutException):
        raise HTTPException(504, "Nhận diện hơi lâu. Bạn thử lại hoặc gõ câu hỏi nhé.") from None
    except (google.auth.exceptions.GoogleAuthError, httpx.HTTPError, ValueError, KeyError, IndexError):
        logger.warning("google_speech_failed")
        raise HTTPException(502, "Google Speech chưa nhận diện được. Bạn vẫn có thể gõ câu hỏi.") from None
