# Migration workflow

1. Create migration file (after model change):
```bash
DATABASE_URL=postgresql+psycopg://recipe_user:recipe_pass123@localhost:5432/recipe_db .venv/bin/alembic revision -m "describe_change"
```

2. Edit the new file under:
- versions

3. Apply locally:
```bash
DATABASE_URL=postgresql+psycopg://recipe_user:recipe_pass123@localhost:5432/recipe_db .venv/bin/alembic upgrade head
```

4. Verify current revision:
```bash
DATABASE_URL=postgresql+psycopg://recipe_user:recipe_pass123@localhost:5432/recipe_db .venv/bin/alembic current
```

5. Rebuild/restart app when requirements or startup behavior changed:
```bash
docker compose up -d --build fastapi
```

6. Backup before risky migrations:
```bash
docker compose exec -T db pg_dump -U recipe_user -d recipe_db > db/backups/pre_change_backup.sql
```

7. Roll back one step if needed:
```bash
DATABASE_URL=postgresql+psycopg://recipe_user:recipe_pass123@localhost:5432/recipe_db .venv/bin/alembic downgrade -1
```

## How container stays up to date now

On every FastAPI container start, this command runs automatically:
- alembic upgrade head
- then uvicorn starts

So if the DB is behind, it migrates forward before serving traffic.

Natural next steps

1. Add a small Makefile target set (migrate, rollback, revision, backup) for one-command ops.
2. Add a lightweight migration CI check to fail PRs when model/schema drift is detected.

## Migration 003 smoke tests

Run the reusable smoke test script:

```bash
docker compose exec -T db psql -U recipe_user -d recipe_db < db/scripts/smoke_test_migration_003.sql
```

What to expect:
- Successful checks print selected rows for default and valid insert/update flows.
- Failing checks intentionally trigger constraint errors and then roll back.
- No test data persists because each scenario runs inside a transaction and rolls back.

## Fresh reset test (no local venv required)

This validates that a clean volume init auto-aligns revision history and then auto-applies current migrations.

1. Stop and remove containers plus volume:

```bash
docker compose down -v
```

2. Start stack:

```bash
docker compose up -d --build
```

3. Confirm DB is healthy:

```bash
docker compose ps
```

4. Check Alembic revision in DB (should be head after FastAPI startup migration):

```bash
docker compose exec -T db psql -U recipe_user -d recipe_db -c "SELECT version_num FROM alembic_version;"
```

5. Verify migration 003 columns exist:

```bash
docker compose exec -T db psql -U recipe_user -d recipe_db -c "SELECT column_name FROM information_schema.columns WHERE table_schema='public' AND table_name='recipes' AND column_name IN ('yield_mode','portion_size_grams','total_raw_weight_grams','total_cooked_weight_grams','portions_count_resolved') ORDER BY column_name;"
```

Should see something like:

```bash
 portion_size_grams
 portions_count_resolved
 total_cooked_weight_grams
 total_raw_weight_grams
 yield_mode
(5 rows)
```

6. Run migration smoke tests:

```bash
docker compose exec -T db psql -U recipe_user -d recipe_db < db/scripts/smoke_test_migration_003.sql
```
