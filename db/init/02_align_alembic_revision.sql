-- Align dump-initialized revision marker to current Alembic head.
-- This runs only on first database initialization (empty data volume).

DO $$
BEGIN
    IF EXISTS (
        SELECT 1
        FROM information_schema.tables
        WHERE table_schema = 'public'
          AND table_name = 'alembic_version'
    ) THEN
        -- Normalize any pre-existing marker to the current migration head.
        UPDATE public.alembic_version
        SET version_num = '012'
        WHERE version_num <> '012';

        IF NOT EXISTS (
            SELECT 1 FROM public.alembic_version WHERE version_num = '012'
        ) THEN
            INSERT INTO public.alembic_version(version_num) VALUES ('012');
        END IF;
    END IF;
END $$;
