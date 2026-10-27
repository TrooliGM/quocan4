-- Schema theo các truy vấn hiện tại; không tự chạy khi khởi động.
-- Chạy trên database thử nghiệm trước, đối chiếu schema thật trước Production.
-- CREATE IF NOT EXISTS không sửa kiểu cột đã tồn tại.
BEGIN;
SET LOCAL lock_timeout = '3s';
SET LOCAL statement_timeout = '30s';
CREATE TABLE IF NOT EXISTS advisor_sessions (
    id TEXT PRIMARY KEY,
    owner TEXT NOT NULL,
    title TEXT NOT NULL,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL,
    messages TEXT NOT NULL,
    profile TEXT NOT NULL,
    summary TEXT NOT NULL
);
CREATE INDEX IF NOT EXISTS advisor_owner ON advisor_sessions(owner, updated_at);
CREATE TABLE IF NOT EXISTS advisor_temporary_sessions (
    id TEXT PRIMARY KEY,
    owner TEXT NOT NULL,
    title TEXT NOT NULL,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL,
    messages TEXT NOT NULL,
    profile TEXT NOT NULL,
    summary TEXT NOT NULL,
    expires_at TIMESTAMPTZ NOT NULL
);
CREATE INDEX IF NOT EXISTS advisor_temporary_owner ON advisor_temporary_sessions(owner, updated_at);
COMMIT;
