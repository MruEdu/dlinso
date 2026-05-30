-- Supabase SQL Editor — 숲 · 연결의 서사 (isolation_narratives)
-- 실행: Supabase Dashboard → SQL → New query → Run

CREATE TABLE IF NOT EXISTS public.isolation_narratives (
    id          BIGSERIAL PRIMARY KEY,
    created_at  TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    nickname    TEXT NOT NULL DEFAULT '',
    user_input  TEXT NOT NULL DEFAULT '',
    ai_response TEXT NOT NULL DEFAULT '',
    signals_json JSONB NOT NULL DEFAULT '{}'::jsonb
);

COMMENT ON TABLE public.isolation_narratives IS
    'dlinso 숲 모듈 — 대화 턴 + 회복 신호(JSON). 로컬 isolation.db 와 이중 저장.';

CREATE INDEX IF NOT EXISTS idx_isolation_narratives_nickname
    ON public.isolation_narratives (nickname);

CREATE INDEX IF NOT EXISTS idx_isolation_narratives_created_at
    ON public.isolation_narratives (created_at DESC);

-- Streamlit: publishable(sb_publishable_...) 또는 secret(sb_secret_...) 키
--   · publishable → 아래 anon INSERT 정책 필요
--   · secret / service_role → RLS 우회(추가 정책 불필요)

ALTER TABLE public.isolation_narratives ENABLE ROW LEVEL SECURITY;

CREATE POLICY "service_role_all_isolation_narratives"
    ON public.isolation_narratives
    FOR ALL
    TO service_role
    USING (true)
    WITH CHECK (true);

-- publishable / anon 키로 서버 INSERT (Streamlit secrets에 publishable 사용 시)
DROP POLICY IF EXISTS "anon_insert_isolation_narratives" ON public.isolation_narratives;
CREATE POLICY "anon_insert_isolation_narratives"
    ON public.isolation_narratives
    FOR INSERT
    TO anon
    WITH CHECK (true);
