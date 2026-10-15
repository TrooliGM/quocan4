-- Chạy bằng tài khoản migration trên database thử nghiệm trước.
-- Không tự chạy khi ứng dụng khởi động. Không xóa/reset dữ liệu hiện có.
CREATE TABLE IF NOT EXISTS guest_ai_usage (
    uid TEXT PRIMARY KEY,
    used_questions INTEGER NOT NULL DEFAULT 0,
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
CREATE TABLE IF NOT EXISTS guest_ai_requests (
    request_id TEXT PRIMARY KEY,
    uid TEXT NOT NULL,
    session_id TEXT NOT NULL,
    status TEXT NOT NULL,
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
ALTER TABLE guest_ai_requests ADD COLUMN IF NOT EXISTS message_hash TEXT;
ALTER TABLE guest_ai_requests ADD COLUMN IF NOT EXISTS reservation_token TEXT;
ALTER TABLE guest_ai_requests ADD COLUMN IF NOT EXISTS lease_until TIMESTAMPTZ;
CREATE INDEX IF NOT EXISTS guest_ai_requests_uid_status ON guest_ai_requests(uid, status);
CREATE TABLE IF NOT EXISTS advisor_guest_claims (
    guest_uid TEXT PRIMARY KEY,
    account_uid TEXT NOT NULL,
    claimed_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
CREATE TABLE IF NOT EXISTS advisor_chat_rate_limits (
    uid TEXT PRIMARY KEY,
    window_start TIMESTAMPTZ NOT NULL,
    requests INTEGER NOT NULL
);
