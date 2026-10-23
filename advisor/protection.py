"""Shared PostgreSQL admission; never trust client identities or forwarded IP by default."""
import hashlib
import ipaddress
import os
import secrets
from uuid import uuid4

from fastapi import HTTPException, Request, Response

from .guest_quota import connection
from .store import StorageConfigurationError

COOKIE = 'laban_guest'


def cookie_name(request):
    return '__Host-' + COOKIE if os.getenv('VERCEL') or request.url.scheme == 'https' else COOKIE


def setting(name, default, minimum=1, maximum=100000):
    raw = os.getenv(name, str(default))
    try:
        value = int(raw)
        if not minimum <= value <= maximum:
            raise ValueError()
        return value
    except ValueError:
        raise StorageConfigurationError('Cấu hình giới hạn AI không hợp lệ.') from None


def client_ip(request: Request):
    # ASGI server must NOT apply untrusted proxy headers before this function.
    try:
        peer = ipaddress.ip_address(request.client.host)
        networks = [ipaddress.ip_network(v.strip()) for v in os.getenv('AI_TRUSTED_PROXY_CIDRS', '').split(',') if v.strip()]
    except (ValueError, AttributeError):
        raise StorageConfigurationError('Cấu hình proxy AI không hợp lệ.') from None
    if any(peer in network for network in networks):
        if len(request.headers.getlist('x-forwarded-for')) > 1:
            raise HTTPException(400, 'Địa chỉ proxy không hợp lệ.')
        values = request.headers.get('x-forwarded-for', '').split(',')
        if len(values) > 20:
            raise HTTPException(400, 'Địa chỉ proxy không hợp lệ.')
        chain = []
        try:
            chain = [ipaddress.ip_address(v.strip()) for v in values if v.strip()]
        except ValueError:
            raise HTTPException(400, 'Địa chỉ proxy không hợp lệ.') from None
        for address in reversed(chain):
            peer = address
            if not any(peer in network for network in networks):
                break
    return str(peer)


def same_origin(request):
    from urllib.parse import urlsplit
    origin = request.headers.get('origin')
    # A browser's Origin cannot be supplied by script. Never use X-Forwarded-Host.
    expected = os.getenv('AI_PUBLIC_ORIGIN', '').rstrip('/') or str(request.base_url).rstrip('/')
    if request.headers.get('sec-fetch-site') == 'cross-site' or (origin and origin != expected):
        raise HTTPException(403, 'Yêu cầu phải xuất phát từ website La Bàn.')
    parsed = urlsplit(expected)
    if parsed.scheme not in ('http', 'https') or not parsed.netloc:
        raise StorageConfigurationError('Cấu hình origin AI không hợp lệ.')


def key(scope, value):
    return scope + ':' + hashlib.sha256(value.encode()).hexdigest()


def limit(db, name, value, maximum, seconds):
    bucket = key(name, value)
    row = db.execute('''INSERT INTO advisor_chat_rate_limits(uid,window_start,requests) VALUES(%s,NOW(),1)
        ON CONFLICT(uid) DO UPDATE SET
        requests=CASE WHEN advisor_chat_rate_limits.window_start<=NOW()-(%s * INTERVAL '1 second') THEN 1 ELSE advisor_chat_rate_limits.requests+1 END,
        window_start=CASE WHEN advisor_chat_rate_limits.window_start<=NOW()-(%s * INTERVAL '1 second') THEN NOW() ELSE advisor_chat_rate_limits.window_start END
        WHERE advisor_chat_rate_limits.window_start<=NOW()-(%s * INTERVAL '1 second') OR advisor_chat_rate_limits.requests<%s
        RETURNING requests''', (bucket, seconds, seconds, seconds, maximum)).fetchone()
    if not row:
        raise HTTPException(429, {'code': 'AI_RATE_LIMIT', 'message': 'Bạn đã đạt giới hạn sử dụng. Hãy đợi rồi thử lại.'}, headers={'Retry-After': str(seconds)})


def check_ai_rate(request, user, paid=True):
    """One transaction across identity + IP limits, shared by every AI endpoint."""
    from .store import get_store
    from .postgres_adapter import PostgresConversationStore
    if not isinstance(get_store(), PostgresConversationStore):
        # Local SQLite remains usable for authenticated demo only; no paid unlimited fallback.
        if not paid and user.get('provider') != 'anonymous':
            return
        raise StorageConfigurationError('AI cần PostgreSQL để áp dụng giới hạn dùng chung.')
    ip = client_ip(request)
    with connection() as db:
        # Stable global order avoids deadlocks across concurrent identity/IP pairs.
        limit(db, 'ai:ip:minute', ip, setting('AI_IP_PER_MINUTE', 60), 60)
        limit(db, 'ai:ip:day', ip, setting('AI_IP_PER_DAY', 300), 86400)
        limit(db, 'ai:uid:minute', user['uid'], setting('AI_USER_PER_MINUTE', 30), 60)
        limit(db, 'ai:uid:day', user['uid'], setting('AI_USER_PER_DAY', 200), 86400)


def server_guest(request, required=True):
    token = request.cookies.get(cookie_name(request), '')
    if not token or len(token) > 128:
        if required:
            raise HTTPException(401, 'Bạn hãy mở phiên khách trước khi trò chuyện.')
        return None
    with connection() as db:
        row = db.execute('SELECT uid FROM advisor_guest_sessions WHERE token_hash=%s AND expires_at>NOW()', (hashlib.sha256(token.encode()).hexdigest(),)).fetchone()
        if row and db.execute('SELECT 1 FROM advisor_guest_claims WHERE guest_uid=%s', (row['uid'],)).fetchone():
            row = None
    if not row:
        if required:
            raise HTTPException(401, 'Phiên khách đã hết hạn hoặc được chuyển sang tài khoản.')
        return None
    if request.method not in ('GET', 'HEAD', 'OPTIONS'):
        same_origin(request)
    return {'uid': row['uid'], 'provider': 'anonymous', 'server_guest': True}


def issue_guest(request: Request, response: Response):
    same_origin(request)
    from .store import get_store
    from .postgres_adapter import PostgresConversationStore
    if not isinstance(get_store(), PostgresConversationStore):
        raise StorageConfigurationError('Phiên khách cần PostgreSQL dùng chung.')
    existing = server_guest(request, required=False)
    if existing:
        return {'user': existing}
    ip = client_ip(request)
    token, uid = secrets.token_urlsafe(32), 'sg_' + uuid4().hex
    lifetime = setting('AI_GUEST_TTL_SECONDS', 86400, 300, 604800)
    with connection() as db:
        limit(db, 'guest:create:minute', ip, setting('AI_GUEST_CREATE_PER_MINUTE', 3), 60)
        limit(db, 'guest:create:day', ip, setting('AI_GUEST_CREATE_PER_DAY', 10), 86400)
        db.execute("INSERT INTO advisor_guest_sessions(token_hash,uid,expires_at) VALUES(%s,%s,NOW()+(%s * INTERVAL '1 second'))", (hashlib.sha256(token.encode()).hexdigest(), uid, lifetime))
    secure = bool(os.getenv('VERCEL')) or request.url.scheme == 'https'
    response.set_cookie(cookie_name(request), token, max_age=lifetime, httponly=True, secure=secure, samesite='strict', path='/')
    return {'user': {'uid': uid, 'provider': 'anonymous', 'server_guest': True}}
