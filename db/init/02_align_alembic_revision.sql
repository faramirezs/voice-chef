-- Align legacy dump revision to the current Alembic migration chain.
-- This runs only on first database initialization (empty data volume).

DO $$
BEGIN
    IF EXISTS (
        SELECT 1
        FROM information_schema.tables
        WHERE table_schema = 'public'
          AND table_name = 'alembic_version'
    ) THEN
        UPDATE public.alembic_version
        SET version_num = '002'
        WHERE version_num = '003_allergens_additives';

        IF NOT EXISTS (SELECT 1 FROM public.alembic_version) THEN
            INSERT INTO public.alembic_version(version_num) VALUES ('002');
        END IF;
    END IF;
END $$;
