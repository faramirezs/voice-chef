# Migration 012 — Gap Analysis & Must-Fix Report

> Generated 2026-04-10 from cross-referencing all SQLModel models, Alembic
> migrations 001–011, the regenerated `01_dump.sql`, reference data JSONs,
> Docker init scripts, CI workflow, and test suite.

---

## Method

Three exhaustive inventories were compared column-by-column, constraint-by-constraint:

| Source | Tables | Columns | Indexes | Constraints |
|--------|--------|---------|---------|-------------|
| SQLModel models (`*_models.py`) | 30 (26 classes + 4 `Table()`) | ~220 | 26 | ~35 |
| Alembic migrations 001–011 | 27 created (1 dropped by 011) | ~220 | 26 | ~35 |
| `db/init/01_dump.sql` (regenerated) | 27 + `alembic_version` | ~220 | 26 | ~35 |

---

## Good news: Schema is aligned

After migration 002 (`002_unit_system.py`) creates `units` and
`ingredient_units`, **every model-defined table, column, index, and constraint
has a corresponding migration**. The dump was regenerated from migration head
(`make dump-regen`, schema-only) and matches exactly.

There is **no missing table migration** — the initial concern that `units` and
`ingredient_units` lacked migrations was incorrect; migration 002 creates them
and migration 004 re-ensures them with `IF NOT EXISTS`.

---

## CRITICAL gaps

### 1. Docker init skips ALL data migrations

**Impact: any code relying on `units` rows, market-estimate prices, or canonical backfill fields will fail on a fresh Docker start.**

The startup sequence is:

1. `db/init/01_dump.sql` → loads schema (empty tables, zero rows)
2. `db/init/02_align_alembic_revision.sql` → stamps `alembic_version = '011'`
3. FastAPI Dockerfile: `alembic upgrade head` → sees DB at 011, head is 011, **does nothing**
4. DB has correct schema, but **zero data**

Data that is lost by skipping migrations:

| Migration | Data it inserts | Impact |
|-----------|----------------|--------|
| 004 | 6 base units (`g`, `kg`, `mg`, `l`, `ml`, `pc`) into `units` | Unit lookups fail |
| 006 | 7 ingredient-unit conversions + `price_per_gram` backfill | Price-per-gram is NULL everywhere |
| 009 | Market-estimate fallback prices for ingredients without supplier prices | Costing gaps |
| 010 | Canonical backfill: `recipe_ingredients.quantity_grams` + recipe weight totals | Recipe calculations broken |

### 2. Reference data has no load path

Three curated JSON files exist with no migration or script that loads them:

| File | Records | Status |
|------|---------|--------|
| `db/scripts/reference_data/units.json` | 19 units (migration 004 only seeds 6) | 13 units missing: `cl`, `dl`, `el`, `tl`, `prise`, `stk`, `pck`, `bund`, `dose`, `blatt`, `zehe`, `scheibe`, `tasse` |
| `db/scripts/reference_data/allergens.json` | 33 allergens (EU-14 + sub-allergens) | `allergens` table is always empty |
| `db/scripts/reference_data/additives.json` | ~35 additives (German food labelling) | `additives` table is always empty |

### 3. Original seed data is gone

| Source | Status |
|--------|--------|
| `db/init/01_dump.sql` | Schema-only (0 INSERT/COPY statements) |
| `db/backups/neon_recipes_010_pre_local_push_2026-03-17.sql` | Empty file (just pg_dump headers, 27 lines, no data) |
| `db/scripts/seed_from_neon.py` | Deleted — only stale `.pyc` remains |
| Neon cloud DB | Unknown — may still contain the original recipe/ingredient data |

If the Neon database still exists, the original recipe/ingredient/price data can
be recovered. Otherwise, the only seed data source is the market-estimate prices
from migration 009.

---

## HIGH-priority gaps

### 4. `02_align_alembic_revision.sql` hardcodes revision `011`

```sql
UPDATE public.alembic_version SET version_num = '011' WHERE version_num <> '011';
```

Every new migration requires manually updating this file. If forgotten, Docker
init stamps the wrong revision and Alembic will either skip the new migration
or crash trying to upgrade from a non-existent base.

**Fix:** Either auto-detect head from the migration directory, or replace with a
convention that the dump-regen script also updates this file.

### 5. Drift test covers only 3 of 30 tables

`db/test/test_schema_drift.py` line 55:

```python
MANAGED_TABLES = {"users", "tenants", "recipes"}
```

27 tables are never drift-checked by the pytest suite. The `env.py`
`include_object` filter correctly scopes to all `MODEL_TABLE_NAMES`, but the
surgical `TestInspect` class only parametrizes over 3 tables.

---

## MEDIUM-priority gaps

### 6. Migrations 007/008 reference non-existent columns

Both merge migrations reference `ingredients` columns that exist in neither the
model nor any migration:

- `ingredient_type`
- `has_parent`
- `initial_recipe_id`
- `usage_count`
- `recipe_count`
- `nutrition_id`

These were legacy columns from the original Neon dump. The SQL is wrapped in
conditional blocks (`DO $$...$$`) so it doesn't crash, but it's dead code on
any current DB path. Not harmful, but confusing for future maintainers.

### 7. View `ingredient_prices_latest` is invisible to drift checks

Created by migration 005, this view is not represented in SQLModel metadata.
Autogenerate and drift checks cannot detect if it's missing or stale. If the
view definition needs to change, it must be handled manually.

### 8. No allergen/additive reference data loading

The `allergens` and `additives` tables exist but are always empty. For a
food-industry application, these are required for ingredient labelling
compliance. Either a migration or an init script must seed them.

---

## What migration 012 should contain

Based on the analysis above, here is the must-fix scope:

### Schema changes: NONE needed

Models, migrations, and dump are aligned. No new tables, columns, or indexes
are required.

### Data/process fixes needed:

| # | Fix | Type |
|---|-----|------|
| A | Seed full 19-unit set from `units.json` (idempotent `ON CONFLICT`) | Data migration |
| B | Seed 33 allergens from `allergens.json` (idempotent) | Data migration |
| C | Seed ~35 additives from `additives.json` (idempotent) | Data migration |
| D | Create `db/init/03_seed_reference_data.sql` for Docker init path | Init script |
| E | Make `02_align_alembic_revision.sql` auto-detect head or update to `012` | Init script fix |
| F | Expand `MANAGED_TABLES` in `test_schema_drift.py` to all model tables | Test fix |
| G | Update CI workflow if needed | CI fix |

### Separate from migration 012:

| # | Fix | Type |
|---|-----|------|
| H | Recover Neon data if DB still exists, export as seed SQL | Data recovery |
| I | Clean up dead column references in 007/008 | Optional refactor (low priority) |
| J | Add view drift check for `ingredient_prices_latest` | Test enhancement |

---

## Recommended execution order

1. **Check if Neon DB still has data** — if yes, export recipes/ingredients/prices
   as `db/seeds/legacy_data.sql` before anything else.
2. **Write migration 012** — seed units, allergens, additives from JSON
   (idempotent INSERTs).
3. **Create `db/init/03_seed_reference_data.sql`** — same INSERTs, for the
   Docker init path that skips migrations.
4. **Update `02_align_alembic_revision.sql`** — point to `012`.
5. **Regenerate `01_dump.sql`** — `make dump-regen` to capture any schema
   changes (even if none in 012, keeps the pipeline honest).
6. **Fix `MANAGED_TABLES`** — expand to all model tables.
7. **Run full drift gate** — `make drift-gate-local` should now pass.
8. **Run CI** — both jobs should pass.
