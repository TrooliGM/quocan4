"""Conservative admission-score grounding. Public facts only, no LLM extraction.

The audited 2020 CAND announcement uses hierarchical paragraphs, not <table>.
Other layouts/years fail closed instead of turning search snippets into scores.
"""
import asyncio
from collections import OrderedDict
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
from decimal import Decimal
import http.client
import re
import threading
import time
from urllib.parse import urlsplit

from lxml import html, etree
from .conversation_context import plain, police_topic, score_topic

_pool=ThreadPoolExecutor(max_workers=2,thread_name_prefix='laban-score-source')
_slots=threading.BoundedSemaphore(2)
_pages=OrderedDict()
_hosts={'hvcsnd.edu.vn':'Học viện Cảnh sát nhân dân','cand.vn':'Báo Công an nhân dân'}
_schools={
    'hoc vien annd':'Học viện An ninh nhân dân',
    'hoc vien an ninh nhan dan':'Học viện An ninh nhân dân',
    'hoc vien canh sat nhan dan':'Học viện Cảnh sát nhân dân',
    'hoc vien chinh tri cong an nhan dan':'Học viện Chính trị Công an nhân dân',
    'dai hoc an ninh nhan dan':'Đại học An ninh nhân dân',
    'dai hoc canh sat nhan dan':'Đại học Cảnh sát nhân dân',
    'dai hoc pccc':'Đại học Phòng cháy chữa cháy',
    'dai hoc ky thuat hau can cand':'Đại học Kỹ thuật Hậu cần CAND',
}


def score_lookup(query):
    t=plain(query)
    return bool(police_topic(query) and score_topic(query) and not
                re.search(r'la gi|cach tinh|giai thich khai niem',t))


def official_host(url):
    from .search_provider import safe_url
    _,host=safe_url(url)
    host=host.removeprefix('www.')
    return host if host in _hosts else None


def parse_announcement(document, url):
    """Recognize one published layout; keep every row's complete explicit scope."""
    host=official_host(url)
    if host!='hvcsnd.edu.vn':return None  # Other publishers require their own audited layout.
    root=html.fromstring(document,parser=html.HTMLParser(no_network=True))
    detail=root.xpath('//div[contains(concat(" ",normalize-space(@class)," ")," story-detail ")]')
    if len(detail)!=1:return None
    title=detail[0].xpath('.//h1')
    bodies=detail[0].xpath('.//div[@class="story-body"]')
    if not title or len(bodies)!=1:return None
    heading=' '.join(title[0].text_content().split())
    if plain(heading)!='cong bo diem chuan vao cac truong cand 2020':return None
    # Refuse unexpected active content/table layouts instead of flattening columns.
    if bodies[0].xpath('.//script|.//style|.//table|.//iframe'):return None
    lines=[' '.join(p.text_content().split()) for p in bodies[0].xpath('./p')]
    school=program=gender=region=None;rows=[]
    for line in lines:
        t=plain(line).strip(' :.')
        school_key=re.sub(r'^truong ','',t)
        if school_key in _schools:
            school=_schools[school_key];program=gender=region=None;continue
        if re.match(r'^(?:truong |hoc vien |dai hoc )',t):
            school=program=gender=region=None;continue
        if re.match(r'^(?:\d+\. )?(?:nganh |nghiep vu |gui dao tao)',t):
            program=re.sub(r'^\d+\.\s*','',line);gender=region=None;continue
        area=re.fullmatch(r'(?:[a-z0-9]+\. )?phia (bac|nam)',t)
        if area:
            region='miền Bắc' if area[1]=='bac' else 'miền Nam';gender=None;continue
        sex=re.fullmatch(r'(?:[a-z]\. )?doi voi (nam|nu)',t)
        if sex:gender='nam' if sex[1]=='nam' else 'nữ';continue
        matches=list(re.finditer(r'Tổ hợp\s+([A-D]\d{2}):\s*(\d{1,2}(?:[.,]\d{1,2})?)(?=\s|điểm|,|$)',line,re.I))
        if matches:
            # Unknown headers or missing program must never inherit another row.
            if not school or not program:continue  # No inferred program for other sections.
            for i,m in enumerate(matches):
                score=Decimal(m[2].replace(',','.'))
                if not 0<=score<=30:return None
                segment=line[m.end():matches[i+1].start() if i+1<len(matches) else None]
                tie=re.search(r'tiêu chí phụ\s+(\d{1,2}(?:[.,]\d{1,2})?)',segment,re.I)
                rows.append(dict(year=2020,school=school,program=program,gender=gender,region=region,
                                 combination=m[1].upper(),score=str(score),tie_break=tie[1] if tie else None))
        elif t and not re.match(r'^- doi voi (nam|nu):',t):
            # Unexpected section (including changed article structure): stop safely.
            return None
    keys=[tuple(r[k] for k in ('year','school','program','gender','region','combination')) for r in rows]
    if not rows or len(keys)!=len(set(keys)):return None
    # The page explicitly credits CAND; this is not the Ministry's own portal.
    credit='Báo Công an nhân dân điện tử' if 'Nguồn' in detail[0].text_content() and 'Báo Công an nhân dân điện tử' in detail[0].text_content() else None
    intro=' '.join(detail[0].text_content().split())
    provider='Cục Đào tạo, Bộ Công an' if 'Cục Đào tạo' in intro and 'Bộ Công an' in intro else None
    return {'title':heading,'rows':rows,'publisher':_hosts[host],'credited_source':credit,
            'information_provider':provider,'original_publication_url':None}


def select_rows(query, rows):
    """Explicit unknown selectors do not match an unspecified table field."""
    school=police_topic(query);t=plain(query)
    years=re.findall(r'\b(?:19|20)\d{2}\b',t)
    if len(set(years))!=1:return []
    gender_text=re.sub(r'(?:mien|phia) (?:bac|nam)|nam\s+(?:19|20)\d{2}','',t)
    if re.search(r'\bnu\b',gender_text) and re.search(r'\bnam\b',gender_text):return []
    if 'bac' in t and re.search(r'(?:mien|phia) nam',t):return []
    gender='nữ' if re.search(r'\bnu\b',gender_text) else 'nam' if re.search(r'\bnam\b',gender_text) else None
    region='miền Bắc' if re.search(r'(?:mien|phia) bac',t) else 'miền Nam' if re.search(r'(?:mien|phia) nam',t) else None
    combination=re.findall(r'\b[A-D]\d{2}\b',query.upper())
    programs=[p for p in ('nghiep vu canh sat','nghiep vu an ninh','an toan thong tin','nganh y') if p in t]
    if not school or school=='các trường đại học Công an nhân dân' or len(combination)!=1 or len(programs)>1 or not gender and not region:return []
    return [r for r in rows if r['year']==int(years[0]) and r['school']==school
            and (not gender or r['gender']==gender) and (not region or r['region']==region)
            and r['combination']==combination[0]
            and (not programs or all(p in plain(r['program']) for p in programs))]


async def read_announcement(url):
    from .search_provider import _source_request, SearchUnavailable
    if not official_host(url):return None
    hit=_pages.get(url)
    if hit and hit[0]>time.monotonic():return {**hit[1],'cached':True}
    if not _slots.acquire(blocking=False):return None
    def read():return parse_announcement(_source_request(url,read=True),url)
    try:future=_pool.submit(read)
    except BaseException:_slots.release();raise
    future.add_done_callback(lambda _: _slots.release())
    try:
        async with asyncio.timeout(3):parsed=await asyncio.wrap_future(future)
        if parsed:
            parsed['read_at']=datetime.now(timezone.utc).isoformat()
            _pages[url]=(time.monotonic()+300,parsed)
            while len(_pages)>16:_pages.popitem(last=False)
            return {**parsed,'cached':False}
    except (SearchUnavailable,OSError,ValueError,TimeoutError,http.client.HTTPException,etree.LxmlError):pass
    return None


async def ground_scores(query, retrieval, session):
    from .search_provider import SearchUnavailable
    if not score_lookup(query):return retrieval
    result={**retrieval,'score_evidence':{'status':'unverified','query':query}}
    if retrieval.get('status')=='privacy_blocked':return result
    # Only server-saved source metadata, never arbitrary URLs in message text.
    candidates=list(retrieval.get('sources',[]))
    for message in reversed(session.get('messages',[])[-12:]):
        if message.get('role')=='assistant':candidates+=message.get('sources',[])
    # An already verified announcement must not be crowded out by two new links
    # with unsupported layouts (e.g. image-only notices). Still re-read/TTL check.
    candidates.sort(key=lambda source:0 if source.get('verification_level')=='official_score_table_read'
                    else 1 if plain(source.get('title','')).startswith('cong bo diem chuan vao cac truong cand 2020') else 2)
    seen=set()
    for source in candidates:
        url=source.get('url','')
        try:
            if url in seen or official_host(url)!='hvcsnd.edu.vn' or source.get('verification_level') not in ('search_snippet_link_checked','official_score_table_read'):continue
            seen.add(url)
            if len(seen)>2:break
            page=await read_announcement(url)
            if not page:continue
            rows=select_rows(query,page['rows'])
            if len(rows)!=1:
                result['score_evidence']['status']='needs_clarification'
                continue
            row=rows[0]
            excerpt='; '.join(f'{k}: {v}' for k,v in row.items() if v is not None)
            from .search_provider import Source
            proof=Source(title=page['title'],url=url,domain=urlsplit(url).hostname,publisher=page['publisher'],
                         retrieved_at=page.get('read_at',datetime.now(timezone.utc).isoformat()),supporting_excerpt=excerpt,
                         verification_level='official_score_table_read',target_year=row['year'],temporal_relation='explicit_table_year',
                         information_provider=page['information_provider'],credited_source=page['credited_source'],original_publication_url=None).model_dump()
            return {**result,'status':'ok','sources':[proof],'score_evidence':{'status':'verified','row':row,'query':query,'cached':page['cached']}}
        except (ValueError,KeyError,TypeError,SearchUnavailable):continue
    return result


def grounded_answer(retrieval):
    """Deterministic numeric boundary: LLM prose cannot invent a range/score."""
    evidence=retrieval.get('score_evidence')
    if not evidence:return None
    if evidence['status']!='verified':
        return ('Mình chưa đối chiếu được một dòng điểm trong nội dung công bố chính thức khớp đủ điều kiện, '
                'nên chưa thể đưa con số hay dải điểm từ đoạn trích tìm kiếm. '
                'Bạn cho mình biết trường, ngành, năm, nam/nữ, khu vực (nếu phân chia) và tổ hợp xét tuyển nhé?')
    row=evidence['row'];source=retrieval['sources'][0]
    parts=[f"**{row['school']}**, **{row['year']}**, {row['program']}",
           'đối tượng '+(row['gender'] or 'không tách nam/nữ trong dòng công bố'),
           'khu vực '+(row['region'] or 'không phân chia trong mục này'),f"tổ hợp **{row['combination']}**"]
    answer='; '.join(parts)+f": **{row['score'].replace('.',',')} điểm**."
    if row['tie_break']:answer+=f" Tiêu chí phụ được công bố: {row['tie_break'].replace('.',',')} điểm."
    answer+='\n\nĐã đối chiếu nội dung công bố; không suy rộng sang ngành, giới tính, khu vực hoặc tổ hợp khác.'
    if evidence['cached']:answer+=' Nội dung công khai được đọc lại từ bộ nhớ đệm ngắn hạn.'
    answer+=f"\n\nWebsite đăng bài: {source['publisher']}."
    if source.get('information_provider'):answer+=f" Đơn vị cung cấp thông tin được bài nêu: {source['information_provider']}."
    if source.get('credited_source'):answer+=f" Bài ghi nguồn: {source['credited_source']}."
    answer+=' Chưa xác minh URL văn bản thông báo gốc riêng biệt.'
    return answer+f"\n\n[{source['title']}]({source['url']})"
