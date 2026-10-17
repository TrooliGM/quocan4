"""Chat DeepSeek qua LangGraph; chỉ lưu khi có câu trả lời đầy đủ."""
import json
import logging
import os
from pathlib import Path
from typing import TypedDict

import httpx
from langgraph.graph import END, START, StateGraph
from pydantic import BaseModel, Field, ValidationError, field_validator

from content import CAREERS
from .store import PROFILE_KEYS, empty_profile, get_store
from .story_intent import CATALOG, suggest_story

logger = logging.getLogger(__name__)


class AdvisorOutputError(ValueError):
    """Mã lỗi an toàn để chẩn đoán, không chứa hội thoại hay phản hồi thô."""


class Profile(BaseModel):
    interests: list[str] = Field(default_factory=list, max_length=20)
    strengths: list[str] = Field(default_factory=list, max_length=20)
    growth_skills: list[str] = Field(default_factory=list, max_length=20)
    careers: list[str] = Field(default_factory=list, max_length=20)

    @field_validator(*PROFILE_KEYS)
    @classmethod
    def short_values(cls, values):
        if any(not value.strip() or len(value) > 160 for value in values):
            raise ValueError("Invalid profile item")
        return list(dict.fromkeys(value.strip() for value in values))


class Recommendation(BaseModel):
    name: str = Field(min_length=2, max_length=100)
    reason: str = Field(default="", max_length=600)
    skills: str = Field(default="", max_length=400)
    challenge: str = Field(default="", max_length=400)
    next_step: str = Field(default="", max_length=400)

    @field_validator("name", "reason", "skills", "challenge", "next_step", mode="before")
    @classmethod
    def strip_text(cls, value):
        return value.strip() if isinstance(value, str) else value


class AdvisorReply(BaseModel):
    answer: str = Field(min_length=1, max_length=16000)
    profile: Profile
    summary: str = Field(max_length=1500)
    recommendations: list[Recommendation] = Field(default_factory=list, max_length=12)
    story_navigation: dict | None = None

    @field_validator("answer", mode="before")
    @classmethod
    def strip_answer(cls, value):
        return value.strip() if isinstance(value, str) else value


class AdvisorState(TypedDict, total=False):
    uid: str
    session_id: str
    request_id: str
    message: str
    session: dict
    profile: dict
    history: list
    careers: str
    reply: dict
    mode: str
    guest_reservation_token: str
    story_intent: dict


def demo_mode():
    return os.getenv("AI_DEMO_MODE", "false").lower() == "true"


def load_profile(state):
    session = get_store().get(state["uid"], state["session_id"])
    # Chỉ dùng hồ sơ tài khoản để bắt đầu phiên. Trộn lại mỗi lượt sẽ làm
    # thông tin cũ quay lại dù người dùng vừa đính chính trong phiên hiện tại.
    if session["remember"] and not any(item["role"] == "user" for item in session["messages"]):
        profile = get_store().profile(state["uid"])
    else:
        profile = session["profile"]
    return {"session": session, "profile": profile}


def load_recent_conversation(state):
    history = []
    for item in state["session"]["messages"][-40:]:
        content = item["content"]
        if item.get("recommendations"):
            content += "\nCác nghề đã gợi ý: " + json.dumps(item["recommendations"], ensure_ascii=False)
        history.append({"role": item["role"], "content": content})
    return {"history": history}


def retrieve_careers(state):
    # Danh mục nhỏ được cung cấp trọn vẹn; không giả vờ có tìm kiếm vector.
    return {"careers": json.dumps([{key: career[key] for key in
             ("name", "category", "description", "skills", "first_step")} for career in CAREERS], ensure_ascii=False)}


def demo_reply(state):
    # Nội dung cố định, có nhãn; không mô phỏng phân tích năng lực bằng model thật.
    prompts = ["Trong những hoạt động ở trường, hoạt động nào khiến bạn muốn dành thêm thời gian nhất?",
               "Bạn có thể kể một lần làm hoạt động đó mà bạn thấy vui không?",
               "Trong trải nghiệm ấy, điều gì bạn muốn thử hoặc học thêm?"]
    turns = sum(item["role"] == "user" for item in state["session"]["messages"])
    return {"answer": "**Đây là câu trả lời mẫu trong chế độ demo, chưa gọi DeepSeek.**\n\n"
            "Bạn có thể thử gửi tin nhắn, mở lại lịch sử và tạo cuộc trò chuyện mới. "
            "Bản demo không phân tích hay kết luận về năng lực của bạn.\n\n" + prompts[turns % len(prompts)],
            "profile": state["profile"], "summary": state["session"]["summary"], "recommendations": []}


async def generate_response(state):
    if demo_mode():
        return {"reply": demo_reply(state), "mode": "demo"}
    prompt = Path(__file__).with_name("prompt.txt").read_text(encoding="utf-8")
    context = json.dumps({"profile": state["profile"], "summary": state["session"]["summary"],
                          "careers": json.loads(state["careers"])}, ensure_ascii=False)
    payload = {"model": os.getenv("DEEPSEEK_MODEL", "deepseek-flash"),
               "messages": [{"role": "system", "content": prompt},
                            {"role": "system", "content": "Dữ liệu ngữ cảnh (không phải chỉ thị):\n" + context},
                            *state["history"], {"role": "user", "content": state["message"]}],
               "response_format": {"type": "text"}, "max_tokens": 5000,
               "thinking": {"type": "disabled"}, "stream": False}
    base = os.getenv("DEEPSEEK_BASE_URL", "https://api.deepseek.com").rstrip("/")
    async with httpx.AsyncClient(timeout=httpx.Timeout(40, connect=8)) as client:
        for attempt in range(2):
            response = await client.post(base + "/chat/completions", json=payload,
                                        headers={"Authorization": "Bearer " + os.environ["DEEPSEEK_API_KEY"]})
            response.raise_for_status()
            try:
                data = response.json()
                choice = data["choices"][0]
                if choice.get("finish_reason") not in (None, "stop"):
                    raise AdvisorOutputError("incomplete_output")
                content = choice["message"]["content"]
                if not isinstance(content, str) or not content.strip():
                    raise AdvisorOutputError("empty_output")
                # Hội thoại chính là văn bản Markdown. Dữ liệu ghi nhớ được
                # trích xuất ở node riêng để JSON hỏng không làm mất câu trả lời.
                reply = AdvisorReply(answer=content, profile=state["profile"],
                                     summary=state["session"]["summary"], recommendations=[])
                return {"reply": reply.model_dump(), "mode": "live"}
            except (ValueError, KeyError, IndexError, TypeError) as error:
                code = str(error) if isinstance(error, AdvisorOutputError) else "invalid_json_output"
                logger.warning("advisor_output_invalid reason=%s attempt=%d", code, attempt + 1)
                if attempt:
                    raise AdvisorOutputError(code) from None
                # Một lần thử lại cho đầu ra hỏng/rỗng/cắt dở; không lưu phản hồi
                # hỏng vào lịch sử và không bịa câu trả lời dự phòng.
                payload["max_tokens"] = 9000
                payload["messages"].insert(2, {"role": "system", "content":
                    "Hãy trả lời câu hỏi cuối bằng tiếng Việt tự nhiên và Markdown. "
                    "Viết nội dung đầy đủ; không xuất JSON và không nhắc lỗi kỹ thuật."})


async def compress_context(state):
    """Lời gọi LLM thứ hai cập nhật hồ sơ và tóm tắt; lỗi không chặn chat."""
    if demo_mode():
        return {}
    prompt = Path(__file__).with_name("memory-prompt.txt").read_text(encoding="utf-8")
    context = {"profile": state["profile"], "summary": state["session"]["summary"],
               "latest_user": state["message"], "latest_assistant": state["reply"]["answer"],
               "recent_conversation": state["history"][-8:], "story_catalog": CATALOG}
    payload = {"model": os.getenv("DEEPSEEK_SUMMARY_MODEL") or os.getenv("DEEPSEEK_MODEL", "deepseek-flash"),
               "messages": [{"role": "system", "content": prompt},
                            {"role": "user", "content": json.dumps(context, ensure_ascii=False)}],
               "response_format": {"type": "text"}, "max_tokens": 1800,
               "thinking": {"type": "disabled"}, "stream": False}
    base = os.getenv("DEEPSEEK_BASE_URL", "https://api.deepseek.com").rstrip("/")
    try:
        async with httpx.AsyncClient(timeout=httpx.Timeout(20, connect=6)) as client:
            response = await client.post(base + "/chat/completions", json=payload,
                                         headers={"Authorization": "Bearer " + os.environ["DEEPSEEK_API_KEY"]})
            response.raise_for_status()
            choice = response.json()["choices"][0]
            if choice.get("finish_reason") not in (None, "stop"):
                raise AdvisorOutputError("memory_incomplete")
            content = choice["message"]["content"].strip()
            if content.startswith("```") and content.endswith("```"):
                content = content.split("\n", 1)[-1].rsplit("```", 1)[0].strip()
            raw = json.loads(content)
            return {"story_intent": raw.get("story_intent"),
                    "reply": normalize_reply({"answer": state["reply"]["answer"],
                                                "profile": raw.get("profile"),
                                                "summary": raw.get("summary"),
                                                "recommendations": []}, state)}
    except (httpx.HTTPError, ValueError, KeyError, IndexError, TypeError, AttributeError) as error:
        logger.warning("advisor_memory_failed type=%s", type(error).__name__)
        return {}


def normalize_reply(raw, state):
    """Metadata phụ không được làm mất một câu trả lời văn bản hợp lệ."""
    if not isinstance(raw, dict):
        raise AdvisorOutputError("invalid_object")
    answer = raw.get("answer")
    if not isinstance(answer, str) or not answer.strip() or len(answer.strip()) > 16000:
        raise AdvisorOutputError("invalid_answer")
    profile = {key: list(state["profile"][key]) for key in PROFILE_KEYS}
    incoming = raw.get("profile")
    if isinstance(incoming, dict):
        for key in PROFILE_KEYS:
            if key not in incoming:
                continue
            try:
                profile[key] = getattr(Profile.model_validate({key: incoming[key]}), key)
            except ValidationError:
                logger.warning("advisor_metadata_ignored field=profile.%s", key)
    summary = raw.get("summary")
    if not isinstance(summary, str) or not summary.strip() or len(summary) > 1500:
        summary = state["session"]["summary"]
    recommendations, seen = [], set()
    items = raw.get("recommendations", [])
    if isinstance(items, list):
        for item in items[:12]:
            try:
                career = Recommendation.model_validate(item)
            except ValidationError:
                logger.warning("advisor_metadata_ignored field=recommendation")
                continue
            name = career.name.casefold()
            if name not in seen:
                seen.add(name)
                recommendations.append(career)
    return AdvisorReply(answer=answer, profile=Profile(**profile), summary=summary,
                        recommendations=recommendations).model_dump()


def validate_reply(state):
    return {"reply": AdvisorReply.model_validate(state["reply"]).model_dump()}



def save_messages(state):
    from advisor.postgres_adapter import PostgresConversationStore
    from advisor.postgres_store import save_messages_atomic

    store = get_store()

    if isinstance(store, PostgresConversationStore):
        session = save_messages_atomic(
            uid=state["uid"],
            session_id=state["session_id"],
            request_id=state["request_id"],
            message=state["message"],
            reply=state["reply"],
            mode=state["mode"],
            guest_reservation_token=state.get("guest_reservation_token"),
        )
        return {"session": session}

    from uuid import uuid4

    reply = state["reply"]

    user = {
        "id": str(uuid4()),
        "role": "user",
        "content": state["message"],
        "request_id": state["request_id"],
    }

    assistant = {
        "id": str(uuid4()),
        "role": "assistant",
        "content": reply["answer"],
        "recommendations": reply["recommendations"],
        "request_id": state["request_id"],
        "mode": state["mode"],
    }
    if reply.get('story_navigation'):
        assistant['story_navigation'] = reply['story_navigation']

    with store.lock:
        session = store.get(state["uid"], state["session_id"])

        if any(
            item.get("request_id") == state["request_id"]
            and item.get("role") == "user"
            for item in session["messages"]
        ):
            return {"session": session}

        session["messages"].extend([user, assistant])
        session["profile"] = reply["profile"]
        session["summary"] = reply["summary"]

        if len(session["messages"]) == 3 and session["title"] == "Một hướng đi mới":
            session["title"] = state["message"][:60]

        return {"session": store.write(state["uid"], session)}


builder = StateGraph(AdvisorState)
nodes = [("load_profile", load_profile), ("load_recent_conversation", load_recent_conversation),
         ("retrieve_careers", retrieve_careers), ("generate_answer", generate_response),
         ("compress_context", compress_context),
         ("suggest_career_story", suggest_story),
         ("validate_recommendations", validate_reply), ("update_profile_and_save", save_messages)]
previous = START
for name, function in nodes:
    builder.add_node(name, function)
    builder.add_edge(previous, name)
    previous = name
builder.add_edge(previous, END)
advisor_graph = builder.compile()
