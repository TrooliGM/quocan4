"""Quyền tính năng đã phát hành công khai cho Guest và Member.

Danh tính phải được backend xác minh (Firebase hoặc phiên Guest ký bởi server).
Không nhận UID hay provider từ tham số mà người dùng tự khai. Các giới hạn
quyền sở hữu, TTL, quota và xác nhận lưu hồ sơ vẫn do các tầng riêng thực thi.
"""
import os
from fastapi import HTTPException

VALID_PROVIDERS = frozenset(('anonymous', 'google.com', 'password'))

def controlled():
    """Tương thích cũ: đã kết thúc rollout theo danh sách UID QA."""
    return False

def uid_allowed(uid):
    # Dùng khi chuyển dữ liệu Guest sang thành viên đã xác thực; không còn QA allowlist.
    return isinstance(uid, str) and bool(uid.strip())

def allowed(user):
    return (isinstance(user, dict) and
            user.get('provider') in VALID_PROVIDERS and
            uid_allowed(user.get('uid')))

def require(user):
    if not allowed(user):
        raise HTTPException(404, 'Chức năng không khả dụng cho phiên đăng nhập này.')

def search_restricted():
    """Công khai Search; chỉ chặn toàn bộ khi có công tắc sự cố rõ ràng.

    SEARCH_QA_ONLY/SEARCH_TEST_UIDS là cấu hình legacy, không còn chia quyền
    theo QA. SEARCH_PUBLIC_ENABLED=false tắt provider cho mọi tài khoản.
    """
    return os.getenv('SEARCH_PUBLIC_ENABLED', 'true').strip().lower() != 'true'

def search_allowed(user):
    return allowed(user) and not search_restricted()
