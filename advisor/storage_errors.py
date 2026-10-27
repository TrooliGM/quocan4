"""Phân loại lỗi storage mà không đưa DSN/SQL/dữ liệu vào response hoặc log."""
import psycopg
from .store import StorageConfigurationError


def storage_error(error):
    if isinstance(error, StorageConfigurationError):
        code = 'DATABASE_CONFIGURATION'
        message = 'Chưa cấu hình database phù hợp. Nhóm dự án cần kiểm tra DATABASE_URL cho đúng môi trường triển khai.'
    elif isinstance(error, (psycopg.errors.UndefinedTable, psycopg.errors.UndefinedColumn)):
        code = 'DATABASE_SCHEMA_MISSING'
        message = 'Database chưa đủ cấu trúc lưu hội thoại hoặc quota. Nhóm dự án cần kiểm tra migration.'
    elif isinstance(error, psycopg.errors.InsufficientPrivilege):
        code = 'DATABASE_PERMISSION'
        message = 'Database chưa cấp đủ quyền cho ứng dụng. Nhóm dự án cần kiểm tra quyền truy cập.'
    elif isinstance(error, (psycopg.OperationalError, psycopg.InterfaceError)):
        code = 'DATABASE_UNAVAILABLE'
        message = 'Chưa kết nối được database hoặc database đang bận. Bạn thử lại sau nhé.'
    else:
        code = 'DATABASE_OPERATION_FAILED'
        message = 'Chưa xác nhận được thao tác lưu dữ liệu. Bạn giữ nguyên tin nhắn và thử lại nhé.'
    return 503, {'code': code, 'message': message}
