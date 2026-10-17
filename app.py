import asyncio
import os
import logging
import unicodedata
from pathlib import Path

import httpx
from dotenv import load_dotenv
from fastapi import FastAPI, Header, HTTPException, Query, Response
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field, field_validator

from content import ARTICLES, CAREERS
from career_stories import STORIES, get_story
from firebase_auth import verify_user, web_config
from advisor.store import StorageConfigurationError
from advisor.storage_errors import storage_error
from deepseek_client import provider_http_error, model_name
import psycopg

ROOT = Path(__file__).resolve().parent
if not os.getenv('VERCEL'):
    load_dotenv(ROOT / ".env")
from advisor.routes import router as advisor_router

app = FastAPI(title="La Bàn — KHKT 2027", version="0.1.0")
app.include_router(advisor_router)
ai_slots = asyncio.Semaphore(4)
logger = logging.getLogger(__name__)


@app.exception_handler(StorageConfigurationError)
@app.exception_handler(psycopg.Error)
async def storage_failure(request, error):
    status, detail = storage_error(error)
    logger.error('storage_failure code=%s type=%s', detail['code'], type(error).__name__)
    return JSONResponse({'detail': detail}, status_code=status, headers={'Cache-Control': 'no-store', 'Retry-After': '30'})


def html_page(filename):
    # HTML runtime ở gốc, assets trong public/ do Vercel CDN phục vụ.
    # Bản public là fallback cho checkout cũ/local; không giả định nó có trong Function.
    for path in (ROOT / filename, ROOT / 'public' / filename):
        try:
            return HTMLResponse(path.read_text(encoding='utf-8'), headers={'Cache-Control': 'no-store'})
        except (OSError, UnicodeError):
            continue
    logger.error('html_page_unavailable page=%s', filename)
    return HTMLResponse('<!doctype html><html lang="vi"><meta charset="utf-8"><title>La Bàn</title>'
                        '<h1>La Bàn đang được cập nhật</h1><p>Chưa tải được trang này. Bạn thử lại sau nhé.</p>'
                        '<a href="/">Về trang chủ</a></html>', status_code=503,
                        headers={'Cache-Control': 'no-store', 'Retry-After': '30'})


@app.middleware("http")
async def auth_cache_control(request, call_next):
    response = await call_next(request)
    if request.url.path.startswith(("/api/auth/", "/api/ai/", "/api/voice/")):
        response.headers["Cache-Control"] = "no-store"
    return response


def normalize(text: str) -> str:
    text = unicodedata.normalize("NFD", text.casefold().replace("đ", "d"))
    return "".join(c for c in text if unicodedata.category(c) != "Mn")


@app.get("/", include_in_schema=False)
def homepage():
    return html_page('index.html')


@app.get("/ai-career-advisor", include_in_schema=False)
@app.get("/chat", include_in_schema=False)
def career_advisor():
    return html_page('chat.html')

@app.get("/mot-ngay-lam-viec", include_in_schema=False)
def career_comics():
    return html_page('stories.html')


@app.get("/api/career-stories")
def story_catalog():
    return {"items": [{"id": c["id"], "name": c["name"], "category": c["category"],
                       "color": c["color"], "scenes": len(STORIES[c["id"]]["scenes"])}
                      for c in CAREERS if c["id"] in STORIES]}


@app.get("/api/career-stories/{career_id}")
def career_story(career_id: str):
    story = get_story(career_id)
    if not story:
        raise HTTPException(404, "Chưa có truyện cho nghề này. Bạn chọn một nghề trong thư viện nhé.")
    return story


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


class StoryQuestion(AdviceRequest):
    scene_index: int = Field(default=0, ge=0, le=20)


@app.post("/api/career-stories/{career_id}/ask")
async def ask_about_story(career_id: str, payload: StoryQuestion, response: Response):
    response.headers["Cache-Control"] = "no-store"
    story = career_story(career_id)
    if payload.scene_index >= len(story["scenes"]):
        raise HTTPException(422, "Cảnh truyện không hợp lệ.")
    if not os.getenv("DEEPSEEK_API_KEY", "").strip():
        raise HTTPException(503, "La Bàn AI chưa được cấu hình. Bạn vẫn có thể xem truyện và thử các tình huống.")
    from story_ai import story_graph
    try:
        async with asyncio.timeout(30):
            async with ai_slots:
                result = await story_graph.ainvoke({"career_id": career_id, "scene_index": payload.scene_index,
                                                   "question": payload.question, "context": "", "answer": ""})
        return {"answer": result["answer"]}
    except (TimeoutError, httpx.HTTPError, ValueError, KeyError, IndexError, TypeError, AttributeError, RuntimeError) as error:
        raise provider_http_error(error) from None


@app.post("/api/advice")
async def advice(payload: AdviceRequest):
    if not os.getenv("DEEPSEEK_API_KEY", "").strip():
        raise HTTPException(503, "Trợ lý đang được chuẩn bị. Bạn vẫn có thể khám phá nghề và đọc bài viết.")
    from ai import advice_graph
    try:
        async with asyncio.timeout(30):
            async with ai_slots:
                result = await advice_graph.ainvoke({"question": payload.question, "context": "", "answer": ""})
        return {"answer": result["answer"], "model": model_name()}
    except (TimeoutError, httpx.HTTPError, ValueError, KeyError, IndexError, TypeError, AttributeError, RuntimeError) as error:
        raise provider_http_error(error) from None


# public/ được Vercel phục vụ qua CDN; mount này chỉ dành cho chạy local.
if not os.getenv("VERCEL"):
    app.mount("/assets", StaticFiles(directory=ROOT / "public" / "assets"), name="assets")
