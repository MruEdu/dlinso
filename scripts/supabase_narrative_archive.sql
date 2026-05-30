-- Supabase SQL Editor — 서사 기록실 (user_sessions + narrative_assets)
-- dlinso_users / dlinso_conversation_turns 와 함께 사용
-- 실행: Supabase Dashboard → SQL → New query → Run

CREATE TABLE IF NOT EXISTS public.user_sessions (
    nickname            TEXT PRIMARY KEY,
    module_type         TEXT NOT NULL DEFAULT 'lifespan',
    session_context     JSONB NOT NULL DEFAULT '{}'::jsonb,
    metadata_json       JSONB NOT NULL DEFAULT '{}'::jsonb,
    turn_count          INTEGER NOT NULL DEFAULT 0,
    asset_progress      REAL NOT NULL DEFAULT 0,
    updated_at          TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

COMMENT ON TABLE public.user_sessions IS
    '서사 기록실 — 대화 문맥·메타데이터·자산화 진척도 (Cloud Memory).';

CREATE TABLE IF NOT EXISTS public.narrative_assets (
    id                  BIGSERIAL PRIMARY KEY,
    created_at          TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    nickname            TEXT NOT NULL DEFAULT '',
    module_type         TEXT NOT NULL DEFAULT 'lifespan',
    raw_narrative       TEXT NOT NULL DEFAULT '',
    core_competencies   JSONB NOT NULL DEFAULT '[]'::jsonb,
    emotion_keywords    JSONB NOT NULL DEFAULT '[]'::jsonb,
    scene_fragments     JSONB NOT NULL DEFAULT '[]'::jsonb,
    deidentified        BOOLEAN NOT NULL DEFAULT TRUE,
    source_snippet      TEXT NOT NULL DEFAULT ''
);

COMMENT ON TABLE public.narrative_assets IS
    '대화에서 추출된 핵심 서사(raw) — 비식별화 저장 · 콘텐츠 원료 프로토타입.';

CREATE INDEX IF NOT EXISTS idx_user_sessions_updated
    ON public.user_sessions (updated_at DESC);

CREATE INDEX IF NOT EXISTS idx_narrative_assets_nickname
    ON public.narrative_assets (nickname, created_at DESC);

ALTER TABLE public.user_sessions ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.narrative_assets ENABLE ROW LEVEL SECURITY;

CREATE POLICY "service_role_all_user_sessions"
    ON public.user_sessions FOR ALL TO service_role
    USING (true) WITH CHECK (true);

CREATE POLICY "service_role_all_narrative_assets"
    ON public.narrative_assets FOR ALL TO service_role
    USING (true) WITH CHECK (true);

DROP POLICY IF EXISTS "anon_insert_user_sessions" ON public.user_sessions;
CREATE POLICY "anon_insert_user_sessions"
    ON public.user_sessions FOR INSERT TO anon WITH CHECK (true);

DROP POLICY IF EXISTS "anon_update_user_sessions" ON public.user_sessions;
CREATE POLICY "anon_update_user_sessions"
    ON public.user_sessions FOR UPDATE TO anon USING (true) WITH CHECK (true);

DROP POLICY IF EXISTS "anon_select_user_sessions" ON public.user_sessions;
CREATE POLICY "anon_select_user_sessions"
    ON public.user_sessions FOR SELECT TO anon USING (true);

DROP POLICY IF EXISTS "anon_insert_narrative_assets" ON public.narrative_assets;
CREATE POLICY "anon_insert_narrative_assets"
    ON public.narrative_assets FOR INSERT TO anon WITH CHECK (true);

DROP POLICY IF EXISTS "anon_select_narrative_assets" ON public.narrative_assets;
CREATE POLICY "anon_select_narrative_assets"
    ON public.narrative_assets FOR SELECT TO anon USING (true);
