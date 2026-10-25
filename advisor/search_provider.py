"""Tra cứu độc lập nhà cung cấp. Snippet không được coi là đã đọc toàn trang.

Chỉ gọi trong lượt chat đã qua auth/rate/quota. Không fetch URL do LLM tự tạo.
"""
import asyncio
from collections import OrderedDict
from datetime import datetime, timezone
import hashlib
from concurrent.futures import ThreadPoolExecutor
import http.client
import ipaddress
import logging
import os
import re
import socket
import ssl
import time
import threading
import unicodedata
from typing import Protocol
from urllib.parse import urlsplit, quote
import httpx
from pydantic import BaseModel, Field

class Source(BaseModel):
    title: str = Field(max_length=240)
    url: str = Field(max_length=1500)
    domain: str
    publisher: str
    published_at: str | None = None
    retrieved_at: str
    supporting_excerpt: str = Field(max_length=700)
    verification_level: str = 'search_snippet_link_checked'
    target_year: int | None = None
    temporal_relation: str = 'not_requested'

class SearchUnavailable(RuntimeError):pass
class SearchProvider(Protocol):
    async def search(self, query: str) -> list[dict]: ...

def needs_search(text):
    from .conversation_context import plain
    text=plain(text)
    if re.search(r'\b(?:khong|ko|k|dung) (?:can )?(?:tra (?:cuu|web)|tim (?:kiem|nguon)|search)\b',text):return False
    return bool(re.search(
        r'\b(?:19|20)\d{2}\b|hien nay|hien tai|moi nhat|moi nt|tra (?:cuu|giup|ho|web)|'
        r'tim (?:nguon|kiem|tren (?:google|web|mang))|\bsearch\b|thong ke|muc luong|luong .*?(?:bao nhieu|khoang|hien)|'
        r'diem chuan|tuyen sinh|nhu cau nhan luc|quy dinh|chinh sach|chung chi hanh nghe|bao cao|nghien cuu moi|'
        r'nguon .*?(?:dau|nao)|(?:dan|cho|xin) nguon|(?:dang|hien) phat trien|xu huong',text))

def private_query(text):
    """Fail closed on identifiers/self disclosures; never receive profile/survey objects."""
    from .conversation_context import plain
    return bool(re.search(
        r'sk-[\w-]{16,}|eyJ[\w-]+\.[\w-]+\.[\w-]+|private key|database_url|password|mat khau|'
        r'[\w.+-]+@[\w.-]+|\+?\d[\d .-]{8,}\d|https?://|'
        r'\b(?:toi|em|minh|mk|anh|chi|chau|con) (?:ten|o|hoc tai|hoc lop|hoc truong|song|bi benh|mac benh|thich|gioi|yeu|kem)|'
        r'ho ten|dia chi|so dien thoai|so can cuoc|cccd|ngay sinh|ho so (?:cua|ca nhan)|benh an',plain(text)))

def relevant(query,title,excerpt):
    def plain(t):return ''.join(c for c in unicodedata.normalize('NFD',t.lower()) if unicodedata.category(c)!='Mn').replace('đ','d')
    stop={'hay','tong','hop','thong','tin','nam','nganh','cua','toi','minh','ban','cho','tra','cuu','tim','kiem','ve','hien','nay','moi','nhat','tinh','hinh','lieu','bao','cao'}
    words={w for w in re.findall(r'[a-z]+',plain(query)) if len(w)>2 and w not in stop}
    text=plain(title+' '+excerpt)
    return bool(words) and any(re.search(r'\b'+re.escape(w)+r'\b',text) for w in words)

def safe_url(url):
    try:
        u=urlsplit(url)
        if u.scheme!='https' or not u.hostname or u.username or u.password or u.port not in (None,443) or len(url)>1500 or any(c.isspace() or ord(c)<32 for c in url):raise ValueError()
        host=u.hostname.encode('idna').decode('ascii')
        if host.endswith(('.localhost','.local','.internal')) or '.' not in host:raise ValueError()
        return u,host
    except (ValueError,UnicodeError):raise SearchUnavailable('unsafe_source') from None

def public_addresses(host):
    rows=socket.getaddrinfo(host,443,type=socket.SOCK_STREAM)
    addresses=list(dict.fromkeys(row[4][0] for row in rows))
    if not addresses or any(not ipaddress.ip_address(ip).is_global for ip in addresses):raise SearchUnavailable('unsafe_source')
    return addresses

def check_link(url):
    """HEAD trên IP đã xác minh và ghim kết nối; giữ SNI/TLS hostname gốc.

    Không follow redirect, không tải body, không có DNS lần hai/rebinding.
    """
    u,host=safe_url(url);addresses=public_addresses(host)
    class PinnedHTTPS(http.client.HTTPSConnection):
        def connect(self):
            sock=socket.create_connection((addresses[0],443),timeout=2.5)
            try:self.sock=self._context.wrap_socket(sock,server_hostname=host)
            except BaseException:sock.close();raise
    conn=PinnedHTTPS(host,timeout=2.5,context=ssl.create_default_context())
    try:
        path=quote(u.path or '/',safe='/%:@!$&\'()*+,;=-._~')
        if u.query:path+='?'+quote(u.query,safe='/%?:@!$&\'()*+,;=-._~')
        conn.request('HEAD',path,headers={'User-Agent':'LaBan-Career-SourceCheck/1.0'})
        response=conn.getresponse()
        return 200<=response.status<300
    finally:conn.close()

class BraveSearch:
    async def search(self,query):
        key=os.getenv('SEARCH_API_KEY','').strip()
        if not key:raise SearchUnavailable('not_configured')
        # URL cố định; query ở params, không log URL/header/body.
        async with httpx.AsyncClient(timeout=httpx.Timeout(5,connect=2),follow_redirects=False,trust_env=False) as client:
            for attempt in range(2):
                async with client.stream('GET','https://api.search.brave.com/res/v1/web/search',params={'q':query,'count':6,'safesearch':'strict','search_lang':'vi'},headers={'X-Subscription-Token':key}) as response:
                    if response.status_code in (502,503,504) and not attempt:continue
                    response.raise_for_status();raw=bytearray()
                    async for part in response.aiter_bytes():
                        raw.extend(part)
                        if len(raw)>200000:raise SearchUnavailable('oversize')
                    import json
                    return json.loads(raw).get('web',{}).get('results',[])[:6]
        raise SearchUnavailable('unavailable')

# Slots are released on actual worker completion, even after caller cancellation.
# PostgreSQL rate/quota protection remains shared across serverless instances.
_ddgs_pool=ThreadPoolExecutor(max_workers=2,thread_name_prefix='laban-search')
_ddgs_slots=threading.BoundedSemaphore(2)

class DDGSSearch:
    @staticmethod
    def _search(query):
        try:
            from ddgs import DDGS
            logger=logging.getLogger('ddgs');logger.handlers=[logging.NullHandler()];logger.propagate=False
            with DDGS(timeout=5,verify=True) as client:
                rows=client.text(query,max_results=5,safesearch='on',backend='auto',region='vn-vi')
            return [{'title':str(r.get('title',''))[:240],'url':str(r.get('href',''))[:1500],
                     'description':str(r.get('body',''))[:700]} for r in rows[:5]]
        except Exception:
            # Upstream exceptions may include raw queries. Never echo or log them.
            raise SearchUnavailable('ddgs_unavailable') from None

    async def search(self,query):
        if not _ddgs_slots.acquire(blocking=False):raise SearchUnavailable('busy')
        try:future=_ddgs_pool.submit(self._search,query)
        except BaseException:
            _ddgs_slots.release();raise
        future.add_done_callback(lambda _: _ddgs_slots.release())
        async with asyncio.timeout(7):return await asyncio.wrap_future(future)

_cache=OrderedDict()
def provider():
    name=os.getenv('SEARCH_PROVIDER','').strip().lower()
    if name=='brave':return BraveSearch()
    if name=='ddgs':return DDGSSearch()
    raise SearchUnavailable('not_configured')

async def retrieve(uid,text):
    if not needs_search(text):return {'status':'not_needed','sources':[]}
    if private_query(text):
        return {'status':'privacy_blocked','sources':[]}
    year_match=re.search(r'\b((?:19|20)\d{2})\b',text);year=int(year_match[1]) if year_match else None
    # Không gửi profile/khảo sát/UID. Chặn định danh rõ ràng trong câu tra cứu.
    query=text[:300]
    cache_key=hashlib.sha256((os.getenv('SEARCH_PROVIDER','')+'\0'+uid+'\0'+query).encode()).hexdigest()
    hit=_cache.get(cache_key)
    if hit and hit[0]>time.monotonic():return {**hit[1],'cached':True}
    try:
        async with asyncio.timeout(12):
            rows=await provider().search(query)
            async def validate(row):
                try:
                    url=row['url'];_,host=safe_url(url)
                    excerpt=re.sub('<[^>]+>','',row.get('description',''))[:700]
                    if not relevant(query,row['title'],excerpt):return None
                    if not await asyncio.to_thread(check_link,url):return None
                    return Source(title=row['title'][:240],url=url,domain=host,publisher=host,published_at=row.get('page_age') if isinstance(row.get('page_age'),str) else None,retrieved_at=datetime.now(timezone.utc).isoformat(),supporting_excerpt=excerpt,target_year=year,temporal_relation='year_mentioned_only' if year and str(year) in excerpt else 'not_established' if year else 'not_requested').model_dump()
                except (ValueError,KeyError,TypeError,OSError,http.client.HTTPException,SearchUnavailable):return None
            candidates=await asyncio.gather(*(validate(row) for row in rows[:6]))
            def rank(s):return any(s['domain'].endswith(t) for t in ('.gov.vn','.edu.vn','.gov','.edu'))
            unique={s['url']:s for s in candidates if s and s['supporting_excerpt']}
            sources=sorted(unique.values(),key=rank,reverse=True)[:4]
            result={'status':'ok' if sources else 'no_verified_sources','target_year':year,'sources':sources}
            _cache[cache_key]=(time.monotonic()+(3600 if year and year<datetime.now().year else 300),result)
            while len(_cache)>64:_cache.popitem(last=False)
            return result
    except (SearchUnavailable,httpx.HTTPError,TimeoutError,ValueError,KeyError,TypeError):
        return {'status':'unavailable','target_year':year,'sources':[]}

def constrain_links(answer,sources):
    allowed={s['url'] for s in sources}
    answer=re.sub(r'\[([^\]]+)\]\((https?://[^\s)]+)\)',lambda m:m[0] if m[2] in allowed else m[1]+' (chưa có nguồn đã kiểm tra)',answer)
    return re.sub(r'https?://[^\s<>\])]+',lambda m:m[0] if m[0].rstrip('.,;') in allowed else '[đường dẫn chưa xác minh]',answer)

async def search_context(state):
    from .performance import measure
    from .conversation_context import public_search_query
    from .rollout import search_restricted
    # Gate trước provider/cache/context expansion. Flag chỉ từ Firebase/server identity.
    if search_restricted() and not state.get('web_search_allowed',False):
        return {'retrieval':{'status':'unavailable' if needs_search(state['message']) else 'not_needed','sources':[]}}
    with measure('web_search'):result=await retrieve(state['uid'],public_search_query(state.get('session',{'messages':[]}),state['message']))
    return {'retrieval':result}
