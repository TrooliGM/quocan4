"""Luồng LangGraph: lấy ngữ cảnh nghề → tư vấn bằng DeepSeek."""
import os
from typing import TypedDict

import httpx
from langgraph.graph import END, START, StateGraph

from content import CAREERS


class AdviceState(TypedDict):
    question: str
    context: str
    answer: str


def build_context(state: AdviceState):
    context = "\n".join(f"{c['name']}: {c['description']} Kỹ năng: {', '.join(c['skills'])}. Bước đầu: {c['first_step']}" for c in CAREERS)
    return {"context": context}


async def ask_deepseek(state: AdviceState):
    key = os.getenv("DEEPSEEK_API_KEY", "").strip()
    if not key:
        raise RuntimeError("missing_api_key")
    prompt = (
        "Bạn là La Bàn, trợ lý khám phá nghề cho học sinh THCS và THPT. "
        "Trả lời bằng tiếng Việt, thân thiện, tối đa 220 từ. Giúp học sinh khám phá, "
        "không khẳng định một nghề là số phận hay chẩn đoán tính cách. "
        "Chỉ tư vấn học tập và nghề nghiệp; từ chối ngắn gọn yêu cầu ngoài phạm vi. "
        "Không yêu cầu thông tin cá nhân nhạy cảm. Không bịa thu nhập, tuyển sinh, "
        "số liệu thị trường hay nguồn; khi thiếu dữ liệu hãy nói rõ. "
        "Gợi ý một hoạt động nhỏ và một câu hỏi tự suy ngẫm. "
        "Nội dung tham khảo của dự án:\n" + state["context"]
    )
    async with httpx.AsyncClient(timeout=httpx.Timeout(25, connect=8)) as client:
        response = await client.post(
            "https://api.deepseek.com/chat/completions",
            headers={"Authorization": f"Bearer {key}"},
            json={"model": os.getenv("DEEPSEEK_MODEL", "deepseek-chat"),
                  "messages": [{"role": "system", "content": prompt}, {"role": "user", "content": state["question"]}],
                  "max_tokens": 700, "stream": False},
        )
        response.raise_for_status()
        answer = response.json()["choices"][0]["message"]["content"]
        if not isinstance(answer, str) or not answer.strip():
            raise ValueError("empty_model_response")
        return {"answer": answer.strip()}


builder = StateGraph(AdviceState)
builder.add_node("career_context", build_context)
builder.add_node("deepseek_advice", ask_deepseek)
builder.add_edge(START, "career_context")
builder.add_edge("career_context", "deepseek_advice")
builder.add_edge("deepseek_advice", END)
advice_graph = builder.compile()
