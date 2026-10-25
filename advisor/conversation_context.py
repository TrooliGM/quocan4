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
    short = bool(re.search(r'ngan gon|ngan thoi|mot cau|[123] cau|chi.*mot so', text))
    deep = bool(re.search(r'phan tich sau|chi tiet|nghien cuu|ky hon', text))
    limit = 800 if short or intent == 'social' else 3500 if deep else 2600 if intent in ('compare', 'plan', 'research') else 2000
    career = (session.get('messages') or [{}])[0].get('career_context', {})
    return {'intent':intent, 'detail':'brief' if short else 'deep' if deep else 'adaptive',
            'max_tokens':limit, 'mode':career.get('mode','career_discovery'),
            'career_id':career.get('career_id')}


def bounded_history(messages, budget=12000):
    """Giữ phần gần nhất và tối đa hai lời chia sẻ đầu; không tải toàn bộ chat vào model."""
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


def public_search_query(session, message):
    """Chỉ thêm chủ đề công khai của nghề/câu tra cứu trước, không thêm survey/profile."""
    text=plain(message)
    reference=bool(re.search(r'nganh (do|nay)|nghe (do|nay)|nam (ay|do)',text))
    if not reference:return message
    career=(session.get('messages') or [{}])[0].get('career_context',{})
    topic=career.get('career_name')
    year=None
    from .search_provider import needs_search
    for row in reversed(session.get('messages',[])):
        if row['role']!='user':continue
        previous=row['content']
        # Không dùng một đoạn tự giới thiệu/hồ sơ cá nhân làm truy vấn trước.
        if re.search(r'ten la|dia chi|mat khau|toi thich|em thich|minh thich',plain(previous)):continue
        if needs_search(previous):
            topic=topic or previous[:200]
            match=re.search(r'\b(?:19|20)\d{2}\b',previous)
            if match:year=match[0]
            break
    result=message
    if topic:result=re.sub(r'(?i)(ngành|nganh|nghề|nghe)\s+(đó|do|này|nay)',lambda _:topic,result)
    if year:result=re.sub(r'(?i)(?:năm|nam)\s+(ấy|ay|đó|do)','năm '+year,result)
    return result
