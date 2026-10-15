"""Quota khách trong PostgreSQL, có lease và fencing để phục hồi sau gián đoạn."""
import hashlib
import json
from uuid import uuid4

from fastapi import HTTPException

LIMIT = 8
LEASE_SECONDS = 120  # Lớn hơn timeout 90 giây của route; không gia hạn do retry.


def connection():
    from .postgres_store import postgres_connection
    return postgres_connection()


def digest(message):
    return hashlib.sha256(message.encode('utf-8')).hexdigest()


def lock_usage(db, uid):
    db.execute('INSERT INTO guest_ai_usage (uid, used_questions) VALUES (%s, 0) ON CONFLICT (uid) DO NOTHING', (uid,))
    return db.execute('SELECT used_questions FROM guest_ai_usage WHERE uid=%s FOR UPDATE', (uid,)).fetchone()


def ensure_unclaimed(db, uid):
    if db.execute('SELECT 1 FROM advisor_guest_claims WHERE guest_uid=%s', (uid,)).fetchone():
        raise HTTPException(403, {'code': 'GUEST_UPGRADED', 'message': 'Phiên khách đã được chuyển. Hãy đăng nhập tài khoản để tiếp tục.'})


def saved_pair(db, uid, session_id, request_id, lock=False):
    """Không tin status đơn lẻ của phiên bản cũ; kiểm tra cả cặp tin nhắn."""
    for table in ('advisor_sessions', 'advisor_temporary_sessions'):
        row = db.execute(f'SELECT messages FROM {table} WHERE id=%s AND owner=%s' + (' FOR UPDATE' if lock else ''), (session_id, uid)).fetchone()
        if row:
            messages = json.loads(row['messages'])
            user = next((m for m in messages if m.get('request_id') == request_id and m['role'] == 'user'), None)
            answer = next((m for m in messages if m.get('request_id') == request_id and m['role'] == 'assistant'), None)
            if user and answer:
                return user['content']
    return None


def settle_locked(db, uid, request, success):
    if request['status'] != 'reserved':
        return request['status']
    # Một response đã commit luôn được tính lượt, kể cả HTTP response bị mất.
    if not success:
        success = saved_pair(db, uid, str(request['session_id']), str(request['request_id']), lock=True) is not None
    status = 'completed' if success else 'failed'
    db.execute('UPDATE guest_ai_requests SET status=%s, updated_at=NOW(), lease_until=NULL WHERE request_id=%s AND uid=%s', (status, request['request_id'], uid))
    if not success:
        db.execute('UPDATE guest_ai_usage SET used_questions=GREATEST(used_questions-1,0), updated_at=NOW() WHERE uid=%s', (uid,))
    return status


def recover_expired(db, uid):
    rows = db.execute("""SELECT * FROM guest_ai_requests WHERE uid=%s AND status='reserved'
        AND COALESCE(lease_until, updated_at + INTERVAL '120 seconds') <= NOW()
        ORDER BY request_id FOR UPDATE""", (uid,)).fetchall()
    for request in rows:
        settle_locked(db, uid, request, False)


def usage_payload(used):
    return {'limit': LIMIT, 'used_questions': used, 'remaining': max(0, LIMIT-used)}


def get_guest_usage(uid):
    with connection() as db:
        lock_usage(db, uid)
        ensure_unclaimed(db, uid)
        recover_expired(db, uid)
        used = db.execute('SELECT used_questions FROM guest_ai_usage WHERE uid=%s', (uid,)).fetchone()['used_questions']
        return usage_payload(used)


def reserve_guest_request(uid, session_id, request_id, message=None):
    """new_reservation chỉ đúng khi transaction này thực sự tăng bộ đếm."""
    with connection() as db:
        lock_usage(db, uid)
        ensure_unclaimed(db, uid)
        recover_expired(db, uid)
        previous = db.execute('SELECT * FROM guest_ai_requests WHERE request_id=%s FOR UPDATE', (request_id,)).fetchone()
        used = db.execute('SELECT used_questions FROM guest_ai_usage WHERE uid=%s', (uid,)).fetchone()['used_questions']
        hashed = digest(message) if message is not None else None
        if previous:
            if previous['uid'] != uid or str(previous['session_id']) != str(session_id):
                raise HTTPException(409, 'Mã yêu cầu đã được sử dụng cho cuộc trò chuyện khác.')
            if previous['message_hash'] and hashed and previous['message_hash'] != hashed:
                raise HTTPException(409, 'Mã tin nhắn đã được sử dụng cho nội dung khác.')
            if previous['status'] != 'failed':
                return {**usage_payload(used), 'status': previous['status'], 'new_reservation': False}
        if used >= LIMIT:
            raise HTTPException(403, {'code': 'GUEST_LIMIT_REACHED', 'message': 'Bạn đã dùng hết 8 câu hỏi miễn phí. Đăng nhập Google hoặc email để tiếp tục.', **usage_payload(used)})
        token = str(uuid4())
        if previous:
            db.execute("""UPDATE guest_ai_requests SET status='reserved', reservation_token=%s,
                message_hash=COALESCE(message_hash,%s), lease_until=NOW()+INTERVAL '120 seconds', updated_at=NOW()
                WHERE request_id=%s AND uid=%s""", (token, hashed, request_id, uid))
        else:
            inserted = db.execute("""INSERT INTO guest_ai_requests
                (request_id,uid,session_id,status,message_hash,reservation_token,lease_until)
                VALUES (%s,%s,%s,'reserved',%s,%s,NOW()+INTERVAL '120 seconds')
                ON CONFLICT (request_id) DO NOTHING RETURNING request_id""", (request_id, uid, session_id, hashed, token)).fetchone()
            if not inserted:
                raise HTTPException(409, 'Mã yêu cầu đang được sử dụng. Hãy gửi lại đúng yêu cầu ban đầu.')
        db.execute('UPDATE guest_ai_usage SET used_questions=used_questions+1, updated_at=NOW() WHERE uid=%s', (uid,))
        return {**usage_payload(used+1), 'status': 'reserved', 'new_reservation': True, 'reservation_token': token}


def lock_request_for_save(db, uid, session_id, request_id, message, reservation_token):
    """Thứ tự khóa luôn usage -> request -> session, cùng với finish/recovery."""
    previous = db.execute('SELECT uid FROM guest_ai_requests WHERE request_id=%s', (request_id,)).fetchone()
    if not previous:
        if reservation_token:
            raise HTTPException(409, 'Lượt giữ không còn hợp lệ.')
        return None
    if previous['uid'] != uid:
        raise HTTPException(409, 'Mã yêu cầu đã được sử dụng.')
    lock_usage(db, uid)
    request = db.execute('SELECT *, lease_until > NOW() AS lease_valid FROM guest_ai_requests WHERE request_id=%s AND uid=%s FOR UPDATE', (request_id, uid)).fetchone()
    if str(request['session_id']) != str(session_id) or (request['message_hash'] and request['message_hash'] != digest(message)):
        raise HTTPException(409, 'Nội dung hoặc cuộc trò chuyện không khớp mã yêu cầu.')
    if reservation_token and (request['reservation_token'] != reservation_token or (request['status'] != 'completed' and (request['status'] != 'reserved' or not request['lease_valid']))):
        raise HTTPException(409, {'code': 'GUEST_RESERVATION_EXPIRED', 'message': 'Lượt xử lý đã hết hạn. Bạn gửi lại tin nhắn để thử nhé.'})
    return request


def finish_guest_request(uid, request_id, success, reservation_token):
    with connection() as db:
        lock_usage(db, uid)
        request = db.execute('SELECT * FROM guest_ai_requests WHERE request_id=%s AND uid=%s FOR UPDATE', (request_id, uid)).fetchone()
        if not request:
            return 'missing'
        if request['reservation_token'] != reservation_token:
            return request['status']  # Worker cũ không được hoàn lượt của worker mới.
        if success and saved_pair(db, uid, str(request['session_id']), request_id, lock=True) is None:
            raise ValueError('Chưa có cặp tin nhắn đã lưu; không thể xác nhận lượt.')
        return settle_locked(db, uid, request, success)


def check_chat_rate(uid):
    """Giới hạn tốc độ độc lập quota khách, áp dụng cả Google/email."""
    with connection() as db:
        row = db.execute("""INSERT INTO advisor_chat_rate_limits(uid,window_start,requests) VALUES(%s,NOW(),1)
            ON CONFLICT(uid) DO UPDATE SET
              requests=CASE WHEN advisor_chat_rate_limits.window_start <= NOW()-INTERVAL '1 minute' THEN 1 ELSE advisor_chat_rate_limits.requests+1 END,
              window_start=CASE WHEN advisor_chat_rate_limits.window_start <= NOW()-INTERVAL '1 minute' THEN NOW() ELSE advisor_chat_rate_limits.window_start END
            WHERE advisor_chat_rate_limits.window_start <= NOW()-INTERVAL '1 minute' OR advisor_chat_rate_limits.requests < 30
            RETURNING requests""", (uid,)).fetchone()
        if not row:
            raise HTTPException(429, {'code': 'CHAT_RATE_LIMIT', 'message': 'Bạn gửi hơi nhanh. Hãy đợi một phút rồi thử lại.'}, headers={'Retry-After': '60'})


def claim_guest_history(guest_uid, account_uid):
    """Chỉ gọi sau khi route xác minh cả hai ID token; chuyển owner, không xóa dữ liệu."""
    if guest_uid == account_uid:
        return {'transferred': False, 'session_ids': []}
    with connection() as db:
        lock_usage(db, guest_uid)
        existing = db.execute('SELECT account_uid FROM advisor_guest_claims WHERE guest_uid=%s', (guest_uid,)).fetchone()
        if existing:
            if existing['account_uid'] != account_uid:
                raise HTTPException(409, 'Lịch sử khách đã liên kết với tài khoản khác.')
            return {'transferred': False, 'session_ids': []}
        recover_expired(db, guest_uid)
        if db.execute("SELECT 1 FROM guest_ai_requests WHERE uid=%s AND status='reserved' LIMIT 1", (guest_uid,)).fetchone():
            raise HTTPException(409, {'code': 'GUEST_REQUEST_PENDING', 'message': 'AI đang xử lý tin nhắn của khách. Chờ xong rồi thử giữ lịch sử lại nhé.'})
        db.execute('INSERT INTO advisor_guest_claims(guest_uid,account_uid) VALUES(%s,%s)', (guest_uid, account_uid))
        ids = []
        for table in ('advisor_sessions', 'advisor_temporary_sessions'):
            rows = db.execute(f'UPDATE {table} SET owner=%s WHERE owner=%s RETURNING id', (account_uid, guest_uid)).fetchall()
            ids.extend(str(r['id']) for r in rows)
        return {'transferred': True, 'session_ids': ids}
