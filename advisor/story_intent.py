"""Gợi ý truyện từ phân loại ngữ nghĩa + quy tắc dự phòng, chỉ dùng danh mục thật."""
import re
import unicodedata

from career_stories import STORIES
from content import CAREERS

CATALOG = {c['id']: c['name'] for c in CAREERS if c['id'] in STORIES}
ALIASES = {
    'lap-trinh': ('lập trình viên', 'kỹ sư phần mềm', 'software engineer', 'developer', 'coder'),
    'bac-si': ('bác sĩ', 'doctor'),
    'giao-vien': ('giáo viên', 'thầy giáo', 'cô giáo', 'teacher'),
    'thiet-ke': ('nhà thiết kế đồ họa', 'thiết kế đồ họa', 'graphic designer'),
    'ky-su-moi-truong': ('kỹ sư môi trường', 'environmental engineer'),
    'truyen-thong': ('người làm truyền thông', 'chuyên viên truyền thông', 'nhân viên truyền thông'),
}
UNSUPPORTED = ('bác sĩ thú y', 'kiến trúc sư', 'phi công', 'luật sư', 'đầu bếp', 'nha sĩ', 'kỹ sư cơ khí')


def normalize(value):
    value = unicodedata.normalize('NFD', str(value).lower().replace('đ', 'd'))
    return re.sub(r'\s+', ' ', ''.join(c for c in value if unicodedata.category(c) != 'Mn')).strip()


def named_careers(text):
    """Ưu tiên tên dài để không hiểu bác sĩ thú y là truyện bác sĩ."""
    text = normalize(text)
    candidates = [(alias, CATALOG[key]) for key, aliases in ALIASES.items() for alias in aliases]
    candidates += [(name, name.capitalize()) for name in UNSUPPORTED]
    matches, occupied = [], []
    for alias, name in sorted(candidates, key=lambda item: len(item[0]), reverse=True):
        for match in re.finditer(r'(?<!\w)' + re.escape(normalize(alias)) + r'(?!\w)', text):
            if any(match.start() < end and match.end() > start for start, end in occupied):
                continue
            occupied.append(match.span())
            matches.append((match.start(), name))
    return list(dict.fromkeys(name for _, name in sorted(matches)))


def career_id(name):
    name = normalize(name)
    for key, title in CATALOG.items():
        if name in {normalize(title), *(normalize(a) for a in ALIASES.get(key, ()))}:
            return key
    return None


def declined(text):
    return bool(re.search(r'\b(?:khong|chua|dung|khoi)\s+(?:(?:muon|can|thich|dong y)\s+)?(?:mo|xem|chuyen|sang|trai nghiem)\b', normalize(text)))


def fallback_intent(state):
    """Dự phòng khi bước metadata lỗi; không thay phân loại ngữ nghĩa DeepSeek."""
    message = normalize(state['message'])
    daily = bool(re.search(r'\b(mot ngay|hang ngay|moi ngay|sang den toi|lich trinh|ca lam|ca truc|theo chan|mo truyen|xem truyen|trai nghiem.*lam)\b', message))
    names = named_careers(state['message'])
    previous = state.get('session', {}).get('messages', [])
    last = previous[-1].get('story_navigation') if previous else None
    followup = last and last.get('kind') in ('clarify', 'choices') and names and not re.search(r'luong|thu nhap|co hoi|ky nang', message)
    if not daily and not followup:
        return None
    if not names and re.search(r'\b(nghe do|nghe nay|cong viec do|ho|minh se|ngay cua)\b', message):
        for item in reversed(previous[-12:]):
            if item.get('role') == 'user':
                found = named_careers(item.get('content', ''))
                if found:
                    names = found if len(found) == 1 else []
                    break
    if not names:
        # Giữ tên nghề chưa có trong danh mục, không tự bịa ID/URL.
        match = re.search(r'\b(?:cua|lam|nghe)\s+(.+?)(?:\s+(?:nhu the nao|co gi|thu vi|se ra sao)|[?.!]|$)', message)
        if match:
            candidate = match.group(1).strip()
            if candidate and candidate not in ('viec', 'viec cua', 'minh', 'mot ngay', 'nghe nao') and len(candidate) <= 100 and re.fullmatch(r'[\w\s&()/+-]+', candidate):
                names = [candidate]
    return {'intent': 'career_day_experience', 'career_names': names, 'confidence': .8}


def validated_intent(raw):
    if not isinstance(raw, dict) or raw.get('intent') != 'career_day_experience':
        return None
    confidence = raw.get('confidence')
    if isinstance(confidence, bool) or not isinstance(confidence, (int, float)) or not .75 <= confidence <= 1:
        return None
    names = raw.get('career_names', [])
    if not isinstance(names, list):
        return None
    names = [n.strip() for n in names[:6] if isinstance(n, str) and 0 < len(n.strip()) <= 100
             and re.fullmatch(r'[\w\s&()/+-]+', n.strip())]
    return {'intent': 'career_day_experience', 'career_names': list(dict.fromkeys(names)), 'confidence': confidence}


def suggest_story(state):
    reply = dict(state['reply'])
    if declined(state['message']):
        return {'reply': reply}
    # Không kéo câu hỏi lương/kỹ năng sang truyện chỉ vì ngữ cảnh cũ có truyện.
    text = normalize(state['message'])
    if re.search(r'luong|thu nhap|co hoi|ky nang', text) and not re.search(r'mot ngay|hang ngay|moi ngay|lich trinh|sang den toi|truyen', text):
        return {'reply': reply}
    semantic = state.get('story_intent')
    if isinstance(semantic, dict) and semantic.get('intent') == 'none':
        confidence = semantic.get('confidence')
        if type(confidence) in (int, float) and .75 <= confidence <= 1:
            return {'reply': reply}
    intent = validated_intent(state.get('story_intent')) or fallback_intent(state)
    if not intent:
        return {'reply': reply}
    names = intent['career_names']
    choices, missing = [], []
    for name in names:
        key = career_id(name)
        if key and not any(c['career_id'] == key for c in choices):
            choices.append({'career_id': key, 'career_name': CATALOG[key]})
        elif not key:
            missing.append(name)
    if not names:
        kind = 'clarify'
        notice = 'Bạn muốn khám phá một ngày làm việc của nghề nào?'
    elif not choices:
        kind = 'unavailable'
        notice = 'Truyện nghề hiện chưa có nội dung cho ' + ', '.join(missing) + '. Bạn vẫn có thể tiếp tục hỏi La Bàn về nghề này.'
    elif len(names) > 1:
        kind = 'choices'
        notice = 'Bạn muốn khám phá nghề nào trước? Chọn một truyện bên dưới nhé!'
        if missing:
            notice += ' Hiện chưa có truyện cho ' + ', '.join(missing) + '.'
    else:
        kind = 'open'
        notice = f'Mình sẽ đưa bạn đến Truyện nghề để khám phá một ngày làm việc của {choices[0]["career_name"]} nhé!'
    # Metadata chỉ gồm nghề được backend đối chiếu; không dùng URL từ model.
    reply['story_navigation'] = {**intent, 'kind': kind, 'choices': choices}
    reply['answer'] = (reply['answer'][:15500] + '\n\n' + notice) if kind != 'clarify' else notice
    return {'reply': reply}
