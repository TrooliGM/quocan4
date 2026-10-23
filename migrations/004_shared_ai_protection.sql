-- Chỉ chạy bởi người vận hành sau khi duyệt, không chạy trong runtime.
-- Additive: không sửa/xóa hội thoại hoặc quota hiện có.
BEGIN;
SET LOCAL lock_timeout = '3s';
SET LOCAL statement_timeout = '30s';
ALTER TABLE guest_ai_requests ADD COLUMN charge_quota BOOLEAN NOT NULL DEFAULT TRUE;
CREATE TABLE advisor_guest_sessions (
    token_hash TEXT PRIMARY KEY,
    uid TEXT NOT NULL UNIQUE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    expires_at TIMESTAMPTZ NOT NULL,
    CHECK (expires_at > created_at)
);
CREATE INDEX advisor_guest_sessions_expiry ON advisor_guest_sessions(expires_at);
COMMIT;
