# Migration workflow

## Drift gate runbook

Use this section for fast schema parity checks before/after model changes.

### 1) Prerequisites

```bash
docker compose up -d db
source .venv/bin/activate
export DATABASE_URL=postgresql+psycopg://recipe_user:recipe_pass123@localhost:5432/recipe_db
```

### 2) Full gate (all metadata)

Recommended one-command local run (matches CI strict Gate 4 policy):

```bash
make drift-gate-local
```

Log output:

```bash
logs/drift_gate_local.log
```

Manual equivalent:

1. Migration state check:

```bash
.venv/bin/alembic -c alembic.ini -x db_url="$DATABASE_URL" current
```

2. Programmatic drift check:

```bash
.venv/bin/python db/scripts/drift_check.py
```

3. Pytest drift suite:

```bash
.venv/bin/pytest db/test/test_schema_drift.py --test-alembic -q
```

4. Pending-autogenerate check (manual review):

```bash
DATABASE_URL="$DATABASE_URL" .venv/bin/alembic -c alembic.ini revision --autogenerate -m "drift_check_tmp"
```

If the generated revision contains no operations, pending drift is effectively zero. Delete the temporary revision after review.

```bash
rm db/alembic/versions/*_drift_check_tmp.py
```

Note:
- CI-equivalent Gate 4 policy fails on any pending autogenerate operation.
- Treat every pending `op.create*`, `op.drop*`, `op.add*`, or `op.alter*` as actionable drift.

### 3) Scoped gate examples (split-model work)

Check only Users/Tenants/Recipes:

```bash
.venv/bin/python db/scripts/drift_check.py --class Users --class Tenants --class Recipes
.venv/bin/pytest db/test/test_schema_drift.py --test-alembic --drift-class Users --drift-class Tenants --drift-class Recipes -q
```

Check one table only:

```bash
.venv/bin/python db/scripts/drift_check.py --table users
```

### 4) What output to trust

- `Model metadata loaded from`: all modules imported to build SQLModel metadata.
- `Effective scope sources`: exact source file for each selected table.
- `Requested classes`: class -> table -> source mapping for `--class` selectors.

If scope is small but many files are listed, that is expected. Only `Effective scope sources` and `Requested classes` describe what is evaluated.

### 5) Troubleshooting

- `ModuleNotFoundError: No module named 'app'`:
	use the repo-root command form shown above (the script now bootstraps package paths).
- Drift on one table only:
	run with `--table <name>` and patch model to DB truth or DB to model truth based on your migration policy.
- Alembic at head but drift exists:
	this means runtime schema differs from current metadata; head revision alone does not guarantee parity.

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

## Dump safety and regeneration

Use these commands to keep dump-based local bootstrap aligned with migration head.

1. Blast-radius safety check (fresh dump-init DB, then `alembic upgrade head`):

```bash
make dump-blast-check
```

Log output:

```bash
logs/dump_upgrade_blast_check.log
```

2. Regenerate `db/init/01_dump.sql` from migration head:

```bash
make dump-regen
```

Important:
- `make dump-regen` resets DB volume.
- After regeneration, review `db/init/02_align_alembic_revision.sql` and align/remove revision pinning as needed.

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

## Reconciliation and canonical backfill (004)

Use this flow on legacy databases restored from dump files where canonical 002 fields may be missing.

1. Apply reconciliation migration:

```bash
DATABASE_URL=postgresql+psycopg://recipe_user:recipe_pass123@localhost:5432/recipe_db .venv/bin/alembic upgrade 004
```

2. Run canonical backfill (quantity_grams, price_per_gram, recipe totals):

```bash
docker compose exec -T db psql -U recipe_user -d recipe_db < db/scripts/backfill_canonical_fields.sql
```

3. Run full audit report:

```bash
docker compose exec -T db psql -U recipe_user -d recipe_db < db/scripts/audit_cost_schema_state.sql
```

Expected outcomes after backfill:
- Canonical schema objects from 002 + 003 show as present (except tables absent in legacy source, such as shopping_list_items).
- price_per_gram null rate decreases significantly.
- canonical coverage (ingredient_id + quantity_grams + price_per_gram) should be much higher than exact unit match.

## Latest price policy (005)

`ingredient_prices` stores price history by design. To guarantee deterministic behavior everywhere,
always read from the view `public.ingredient_prices_latest`.

Rules used by the view:
- partition key: `(ingredient_id, unit)`
- winner row: latest by `updated_at DESC`, then `created_at DESC`, then `id DESC`

Apply migration:

```bash
DATABASE_URL=postgresql+psycopg://recipe_user:recipe_pass123@localhost:5432/recipe_db .venv/bin/alembic upgrade 005
```

Example usage:

```sql
SELECT ingredient_id, unit, price_per_unit, price_per_gram, currency
FROM public.ingredient_prices_latest
WHERE ingredient_id = '<ingredient_uuid>';
```

## Piece-unit conversions for unresolved prices

As of Alembic `006`, default conversions for the 7 unresolved piece-unit rows are seeded automatically,
and `price_per_gram` is backfilled in migration flow.

If you need to override these defaults with your own business values, use the scripts below.

Apply migration:

```bash
DATABASE_URL=postgresql+psycopg://recipe_user:recipe_pass123@localhost:5432/recipe_db .venv/bin/alembic upgrade 006
```

1. Fill grams-per-piece values for the exact 7 unresolved ingredients:

```bash
docker compose exec -T db psql -U recipe_user -d recipe_db < db/scripts/template_piece_unit_conversions.sql
```

2. Apply `price_per_gram` updates from those conversions:

```bash
docker compose exec -T db psql -U recipe_user -d recipe_db < db/scripts/apply_price_per_gram_from_piece_conversions.sql
```

3. Re-run the audit:

```bash
docker compose exec -T db psql -U recipe_user -d recipe_db < db/scripts/audit_cost_schema_state.sql
```

## Duplicate ingredient merge (007)

Alembic `007` merges confirmed case-only duplicates while preserving links:
- `Knoblauch` -> `knoblauch`
- `Olivenol` -> `olivenol`
- `Tomatenmark` -> `tomatenmark`

What it preserves:
- recipe links (`recipe_ingredients`)
- cost links (`ingredient_prices`)
- nutrition links and values (`ingredient_nutrition`)
- metadata such as `bls_key`

Apply migration:

```bash
DATABASE_URL=postgresql+psycopg://recipe_user:recipe_pass123@localhost:5432/recipe_db .venv/bin/alembic upgrade 007
```

Verify canonical rows and moved price history:

```bash
docker compose exec -T db psql -U recipe_user -d recipe_db -c "SELECT id, name, bls_key FROM ingredients WHERE id IN ('5adfcc26-f8b0-5f48-8191-b118ea08f87d','957a285e-889a-5f8e-9fcc-b73bfd7304ea','c4174230-c859-5c6e-8d91-0d1dd2081aef');"
```

```bash
docker compose exec -T db psql -U recipe_user -d recipe_db -c "SELECT ingredient_id, COUNT(*) AS price_rows FROM ingredient_prices WHERE ingredient_id IN ('5adfcc26-f8b0-5f48-8191-b118ea08f87d','957a285e-889a-5f8e-9fcc-b73bfd7304ea','c4174230-c859-5c6e-8d91-0d1dd2081aef') GROUP BY ingredient_id ORDER BY ingredient_id;"
```

## User-confirmed cleanup migration (011)

Alembic `011` applies the approved cleanup scope:

- drops table: `public.ingredient_merge_audit`
- drops sequence: `public.ingredient_merge_audit_id_seq`
- drops columns from `public.recipes`:
	- `branch_ids`
	- `preference_price`
	- `ingredient_list_product_pass`
	- `preference_allergens`
	- `layout_id`
	- `row_height`
	- `rezeptblatt_image_width`
	- `vat_rate`
	- `sales_price_points`
	- `bio_label_eu`

Apply migration:

```bash
DATABASE_URL=postgresql+psycopg://recipe_user:recipe_pass123@localhost:5432/recipe_db .venv/bin/alembic upgrade 011
```

Rollback this cleanup only:

```bash
DATABASE_URL=postgresql+psycopg://recipe_user:recipe_pass123@localhost:5432/recipe_db .venv/bin/alembic downgrade 010
```

Notes:

- Migration `011` is idempotent for drops via `IF EXISTS`.
- Downgrade restores the dropped columns and recreates `ingredient_merge_audit` with its sequence and primary key.
- This migration intentionally does not modify FastAPI runtime/schema alignment.

## Runtime/schema drift issue tracking

Per implementation decision, runtime/schema drift is tracked as a dedicated GitHub issue draft (not implemented in this migration scope):

- `docs/issues/fastapi-runtime-schema-drift-issue.md`

Reusable duplicate audit query (case-insensitive exact-name collisions):

```sql
WITH dup AS (
	SELECT lower(name) AS normalized_name, COUNT(*) AS dup_count
	FROM ingredients
	GROUP BY lower(name)
	HAVING COUNT(*) > 1
)
SELECT
	d.normalized_name,
	d.dup_count,
	i.id,
	i.name,
	i.bls_key,
	(SELECT COUNT(*) FROM recipe_ingredients ri WHERE ri.ingredient_id = i.id) AS recipe_refs,
	(SELECT COUNT(*) FROM ingredient_prices ip WHERE ip.ingredient_id = i.id) AS price_rows
FROM dup d
JOIN ingredients i ON lower(i.name) = d.normalized_name
ORDER BY d.normalized_name, recipe_refs DESC, price_rows DESC, i.id;
```

## Bulk duplicate merge (008, lossless mode)

Alembic `008` bulk-merges all exact case-insensitive duplicate names (`lower(name)`).

Lossless guarantees in this migration:
- No `ingredient_prices` rows are dropped.
- No `recipe_ingredients` rows are dropped.
- No `ingredient_units` rows are dropped.
- Nutrition links are preserved by consolidating data into canonical ingredient nutrition rows.

Important detail on nutrition:
- `ingredient_nutrition` has a one-row-per-ingredient unique rule.
- During merge, values from the duplicate nutrition row are merged into the canonical row (filling zero/empty canonical fields), then the duplicate row is removed because two rows cannot point to the same merged ingredient id.

Preflight backup (recommended):

```bash
docker compose exec -T db pg_dump -U recipe_user -d recipe_db > db/backups/pre_008_duplicate_merge.sql
```

Run migration:

```bash
DATABASE_URL=postgresql+psycopg://recipe_user:recipe_pass123@localhost:5432/recipe_db .venv/bin/alembic upgrade 008
```

Post-checks:

```bash
DATABASE_URL=postgresql+psycopg://recipe_user:recipe_pass123@localhost:5432/recipe_db .venv/bin/alembic current
```

```bash
docker compose exec -T db psql -U recipe_user -d recipe_db -c "WITH d AS (SELECT lower(name) AS normalized_name, COUNT(*) AS cnt FROM ingredients GROUP BY lower(name) HAVING COUNT(*) > 1) SELECT COUNT(*) AS duplicate_name_groups, COALESCE(SUM(cnt),0) AS rows_in_duplicate_groups FROM d;"
```

## Market estimate seeding + canonical auto-backfill (009 + 010)

As of Alembic `009` and `010`:
- `009` seeds market-estimate fallback prices (`supplier_id = 'market_estimate_2026_q1'`).
- `010` runs canonical backfill logic during migrations (including `recipe_ingredients.quantity_grams`).

This means a fresh Docker start that runs `alembic upgrade head` no longer requires a manual
`db/scripts/backfill_canonical_fields.sql` run to restore canonical coverage.

Apply latest migrations:

```bash
DATABASE_URL=postgresql+psycopg://recipe_user:recipe_pass123@localhost:5432/recipe_db .venv/bin/alembic upgrade head
```

Quick post-start coverage check:

```bash
docker compose exec -T db psql -X -A -t -P pager=off -U recipe_user -d recipe_db -c "WITH latest_price AS (SELECT * FROM public.ingredient_prices_latest) SELECT COUNT(*) AS total_recipe_lines, COUNT(*) FILTER (WHERE lp.price_per_gram IS NOT NULL AND ri.quantity_grams IS NOT NULL) AS priced_lines, COUNT(*) FILTER (WHERE lp.price_per_gram IS NULL OR ri.quantity_grams IS NULL) AS gap_lines, ROUND((COUNT(*) FILTER (WHERE lp.price_per_gram IS NOT NULL AND ri.quantity_grams IS NOT NULL)::numeric / NULLIF(COUNT(*),0))*100,2) AS coverage_pct FROM recipe_ingredients ri LEFT JOIN latest_price lp ON lp.ingredient_id = ri.ingredient_id;"
```
