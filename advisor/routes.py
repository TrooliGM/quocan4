import asyncio
import os
import logging
import weakref
from uuid import UUID

import httpx
import google.auth.exceptions
from fastapi import APIRouter, Depends, Header, HTTPException, Request, Response
from pydantic import BaseModel, ConfigDict, Field, field_validator

from firebase_auth import verify_user
from .graph import advisor_graph, demo_mode
from .store import get_store
from . import voice

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
            "model": "demo" if demo_mode() else os.getenv("DEEPSEEK_MODEL", "deepseek-flash"),
            "microphone": {"google": voice.google_stt_configured()}}


@router.post("/api/ai/sessions", status_code=201)
def create_session(payload: SessionInput, user=Depends(require_user)):
    return {"session": get_store().create(user["uid"], payload.remember)}


@router.get("/api/ai/sessions")
def list_sessions(user=Depends(require_user)):
    return {"items": get_store().list(user["uid"])}


@router.get("/api/ai/sessions/{session_id}")
def session(session_id: UUID, user=Depends(require_user)):
    return {"session": get_store().get(user["uid"], str(session_id))}


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


@router.post("/api/ai/chat")
async def chat(payload: ChatInput, user=Depends(require_user)):
    session_id, request_id = str(payload.session_id), str(payload.request_id)
    uid = user["uid"]
    # Quyền sở hữu được kiểm tra trước khi chiếm slot hoặc gọi dịch vụ trả phí.
    get_store().get(uid, session_id)
    try:
        async with asyncio.timeout(90):
            async with lock_for(session_id):
                current = get_store().get(uid, session_id)
                for item in current["messages"]:
                    if item.get("request_id") == request_id and item["role"] == "user":
                        if item["content"] != payload.message:
                            raise HTTPException(409, "Mã tin nhắn đã được sử dụng cho nội dung khác.")
                        return {"session": current, "duplicate": True}
                if len(current["messages"]) >= 501:
                    raise HTTPException(409, "Phiên đã dài. Bạn hãy tạo cuộc trò chuyện mới nhé.")
                if not demo_mode() and not os.getenv("DEEPSEEK_API_KEY", "").strip():
                    raise HTTPException(503, "Chưa có khóa DeepSeek. Nhóm dự án cần cấu hình trước khi tư vấn thật.")
                async with slots:
                    result = await advisor_graph.ainvoke({"uid": uid, "session_id": session_id,
                                                         "request_id": request_id, "message": payload.message})
                return {"session": result["session"], "duplicate": False}
    except (TimeoutError, httpx.TimeoutException):
        raise HTTPException(504, "La Bàn phản hồi hơi lâu. Bạn có thể bấm Thử gửi lại.") from None
    except httpx.HTTPStatusError as error:
        status = error.response.status_code
        logger.warning("advisor_provider_failed status=%d", status)
        if status == 429 or status >= 500:
            raise HTTPException(503, "Dịch vụ AI đang bận. Bạn đợi một chút rồi bấm Thử gửi lại nhé.") from None
        if status in (401, 402, 403):
            raise HTTPException(503, "Kết nối DeepSeek cần được kiểm tra lại cấu hình hoặc hạn mức tài khoản.") from None
        raise HTTPException(502, "Chưa kết nối được dịch vụ AI. Bạn thử gửi lại nhé.") from None
    except httpx.HTTPError:
        logger.warning("advisor_provider_failed reason=connection_error")
        raise HTTPException(502, "Kết nối đến AI bị gián đoạn. Tin nhắn vẫn còn để bạn thử gửi lại.") from None
    except (ValueError, KeyError, IndexError, TypeError, RuntimeError) as error:
        logger.warning("advisor_reply_failed type=%s", type(error).__name__)
        raise HTTPException(502, "Chưa nhận được câu trả lời hợp lệ từ AI. Tin nhắn chưa được lưu; bạn thử lại nhé.") from None


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
