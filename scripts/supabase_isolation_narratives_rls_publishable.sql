-- publishable(sb_publishable_...) / anon 키로 INSERT 하려면 실행
-- service_role / sb_secret_ 키만 쓰면 이 파일은 불필요

CREATE POLICY IF NOT EXISTS "anon_insert_isolation_narratives"
    ON public.isolation_narratives
    FOR INSERT
    TO anon
    WITH CHECK (true);
