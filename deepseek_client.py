"""Cấu hình và lỗi DeepSeek dùng chung; không log key, body hoặc URL cấu hình."""
import logging
import os
from urllib.parse import urlsplit

import httpx
from fastapi import HTTPException

logger = logging.getLogger(__name__)


class ProviderConfigurationError(ValueError):
    pass


class ProviderOutputError(ValueError):
    pass


def model_name(summary=False):
    main = os.getenv('DEEPSEEK_MODEL', '').strip() or 'deepseek-flash'
    return (os.getenv('DEEPSEEK_SUMMARY_MODEL', '').strip() or main) if summary else main


async def post_completion(payload, timeout=40, connect=8):
    key = os.getenv('DEEPSEEK_API_KEY', '').strip()
    base = (os.getenv('DEEPSEEK_BASE_URL', '').strip() or 'https://api.deepseek.com').rstrip('/')
    try:
        parsed = urlsplit(base)
        if (parsed.scheme != 'https' or not parsed.hostname or parsed.username or parsed.password
                or parsed.query or parsed.fragment or any(c.isspace() for c in base)):
            raise ValueError()
        parsed.port  # Kiểm tra port không hợp lệ trước khi gửi HTTP.
    except ValueError:
        raise ProviderConfigurationError('invalid_provider_url') from None
    if not key:
        raise ProviderConfigurationError('missing_provider_key')
    try:
        async with httpx.AsyncClient(timeout=httpx.Timeout(timeout, connect=connect)) as client:
            response = await client.post(base + '/chat/completions', json=payload,
                                         headers={'Authorization': 'Bearer ' + key})
            response.raise_for_status()
            return response
    except httpx.InvalidURL:
        raise ProviderConfigurationError('invalid_provider_url') from None


def message_text(response):
    try:
        choice = response.json()['choices'][0]
        text = choice['message']['content']
        if choice.get('finish_reason') not in (None, 'stop') or not isinstance(text, str) or not text.strip():
            raise ValueError()
        return text.strip()
    except (ValueError, KeyError, IndexError, TypeError, AttributeError):
        raise ProviderOutputError('invalid_provider_output') from None


def provider_http_error(error):
    if isinstance(error, ProviderConfigurationError):
        code, status, message = 'configuration', 503, 'Dịch vụ AI chưa được cấu hình đúng. Nhóm dự án cần kiểm tra cấu hình máy chủ.'
    elif isinstance(error, (TimeoutError, httpx.TimeoutException)):
        code, status, message = 'timeout', 504, 'AI phản hồi hơi lâu. Bạn thử gửi lại tin nhắn nhé.'
    elif isinstance(error, httpx.HTTPStatusError):
        upstream = error.response.status_code
        if upstream in (401, 403):
            code, status, message = 'credentials', 503, 'Dịch vụ AI chưa xác thực được. Nhóm dự án cần kiểm tra khóa và quyền API.'
        elif upstream == 402:
            code, status, message = 'balance', 503, 'Dịch vụ AI cần được kiểm tra hạn mức. Bạn thử lại sau nhé.'
        elif upstream == 429:
            code, status, message = 'rate_limit', 503, 'Dịch vụ AI đang giới hạn lượt gọi. Bạn chờ một chút rồi thử lại nhé.'
        elif upstream >= 500:
            code, status, message = 'provider_unavailable', 503, 'Dịch vụ AI đang bận. Bạn thử lại sau nhé.'
        elif upstream in (400, 404, 422):
            code, status, message = 'provider_request', 503, 'Cấu hình model hoặc yêu cầu AI chưa được dịch vụ chấp nhận. Nhóm dự án cần kiểm tra cấu hình.'
        else:
            code, status, message = 'provider_http', 502, 'Chưa nhận được phản hồi hợp lệ từ AI. Bạn thử lại nhé.'
    else:
        code, status, message = 'invalid_reply', 502, 'Chưa nhận được câu trả lời hợp lệ từ AI. Bạn thử gửi lại nhé.'
    logger.warning('deepseek_failure code=%s type=%s', code, type(error).__name__)
    return HTTPException(status, message)
