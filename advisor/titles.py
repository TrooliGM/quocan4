"""Deterministic topics; no survey text, provider call or schema change."""
from career_library import find_career, catalog, normalize_search
from .survey import ANALYSIS_MESSAGE

DEFAULT_TITLE = 'Một hướng đi mới'

def first_chat_title(session, message, request_id):
    first = session['messages'][0]
    if session['title'] != DEFAULT_TITLE or first.get('manually_renamed'):
        return session['title']
    # Never backfill or rename an existing conversation.
    if sum(m['role'] == 'user' for m in session['messages']) > 1:
        return session['title']
    context = first.get('career_context', {})
    career = find_career(context.get('career_id')) if context.get('mode') == 'career_exploration' else None
    text = normalize_search(message)
    internal = message == ANALYSIS_MESSAGE or request_id == first.get('survey', {}).get('analysis_request_id') or text.startswith(('hay phan tich khao sat', 'phan tich khao sat'))
    if not career and not internal:
        career = next((c for c in catalog().careers if normalize_search(c.name) in text), None)
    if career:
        prefix = 'Một ngày làm ' if not internal and 'mot ngay' in text else 'Kỹ năng nghề ' if not internal and 'ky nang' in text else 'Tìm hiểu nghề '
        name = career.name
        title = prefix + name
    else:
        title = 'Khám phá nghề phù hợp'
    first['title_source'] = 'career' if career else 'discovery'
    return title if len(title) <= 80 else title[:80].rsplit(' ',1)[0]

def mark_manual(messages):
    if messages:
        messages[0]['manually_renamed'] = True
        messages[0]['title_source'] = 'manual'
