"""Lập kế hoạch ngữ cảnh gọn; không suy năng lực hoặc tạo reasoning nội bộ."""
import re
import unicodedata


def plain(text):
    return ''.join(c for c in unicodedata.normalize('NFD', text.lower())
                   if unicodedata.category(c) != 'Mn').replace('đ', 'd')


def plan_turn(session, message):
    text = plain(message)
    from .search_provider import needs_search
    intent = 'explain'
    if needs_search(message):intent = 'research'
    elif re.search(r'so sanh|khac nhau|uu nhuoc|hay la', text):intent = 'compare'
    elif re.search(r'ke hoach|lo trinh|tung buoc|bat dau tu dau', text):intent = 'plan'
    elif re.search(r'goi y|tu van|hoat dong|chua biet.*thich', text):intent = 'advise'
    elif re.fullmatch(r'(chao|hi|hello|cam on|ok)[! .]*', text):intent = 'social'
    simple_math=bool(re.match(r'^\s*\d+\s*[+*/×÷-]\s*\d+',text)) and not needs_search(message)
    topic_change=bool(re.search(r'doi chu de|khong tu van nghe|dung (?:chuyen sang|noi ve) (?:tu van )?nghe',text))
    short = bool(re.search(r'ngan gon|ngan thoi|mot cau|[123] cau|chi.*mot so', text))
    deep = bool(re.search(r'phan tich sau|chi tiet|nghien cuu|ky hon', text))
    limit = 800 if short or intent == 'social' else 3500 if deep else 2600 if intent in ('compare', 'plan', 'research') else 2000
    career = (session.get('messages') or [{}])[0].get('career_context', {})
    return {'intent':intent, 'detail':'brief' if short else 'deep' if deep else 'adaptive',
            'max_tokens':limit, 'mode':career.get('mode','career_discovery'),
            'career_id':career.get('career_id'),'needs_career_reference':intent!='social' and not simple_math and not topic_change,
            'needs_survey_context':intent!='social' and not simple_math and not topic_change}


def bounded_history(messages, budget=12000):
    """Giữ phần gần nhất trong ngân sách; tham chiếu xa dùng summary của đúng phiên."""
    rows=[];used=0
    for item in reversed(messages[-40:]):
        text=item['content']
        if item.get('recommendations'):
            text+='\nCác nghề đã gợi ý: '+', '.join(str(r.get('name',''))[:100] for r in item['recommendations'][:8])
        if len(text)>6000:text=text[:4000]+'\n[Phần giữa đã rút gọn]\n'+text[-1900:]
        if used+len(text)>budget and rows:break
        text=text[-budget:];rows.append({'role':item['role'],'content':text});used+=len(text)
    rows.reverse()
    # Nhánh tham chiếu xa do summary đảm nhiệm; không ghép thêm private profile khi OFF.
    return rows


def police_topic(text):
    """Chỉ trích tên chủ đề công khai, không sao chép câu trả lời/hồ sơ."""
    t=plain(text)
    if not re.search(r'cong an|\bcand\b|an ninh nhan dan|canh sat nhan dan|\bannd\b|\bcsnd\b',t):return None
    # Tên cụ thể do người dùng nêu được giữ; không tự chọn một trường từ danh sách.
    names=[('dai hoc an ninh nhan dan','Đại học An ninh nhân dân'),
           ('dai hoc canh sat nhan dan','Đại học Cảnh sát nhân dân'),
           ('hoc vien an ninh nhan dan','Học viện An ninh nhân dân'),
           ('hoc vien canh sat nhan dan','Học viện Cảnh sát nhân dân'),
           ('dai hoc phong chay chua chay','Đại học Phòng cháy chữa cháy')]
    found=[name for key,name in names if key in t]
    return found[0] if len(found)==1 else 'các trường đại học Công an nhân dân'


def score_topic(text):
    return bool(re.search(r'diem chuan|diem trung tuyen|diem xet tuyen|bao nhieu diem|lay .*?diem',plain(text)))


def admission_selectors(text):
    """Public cohort selectors only; don't copy arbitrary history into a query."""
    t=plain(text);parts=[]
    if re.search(r'\bnu\b',t):parts.append('nữ')
    elif re.search(r'(?:thi sinh|doi tuong|danh cho) nam\b|\bnam (?=mien|to hop)',t):parts.append('nam')
    for key,label in [('mien bac','miền Bắc'),('mien nam','miền Nam')]:
        if key in t:parts.append(label)
    parts+=list(dict.fromkeys(re.findall(r'\b[A-D]\d{2}\b',text.upper())))
    return ' '.join(parts)


def public_search_plan(session, message):
    """Resolve elliptical public lookups from bounded history; never add survey/profile.

    A complete new subject takes precedence. Assistant history can supply only
    canonical police/score anchors, not arbitrary prose, numbers or source text.
    """
    from .search_provider import private_query,needs_search
    text=plain(message);years=re.findall(r'\b(?:19|20)\d{2}\b',message)
    plan={'query':message,'follow_up':False,'ambiguous':False}
    if private_query(message):return plan
    # An explicit new topic (including calendar questions) must never inherit police scores.
    calendar=bool(re.search(r'nam nhuan|bao nhieu ngay|lich (?:am|duong)',text))
    reference=bool(re.search(r'nganh (do|nay)|nghe (do|nay)|nam (ay|do)|nguon .*?(?:dau|nao)|(?:dan|cho|xin) nguon',text))
    elliptical=bool(re.match(r'^(?:vay|the|con|the thi|vay thi|nam|bao nhieu|la bao nhieu)\b',text))
    # Strip question scaffolding to distinguish a year-only follow-up from a new topic.
    residue=re.sub(r'\b(?:19|20)\d{2}\b|\b(?:vay|thi|the|con|nam|la|bao|nhieu|a|ah|ha|nhi|duoc|co|the|cho|em|hoi|voi|sao|nao|diem|chuan|trung|tuyen)\b|[^a-z ]',' ',text)
    elliptical=elliptical and not residue.strip()
    if calendar or not (reference or elliptical):return plan
    plan['follow_up']=True
    history=session.get('messages',[])[-16:]
    topic=None;previous_year=None;is_score=False;selectors=''
    assistant_topic=None;assistant_score=False
    for row in reversed(history):
        previous=row.get('content','');p=plain(previous)
        if previous==message:continue
        # Never walk past an explicit topic switch to revive a stale subject.
        if row.get('role')=='user' and re.search(r'doi chu de|nam nhuan|bao nhieu ngay',p):break
        if row.get('role')=='assistant':
            # Canonical extraction only: even URLs/PII in a reply are never copied.
            if not assistant_topic:assistant_topic=police_topic(previous)
            assistant_score=assistant_score or score_topic(previous)
            continue
        if row.get('role')!='user' or private_query(previous):continue
        # Follow-up fillers aren't the actual subject; continue to its last explicit turn.
        candidate=police_topic(previous)
        if candidate:
            topic=candidate;is_score=score_topic(previous) or assistant_score
        elif needs_search(previous) and re.search(r'[a-z]{3}',re.sub(r'\b(?:vay|nam|bao|nhieu|the|con|la)\b','',p)):
            topic=previous[:200];is_score=score_topic(previous)
        elif score_topic(previous) and assistant_topic:
            topic=assistant_topic;is_score=True
        if topic:
            prior=re.search(r'\b(?:19|20)\d{2}\b',previous)
            previous_year=prior[0] if prior else None
            selectors=admission_selectors(previous)
            break
    if not topic and elliptical and not assistant_score:
        # A career name alone does not identify a quantity (score, salary, intake...).
        plan['ambiguous']=True
        return plan
    topic=topic or assistant_topic
    if not topic:
        career=(session.get('messages') or [{}])[0].get('career_context',{})
        topic=career.get('career_name')
    if not topic:
        plan['ambiguous']=elliptical
        return plan
    year=years[0] if years else previous_year
    if police_topic(topic) and (is_score or assistant_score):
        query='điểm chuẩn '+topic
        if selectors:query+=' '+selectors
        if year:query+=' năm '+year
        plan.update(query=query,requires_score=True,clarification_question='Bạn muốn điểm chuẩn trường/ngành Công an nào?')
        return plan
    # Replace the old year when the latest turn names a different one.
    if year:topic=re.sub(r'\b(?:19|20)\d{2}\b',year,topic)
    result=re.sub(r'(?i)(ngành|nganh|nghề|nghe)\s+(đó|do|này|nay)',lambda _:topic,message)
    if year:result=re.sub(r'(?i)(?:năm|nam)\s+(ấy|ay|đó|do)','năm '+year,result)
    if result==message:result=topic+((' năm '+year) if year and year not in topic else '')
    plan['query']=result
    return plan


def public_search_query(session, message):
    return public_search_plan(session,message)['query']
