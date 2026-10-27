-- Chỉ chạy trên target đã phê duyệt và xác minh qua control plane; không startup.
-- Không thay đổi bảng cũ, không backfill suy luận LLM thành dữ liệu đã đồng ý.
BEGIN;
SET LOCAL lock_timeout='3s';
SET LOCAL statement_timeout='15s';
DO $$ BEGIN
  IF coalesce(current_setting('laban.profile_migration_target',true),'') NOT IN
    ('task4-staging-approved','task4-production:frosty-math-90753534/br-delicate-wave-azxcb1jo/neondb') THEN
    RAISE EXCEPTION 'Thiếu xác nhận đúng target được duyệt';
  END IF;
  IF to_regclass('advisor_sessions') IS NULL OR to_regclass('advisor_guest_claims') IS NULL THEN
    RAISE EXCEPTION 'Cần schema conversation/claim hiện có';
  END IF;
  IF to_regclass('advisor_profile_items') IS NOT NULL THEN
    RAISE EXCEPTION 'Bảng profile đã tồn tại: dừng, đối chiếu schema, không ghi đè';
  END IF;
END $$;
CREATE TABLE advisor_profile_items (
 id UUID PRIMARY KEY,
 owner TEXT NOT NULL,
 category TEXT NOT NULL CHECK(category IN ('interests','strengths','growth_skills','work_preferences','careers','uncertainties')),
 value TEXT NOT NULL CHECK(char_length(value) BETWEEN 3 AND 160),
 confirmed_by TEXT NOT NULL,
 source_session_id TEXT NOT NULL,
 source_proposal_id TEXT NOT NULL,
 metadata JSONB NOT NULL CHECK(jsonb_typeof(metadata)='object'),
 version INTEGER NOT NULL DEFAULT 1 CHECK(version>0),
 created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
 updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
 expires_at TIMESTAMPTZ,
 UNIQUE(owner,source_session_id,source_proposal_id)
);
CREATE INDEX advisor_profile_owner_updated ON advisor_profile_items(owner,updated_at DESC);
CREATE INDEX advisor_profile_expiry ON advisor_profile_items(expires_at) WHERE expires_at IS NOT NULL;
COMMIT;
