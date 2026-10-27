"""Quyền dữ liệu chưa phát hành; không phân chia pipeline hay model hội thoại."""
import os
from fastapi import HTTPException

def controlled():
    return os.getenv('ADVISOR_CONTROLLED_ROLLOUT','true' if os.getenv('VERCEL_ENV')=='production' else 'false')=='true'

def uid_allowed(uid):
    return not controlled() or uid in {s.strip() for s in os.getenv('ADVISOR_TEST_UIDS','').split(',') if s.strip()}
def allowed(user):
    return not controlled() or user.get('provider') in ('google.com','password') and uid_allowed(user.get('uid',''))
def require(user):
    if not allowed(user):raise HTTPException(404,'Chức năng chưa mở cho tài khoản này.')

def search_restricted():
    """Search canary độc lập quyền hồ sơ; Production mặc định đóng cho non-QA."""
    value=os.getenv('SEARCH_QA_ONLY','true' if os.getenv('VERCEL_ENV')=='production' else 'false')
    return value.strip().lower()!='false'

def search_allowed(user):
    if not search_restricted():return True
    # Không dùng uid_allowed(): controlled=false không được mở Search cho mọi UID.
    return user.get('provider') in ('google.com','password') and user.get('uid') in {
        uid.strip() for uid in os.getenv('SEARCH_TEST_UIDS',os.getenv('ADVISOR_TEST_UIDS','')).split(',') if uid.strip()}
