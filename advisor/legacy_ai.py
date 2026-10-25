"""Legacy response shapes, with the same identity/quota/save fencing as chat."""
import asyncio
import json
from uuid import NAMESPACE_URL, uuid5

from fastapi import HTTPException

from .guest_quota import reserve_guest_request, finish_guest_request, get_guest_usage, connection
from .postgres_store import save_messages_atomic
from .protection import check_ai_rate
from .store import empty_profile, now, get_store
from .postgres_adapter import PostgresConversationStore


async def run_legacy(request, user, request_id, message, scope, graph, state):
    if not isinstance(get_store(), PostgresConversationStore):
        raise HTTPException(503, 'AI cần PostgreSQL để bảo vệ quota dùng chung.')
    uid = user['uid']
    sid = str(uuid5(NAMESPACE_URL, uid + ':' + scope + ':' + request_id))
    # Identifiers are server-derived, never accept a caller's owner/session/role.
    stamp = now()
    store = get_store()
    try:
        current = store.get(uid, sid)
    except HTTPException as error:
        if error.status_code != 404:
            raise
        current = None
    if current:
        for item in current['messages']:
            if item.get('request_id') == request_id and item['role'] == 'user' and item['content'] != message:
                raise HTTPException(409, 'Mã tin nhắn đã được sử dụng cho nội dung khác.')
        cached = next((m for m in current['messages'] if m.get('request_id') == request_id and m['role'] == 'assistant'), None)
        if cached is not None:
            return {'answer':cached['content'],'sources':cached.get('sources',[]),'search_status':cached.get('search_status','not_needed'),
                    'duplicate':True,'pipeline':'saved_response','request_id':request_id,
                    'guest_quota':get_guest_usage(uid) if user.get('provider') == 'anonymous' else None}
    await asyncio.to_thread(check_ai_rate, request, user)
    with connection() as db:
        db.execute('''INSERT INTO advisor_temporary_sessions
            (id,owner,title,created_at,updated_at,messages,profile,summary,expires_at)
            VALUES(%s,%s,%s,%s,%s,%s,%s,'',NOW()+INTERVAL '2 hours') ON CONFLICT(id) DO NOTHING''',
            (sid, uid, 'Hỏi về nghề', stamp, stamp, json.dumps([{'role':'assistant','content':'Hỏi về nghề','survey_required':False,'legacy_scope':scope}]), json.dumps(empty_profile())))
    current = store.get(uid, sid)
    for item in current['messages']:
        if item.get('request_id') == request_id and item['role'] == 'user' and item['content'] != message:
            raise HTTPException(409, 'Mã tin nhắn đã được sử dụng cho nội dung khác.')
    cached = next((m for m in current['messages'] if m.get('request_id') == request_id and m['role'] == 'assistant'), None)
    guest = user.get('provider') == 'anonymous'
    if cached is not None:
        return {'answer': cached['content'],'sources':cached.get('sources',[]),'search_status':cached.get('search_status','not_needed'),
                'duplicate': True, 'pipeline':'saved_response','request_id': request_id,
                'guest_quota': get_guest_usage(uid) if guest else None}
    reservation = None
    try:
        reservation = await asyncio.to_thread(reserve_guest_request, uid, sid, request_id, message, guest)
        if not reservation['new_reservation']:
            raise HTTPException(409, {'code':'AI_REQUEST_PENDING','message':'Yêu cầu đang xử lý hoặc đã hoàn thành. Bạn thử tải lại nhé.'})
        # Same row lease/fencing as chat, compatible with transaction pooling.
        # No database connection/transaction is held while the provider runs.
        result = await graph.ainvoke({**state,'uid':uid,'session_id':sid,'request_id':request_id,
            'session':current,'profile':current['profile'],'confirmed_profile_access':False})
        answer = result.get('answer')
        if not isinstance(answer, str) or not answer.strip():
            raise ValueError('Invalid AI answer')
        reply = result.get('reply') or {'answer':answer,'profile':empty_profile(),'summary':'','recommendations':[]}
        await asyncio.to_thread(save_messages_atomic, uid, sid, request_id, message, reply, 'live', reservation['reservation_token'])
        return {'answer':answer,'duplicate':False,'request_id':request_id,'pipeline':'task41',
                'sources':reply.get('sources',[]),'search_status':reply.get('search_status','not_needed'),
                'guest_quota': get_guest_usage(uid) if guest else None}
    except BaseException:
        if reservation and reservation.get('new_reservation'):
            # Reads saved pair before any refund; save + quota complete are atomic.
            await asyncio.shield(asyncio.to_thread(finish_guest_request, uid, request_id, False, reservation['reservation_token']))
        raise
