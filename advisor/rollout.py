"""Canary fail-closed: UID từ Firebase đã xác minh, không từ query/header tự khai."""
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
