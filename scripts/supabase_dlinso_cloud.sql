-- Supabase SQL Editor — 여정 · 학습 모듈 클라우드 저장 (dlinso_users + dlinso_conversation_turns)
-- 숲 모듈(isolation_narratives)과 동일 Secrets [supabase] 사용
-- 실행: Supabase Dashboard → SQL → New query → Run

CREATE TABLE IF NOT EXISTS public.dlinso_users (
    nickname                TEXT PRIMARY KEY,
    password_hash           TEXT NOT NULL DEFAULT '',
    lang                    TEXT NOT NULL DEFAULT 'ko',
    gender                  TEXT NOT NULL DEFAULT '',
    age_group               TEXT NOT NULL DEFAULT '',
    life_stage              TEXT NOT NULL DEFAULT '',
    first_visit_at          TIMESTAMPTZ,
    last_visit_at           TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    visit_count             INTEGER NOT NULL DEFAULT 1,
    total_turn_count        INTEGER NOT NULL DEFAULT 0,
    agency                  REAL NOT NULL DEFAULT 50,
    reflection_depth        REAL NOT NULL DEFAULT 50,
    emotional_richness      REAL NOT NULL DEFAULT 50,
    relational_connection   REAL NOT NULL DEFAULT 50,
    life_context            TEXT NOT NULL DEFAULT '',
    narrative_stage         TEXT NOT NULL DEFAULT '',
    last_user_snippet       TEXT NOT NULL DEFAULT '',
    last_assistant_snippet  TEXT NOT NULL DEFAULT '',
    updated_at              TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

COMMENT ON TABLE public.dlinso_users IS
    'dlinso 닉네임·프로필 — Streamlit Cloud 재시작 후 재로그인용.';

CREATE TABLE IF NOT EXISTS public.dlinso_conversation_turns (
    id                  BIGSERIAL PRIMARY KEY,
    created_at          TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    nickname            TEXT NOT NULL DEFAULT '',
    module_type         TEXT NOT NULL DEFAULT 'lifespan',
    turn_type           TEXT NOT NULL DEFAULT 'conversation',
    user_input          TEXT NOT NULL DEFAULT '',
    ai_response         TEXT NOT NULL DEFAULT '',
    user_input_ko       TEXT NOT NULL DEFAULT '',
    ai_response_ko      TEXT NOT NULL DEFAULT '',
    learning_audience   TEXT NOT NULL DEFAULT '',
    is_midpoint         BOOLEAN NOT NULL DEFAULT FALSE,
    is_system           BOOLEAN NOT NULL DEFAULT FALSE,
    metadata_json       JSONB NOT NULL DEFAULT '{}'::jsonb
);

COMMENT ON TABLE public.dlinso_conversation_turns IS
    'dlinso 여정(lifespan) · 학습(learning) 대화 턴 — Cloud 영속 저장.';

CREATE INDEX IF NOT EXISTS idx_dlinso_turns_nickname
    ON public.dlinso_conversation_turns (nickname);

CREATE INDEX IF NOT EXISTS idx_dlinso_turns_created_at
    ON public.dlinso_conversation_turns (nickname, created_at ASC);

CREATE INDEX IF NOT EXISTS idx_dlinso_turns_module
    ON public.dlinso_conversation_turns (nickname, module_type, created_at DESC);

-- RLS (publishable / anon 키 — Streamlit secrets 와 동일 패턴)
ALTER TABLE public.dlinso_users ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.dlinso_conversation_turns ENABLE ROW LEVEL SECURITY;

CREATE POLICY "service_role_all_dlinso_users"
    ON public.dlinso_users FOR ALL TO service_role
    USING (true) WITH CHECK (true);

CREATE POLICY "service_role_all_dlinso_turns"
    ON public.dlinso_conversation_turns FOR ALL TO service_role
    USING (true) WITH CHECK (true);

DROP POLICY IF EXISTS "anon_insert_dlinso_users" ON public.dlinso_users;
CREATE POLICY "anon_insert_dlinso_users"
    ON public.dlinso_users FOR INSERT TO anon WITH CHECK (true);

DROP POLICY IF EXISTS "anon_update_dlinso_users" ON public.dlinso_users;
CREATE POLICY "anon_update_dlinso_users"
    ON public.dlinso_users FOR UPDATE TO anon USING (true) WITH CHECK (true);

DROP POLICY IF EXISTS "anon_select_dlinso_users" ON public.dlinso_users;
CREATE POLICY "anon_select_dlinso_users"
    ON public.dlinso_users FOR SELECT TO anon USING (true);

DROP POLICY IF EXISTS "anon_insert_dlinso_turns" ON public.dlinso_conversation_turns;
CREATE POLICY "anon_insert_dlinso_turns"
    ON public.dlinso_conversation_turns FOR INSERT TO anon WITH CHECK (true);

DROP POLICY IF EXISTS "anon_select_dlinso_turns" ON public.dlinso_conversation_turns;
CREATE POLICY "anon_select_dlinso_turns"
    ON public.dlinso_conversation_turns FOR SELECT TO anon USING (true);
