"""Firebase Web config và xác minh ID token bằng khóa công khai của Google."""
import json
import os
import re
import threading
import time
from types import SimpleNamespace

import httpx
from fastapi import HTTPException
from google.auth import exceptions, jwt
from google.oauth2 import id_token

CERT_URL = "https://www.googleapis.com/robot/v1/metadata/x509/securetoken@system.gserviceaccount.com"
_certificate_lock = threading.Lock()
_certificate_cache = {"data": b"", "expires": 0.0}


def web_config():
    # Chỉ xuất cấu hình Web công khai, không xuất toàn bộ environment.
    fields = {"apiKey": "FIREBASE_API_KEY", "authDomain": "FIREBASE_AUTH_DOMAIN",
              "projectId": "FIREBASE_PROJECT_ID", "appId": "FIREBASE_APP_ID",
              "messagingSenderId": "FIREBASE_MESSAGING_SENDER_ID"}
    config = {key: os.getenv(env, "").strip() for key, env in fields.items()}
    configured = all(config[key] for key in ["apiKey", "authDomain", "projectId", "appId"])
    return {"configured": configured, "config": config if configured else None}


def _certificate_request(url, method="GET", **kwargs):
    """Transport cho google-auth; cache theo max-age của chứng thư."""
    if url != CERT_URL or method != "GET":
        raise exceptions.TransportError("Unexpected certificate endpoint")
    with _certificate_lock:
        if time.monotonic() >= _certificate_cache["expires"]:
            try:
                response = httpx.get(CERT_URL, timeout=8)
                response.raise_for_status()
                certificates = response.json()
                if not isinstance(certificates, dict) or not certificates:
                    raise ValueError("Invalid certificates")
                max_age = re.search(r"max-age=(\d+)", response.headers.get("cache-control", ""))
                ttl = int(max_age.group(1)) if max_age else 0
                _certificate_cache.update(data=json.dumps(certificates).encode(), expires=time.monotonic() + ttl)
            except (httpx.HTTPError, ValueError) as error:
                raise exceptions.TransportError("Certificate service unavailable") from error
        return SimpleNamespace(status=200, data=_certificate_cache["data"])


def verify_user(token: str):
    project_id = os.getenv("FIREBASE_PROJECT_ID", "").strip()
    if not project_id:
        raise HTTPException(503, "Đăng nhập đang được thiết lập. Bạn quay lại sau nhé.")
    try:
        header = jwt.decode_header(token)
        if not isinstance(header, dict) or header.get("alg") != "RS256" or not isinstance(header.get("kid"), str) or not header["kid"]:
            raise ValueError("Invalid token header")
        claims = id_token.verify_firebase_token(token, _certificate_request, audience=project_id)
        if claims.get("iss") != f"https://securetoken.google.com/{project_id}":
            raise ValueError("Invalid issuer")
        uid = claims.get("sub")
        if not isinstance(uid, str) or not uid or len(uid) > 128:
            raise ValueError("Invalid subject")
        auth_time = claims.get("auth_time")
        if type(auth_time) not in (int, float) or not 0 <= auth_time <= time.time():
            raise ValueError("Invalid authentication time")
    except exceptions.TransportError:
        raise HTTPException(503, "Chưa kết nối được dịch vụ xác thực. Bạn thử lại nhé.") from None
    except (ValueError, TypeError, KeyError, exceptions.GoogleAuthError):
        raise HTTPException(401, "Phiên đăng nhập không hợp lệ hoặc đã hết hạn. Bạn đăng nhập lại nhé.",
                            headers={"WWW-Authenticate": "Bearer"}) from None
    provider_claims = claims.get("firebase")
    provider = provider_claims.get("sign_in_provider", "") if isinstance(provider_claims, dict) else ""
    return {"uid": uid, "email": claims.get("email", ""), "display_name": claims.get("name", ""),
            "email_verified": claims.get("email_verified") is True,
            "provider": provider}
