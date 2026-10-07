import asyncio
import os
import unicodedata
from pathlib import Path

import httpx
from dotenv import load_dotenv
from fastapi import FastAPI, Header, HTTPException, Query, Response
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field, field_validator

from content import ARTICLES, CAREERS
from firebase_auth import verify_user, web_config

ROOT = Path(__file__).resolve().parent
load_dotenv(ROOT / ".env")
app = FastAPI(title="La Bàn — KHKT 2027", version="0.1.0")
ai_slots = asyncio.Semaphore(4)


@app.middleware("http")
async def auth_cache_control(request, call_next):
    response = await call_next(request)
    if request.url.path.startswith("/api/auth/"):
        response.headers["Cache-Control"] = "no-store"
    return response


def normalize(text: str) -> str:
    text = unicodedata.normalize("NFD", text.casefold().replace("đ", "d"))
    return "".join(c for c in text if unicodedata.category(c) != "Mn")


@app.get("/", include_in_schema=False)
def homepage():
    return FileResponse(ROOT / "public" / "index.html")


@app.get("/api/health")
def health():
    return {"status": "ok", "ai_configured": bool(os.getenv("DEEPSEEK_API_KEY", "").strip()),
            "auth_configured": web_config()["configured"]}


@app.get("/api/auth/config")
def auth_config(response: Response):
    response.headers["Cache-Control"] = "no-store"
    return web_config()


@app.get("/api/auth/me")
def current_user(response: Response, authorization: str | None = Header(default=None)):
    response.headers["Cache-Control"] = "no-store"
    parts = authorization.split() if authorization else []
    if len(parts) != 2 or parts[0].lower() != "bearer" or len(parts[1]) > 12000:
        raise HTTPException(401, "Bạn cần đăng nhập để xem tài khoản.", headers={"WWW-Authenticate": "Bearer"})
    return {"user": verify_user(parts[1])}


@app.get("/api/careers")
def careers(q: str = Query("", max_length=120), category: str = Query("", max_length=60)):
    search = normalize(q.strip())
    return {"items": [c for c in CAREERS if (not category or c["category"] == category) and
                      search in normalize(" ".join([c["name"], c["category"], c["description"], *c["skills"]]))]}


@app.get("/api/articles")
def articles():
    return {"items": ARTICLES}


class AdviceRequest(BaseModel):
    question: str = Field(min_length=3, max_length=600)

    @field_validator("question", mode="before")
    @classmethod
    def strip_question(cls, value):
        return value.strip() if isinstance(value, str) else value


@app.post("/api/advice")
async def advice(payload: AdviceRequest):
    if not os.getenv("DEEPSEEK_API_KEY", "").strip():
        raise HTTPException(503, "Trợ lý đang được chuẩn bị. Bạn vẫn có thể khám phá nghề và đọc bài viết.")
    from ai import advice_graph
    try:
        async with asyncio.timeout(30):
            async with ai_slots:
                result = await advice_graph.ainvoke({"question": payload.question, "context": "", "answer": ""})
        return {"answer": result["answer"], "model": os.getenv("DEEPSEEK_MODEL", "deepseek-chat")}
    except (TimeoutError, httpx.TimeoutException):
        raise HTTPException(504, "Trợ lý phản hồi hơi lâu. Bạn thử lại sau một chút nhé.") from None
    except (httpx.HTTPError, ValueError, KeyError, IndexError, RuntimeError):
        raise HTTPException(502, "Chưa kết nối được trợ lý. Bạn thử lại sau nhé.") from None


# public/ được Vercel phục vụ qua CDN; mount này chỉ dành cho chạy local.
if not os.getenv("VERCEL"):
    app.mount("/assets", StaticFiles(directory=ROOT / "public" / "assets"), name="assets")
