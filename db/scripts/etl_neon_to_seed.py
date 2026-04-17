#!/usr/bin/env python3
"""
ETL: Neon recipes_010 → current schema seed SQL
================================================
Reads the legacy Neon DB (at Alembic revision 010, post-deduplication) and
produces idempotent INSERT statements that fit the current schema (revision 013).

Output:  db/seeds/legacy_data.sql   (authoritative, committed)
         db/init/04_legacy_data.sql  (Docker entrypoint copy)

Column-mapping decisions
------------------------
- ingredients : drops 6 legacy cols; adds `source='standard'` (server default)
- recipes     : renames preparation_time→preparation_time_minutes (text→int),
                cooking_time→cooking_time_minutes, shelf_life→shelf_life_text,
                drops 40+ legacy columns; photo_url=NULL (new col, 013)
- recipe_ingredients : renames quid→quid_percent; drops updated_at; sub_recipe_id=NULL
- ingredient_allergens / ingredient_additives : UUIDs differ between Neon and
  current DB (migration 012 generated fresh UUIDs); we join on integer `code`
  and emit subquery-based INSERTs so the correct target-DB UUIDs are resolved
  at load time.
- ingredient_prices.currency : always non-NULL in Neon data (verified); kept as-is
- tenants.settings : always NULL in Neon; emitted as NULL (JSONB col accepts NULL)

Usage
-----
    python3 db/scripts/etl_neon_to_seed.py [NEON_DSN]

If NEON_DSN is not given the default (development) connection string is used.
"""

import datetime
import decimal
import json
import shutil
import sys
import uuid
from pathlib import Path
from typing import Any

import psycopg2
import psycopg2.extras

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

DEFAULT_NEON_DSN = (
    "postgresql://neondb_owner:npg_sfGtpBNm13gy"
    "@ep-quiet-rice-alh540v4-pooler.c-3.eu-central-1.aws.neon.tech"
    "/recipes_010?sslmode=require&channel_binding=require"
)

ROOT = Path(__file__).resolve().parents[2]
SEEDS_DIR = ROOT / "db" / "seeds"
INIT_DIR = ROOT / "db" / "init"
OUTPUT_SEED = SEEDS_DIR / "legacy_data.sql"
OUTPUT_INIT = INIT_DIR / "04_legacy_data.sql"


# ---------------------------------------------------------------------------
# SQL literal formatters
# ---------------------------------------------------------------------------

def _q(v: Any) -> str:
    """Format a Python value as a SQL literal."""
    if v is None:
        return "NULL"
    if isinstance(v, bool):
        return "TRUE" if v else "FALSE"
    if isinstance(v, (int, float, decimal.Decimal)):
        return str(v)
    if isinstance(v, (datetime.datetime, datetime.date)):
        return f"'{v.isoformat()}'"
    if isinstance(v, uuid.UUID):
        return f"'{v}'"
    if isinstance(v, dict):
        return "'" + json.dumps(v).replace("'", "''") + "'::jsonb"
    # str, and anything else
    return "'" + str(v).replace("'", "''") + "'"


def _parse_minutes(text: Any) -> str:
    """Convert a free-text time string to an integer minute count or NULL."""
    if text is None:
        return "NULL"
    s = str(text).strip()
    if not s:
        return "NULL"
    try:
        return str(int(float(s)))
    except (ValueError, TypeError):
        return "NULL"


# ---------------------------------------------------------------------------
# Writer helpers
# ---------------------------------------------------------------------------

def _section(f, title: str) -> None:
    line = "-" * 66
    f.write(f"\n-- {line}\n-- {title}\n-- {line}\n\n")


def _write_rows(f, table: str, cols: list[str], rows: list[tuple],
                conflict: str = "(id)") -> int:
    """
    conflict: the conflict target, e.g. "(id)" → ON CONFLICT (id) DO NOTHING
              pass "" or None for a bare ON CONFLICT DO NOTHING (no target).
    """
    if not rows:
        f.write(f"-- {table}: 0 rows (nothing to insert)\n\n")
        return 0
    col_list = ", ".join(cols)
    on_conflict = f"ON CONFLICT {conflict} DO NOTHING" if conflict else "ON CONFLICT DO NOTHING"
    for row in rows:
        vals = ", ".join(_q(v) for v in row)
        f.write(
            f"INSERT INTO public.{table} ({col_list})\n"
            f"  VALUES ({vals})\n"
            f"  {on_conflict};\n"
        )
    f.write(f"-- {table}: {len(rows)} rows inserted above\n\n")
    return len(rows)


# ---------------------------------------------------------------------------
# Per-table extractors
# ---------------------------------------------------------------------------

def etl_tenants(cur, f) -> int:
    _section(f, "tenants (13 rows expected)")
    cur.execute("""
        SELECT id, created_at, updated_at, name, slug, is_active, settings
        FROM tenants
        ORDER BY created_at
    """)
    rows = []
    for r in cur.fetchall():
        id_, created_at, updated_at, name, slug, is_active, settings = r
        rows.append((id_, created_at, updated_at, name, slug, is_active, settings))
    cols = ["id", "created_at", "updated_at", "name", "slug", "is_active", "settings"]
    return _write_rows(f, "tenants", cols, rows)


def etl_categories(cur, f) -> int:
    _section(f, "categories (7 rows expected) — tenant_id=NULL (not in legacy)")
    cur.execute("SELECT id, name FROM categories ORDER BY name")
    rows = [(r[0], r[1], None) for r in cur.fetchall()]
    cols = ["id", "name", "tenant_id"]
    return _write_rows(f, "categories", cols, rows)


def etl_ingredients(cur, f) -> int:
    _section(f, "ingredients (12301 rows expected)")
    cur.execute("""
        SELECT id, name, created_at, updated_at, tenant_id,
               default_unit, bls_key, is_custom, parent_id
        FROM ingredients
        ORDER BY created_at, id
    """)
    rows = []
    for r in cur.fetchall():
        id_, name, created_at, updated_at, tenant_id, \
            default_unit, bls_key, is_custom, parent_id = r
        rows.append((
            id_, name, created_at, updated_at, tenant_id,
            default_unit, bls_key, is_custom, parent_id,
            "standard",  # source: NOT NULL, server_default='standard'
        ))
    cols = [
        "id", "name", "created_at", "updated_at", "tenant_id",
        "default_unit", "bls_key", "is_custom", "parent_id",
        "source",
    ]
    return _write_rows(f, "ingredients", cols, rows)


def etl_recipes(cur, f) -> int:
    _section(f, "recipes (83 rows expected — 2 with NULL tenant_id skipped)")
    cur.execute("""
        SELECT
            id, created_at, updated_at, tenant_id, name, description,
            yield_amount, yield_unit, instructions, reduction_factor,
            status, is_component, recipe_number,
            preparation_time,
            cooking_time,
            shelf_life,
            storage_temperature,
            notes, created_by,
            yield_mode, portion_size_grams,
            total_raw_weight_grams, total_cooked_weight_grams,
            portions_count_resolved
        FROM recipes
        WHERE tenant_id IS NOT NULL
        ORDER BY created_at, id
    """)
    rows = []
    for r in cur.fetchall():
        (id_, created_at, updated_at, tenant_id, name, description,
         yield_amount, yield_unit, instructions, reduction_factor,
         status, is_component, recipe_number,
         preparation_time,
         cooking_time,
         shelf_life,
         storage_temperature,
         notes, created_by,
         yield_mode, portion_size_grams,
         total_raw_weight_grams, total_cooked_weight_grams,
         portions_count_resolved) = r

        rows.append((
            id_, created_at, updated_at, tenant_id, name, description,
            yield_amount, yield_unit, instructions, reduction_factor,
            status,
            is_component if is_component is not None else False,
            recipe_number,
            None,               # preparation_time_minutes (all empty in Neon)
            None,               # cooking_time_minutes (all empty in Neon)
            shelf_life,         # → shelf_life_text
            storage_temperature,
            notes, created_by,
            yield_mode or "count",
            portion_size_grams,
            total_raw_weight_grams, total_cooked_weight_grams,
            portions_count_resolved,
            None,               # photo_url (new col, 013 — NULL for legacy data)
        ))

    cols = [
        "id", "created_at", "updated_at", "tenant_id", "name", "description",
        "yield_amount", "yield_unit", "instructions", "reduction_factor",
        "status", "is_component", "recipe_number",
        "preparation_time_minutes",
        "cooking_time_minutes",
        "shelf_life_text",
        "storage_temperature",
        "notes", "created_by",
        "yield_mode", "portion_size_grams",
        "total_raw_weight_grams", "total_cooked_weight_grams",
        "portions_count_resolved",
        "photo_url",
    ]
    return _write_rows(f, "recipes", cols, rows)


def etl_recipe_ingredients(cur, f) -> int:
    _section(f, "recipe_ingredients (867 rows expected)")
    cur.execute("""
        SELECT id, recipe_id, ingredient_id, sort_order, created_at,
               quantity, unit, preparation, quid AS quid_percent,
               item_type, quantity_grams
        FROM recipe_ingredients
        ORDER BY recipe_id, sort_order, id
    """)
    rows = []
    for r in cur.fetchall():
        (id_, recipe_id, ingredient_id, sort_order, created_at,
         quantity, unit, preparation, quid_percent,
         item_type, quantity_grams) = r
        rows.append((
            id_, recipe_id,
            ingredient_id,  # non-NULL in Neon; sub_recipe_id stays NULL
            None,           # sub_recipe_id
            sort_order, created_at,
            quantity, unit, preparation, quid_percent,
            False,          # is_organic: server_default false; Neon has no col
            item_type, quantity_grams,
        ))

    cols = [
        "id", "recipe_id", "ingredient_id", "sub_recipe_id",
        "sort_order", "created_at",
        "quantity", "unit", "preparation", "quid_percent",
        "is_organic", "item_type", "quantity_grams",
    ]
    return _write_rows(f, "recipe_ingredients", cols, rows)


def etl_ingredient_nutrition(cur, f) -> int:
    _section(f, "ingredient_nutrition (305 rows expected)")
    cur.execute("""
        SELECT id, ingredient_id,
               COALESCE(created_at, NOW()) AS created_at,
               COALESCE(updated_at, NOW()) AS updated_at,
               energy_kj, energy_kcal, fat, saturates, carbs,
               sugars, protein, fiber, salt, alcohol, water
        FROM ingredient_nutrition
        ORDER BY ingredient_id
    """)
    rows = list(cur.fetchall())
    cols = [
        "id", "ingredient_id", "created_at", "updated_at",
        "energy_kj", "energy_kcal", "fat", "saturates", "carbs",
        "sugars", "protein", "fiber", "salt", "alcohol", "water",
    ]
    return _write_rows(f, "ingredient_nutrition", cols, rows, conflict="(id)")


def etl_ingredient_prices(cur, f) -> int:
    _section(f, "ingredient_prices — price_per_unit > 0 only; deduped by partial unique indexes")
    cur.execute("""
        SELECT id, ingredient_id, price_per_unit,
               COALESCE(currency, 'EUR') AS currency,
               unit, supplier_id, supplier_name, article_number,
               COALESCE(created_at, NOW()) AS created_at,
               COALESCE(updated_at, NOW()) AS updated_at,
               price_per_gram
        FROM ingredient_prices
        WHERE price_per_unit > 0      -- exclude zero/negative (violate positive_price CHECK)
        ORDER BY ingredient_id, id
    """)
    rows = list(cur.fetchall())
    cols = [
        "id", "ingredient_id", "price_per_unit", "currency", "unit",
        "supplier_id", "supplier_name", "article_number",
        "created_at", "updated_at", "price_per_gram",
    ]
    # Bare DO NOTHING (no conflict target) silences both the PK and the two
    # partial unique indexes (uq_ingredient_no_supplier, uq_ingredient_supplier)
    # that prevent duplicate prices per ingredient.
    return _write_rows(f, "ingredient_prices", cols, rows, conflict="")


def etl_ingredient_allergens(cur, f) -> int:
    """
    UUIDs for allergens differ between Neon and the current DB (migration 012
    generated fresh IDs). We emit subquery-based INSERTs keyed on the stable
    integer `code` so the correct target-DB allergen UUID is resolved at load.
    """
    _section(f, "ingredient_allergens (154 rows expected — subquery by allergen code)")
    cur.execute("""
        SELECT ia.ingredient_id, a.code
        FROM ingredient_allergens ia
        JOIN allergens a ON ia.allergen_id = a.id
        ORDER BY ia.ingredient_id, a.code
    """)
    rows = cur.fetchall()
    if not rows:
        f.write("-- ingredient_allergens: 0 rows\n\n")
        return 0
    for ingredient_id, code in rows:
        f.write(
            f"INSERT INTO public.ingredient_allergens (ingredient_id, allergen_id)\n"
            f"  SELECT {_q(ingredient_id)}, id FROM public.allergens WHERE code = {code}\n"
            f"  ON CONFLICT DO NOTHING;\n"
        )
    f.write(f"-- ingredient_allergens: {len(rows)} rows inserted above\n\n")
    return len(rows)


def etl_ingredient_additives(cur, f) -> int:
    """
    Same UUID-remapping approach as allergens — join on integer `code`.
    """
    _section(f, "ingredient_additives (60 rows expected — subquery by additive code)")
    cur.execute("""
        SELECT ia.ingredient_id, a.code
        FROM ingredient_additives ia
        JOIN additives a ON ia.additive_id = a.id
        ORDER BY ia.ingredient_id, a.code
    """)
    rows = cur.fetchall()
    if not rows:
        f.write("-- ingredient_additives: 0 rows\n\n")
        return 0
    for ingredient_id, code in rows:
        f.write(
            f"INSERT INTO public.ingredient_additives (ingredient_id, additive_id)\n"
            f"  SELECT {_q(ingredient_id)}, id FROM public.additives WHERE code = {code}\n"
            f"  ON CONFLICT DO NOTHING;\n"
        )
    f.write(f"-- ingredient_additives: {len(rows)} rows inserted above\n\n")
    return len(rows)


def etl_ingredient_units(cur, f) -> int:
    _section(f, "ingredient_units (7 rows expected)")
    cur.execute("""
        SELECT id, ingredient_id, unit_code, grams_per_unit, label
        FROM ingredient_units
        ORDER BY ingredient_id
    """)
    rows = list(cur.fetchall())
    cols = ["id", "ingredient_id", "unit_code", "grams_per_unit", "label"]
    return _write_rows(f, "ingredient_units", cols, rows, conflict="(id)")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> None:
    dsn = sys.argv[1] if len(sys.argv) > 1 else DEFAULT_NEON_DSN

    print(f"Connecting to Neon … ")
    conn = psycopg2.connect(dsn)
    conn.autocommit = True
    cur = conn.cursor()

    SEEDS_DIR.mkdir(parents=True, exist_ok=True)

    print(f"Writing → {OUTPUT_SEED}")
    counts: dict[str, int] = {}

    with OUTPUT_SEED.open("w", encoding="utf-8") as f:
        f.write("-- =================================================================\n")
        f.write("-- Legacy data seed — generated by db/scripts/etl_neon_to_seed.py\n")
        f.write("-- Source : Neon recipes_010 (Alembic rev 010, post-deduplication)\n")
        f.write("-- Target : current schema (Alembic rev 013)\n")
        f.write("--\n")
        f.write("-- Load order respects FK dependencies.\n")
        f.write("-- All INSERTs are idempotent (ON CONFLICT … DO NOTHING).\n")
        f.write("-- Skipped: units, allergens, additives (seeded by migration 012).\n")
        f.write("-- Skipped: nutrition_facts, recipe_nutrition (legacy tables, not\n")
        f.write("--          in current schema). Nutrition lives in ingredient_nutrition.\n")
        f.write("-- =================================================================\n")

        # Single transaction wraps all inserts — 1 fsync instead of N*14K
        f.write("\nBEGIN;\n")
        f.write("\nSET session_replication_role = 'replica'; -- disable FK checks during bulk load\n")

        counts["tenants"]              = etl_tenants(cur, f)
        counts["categories"]           = etl_categories(cur, f)
        counts["ingredients"]          = etl_ingredients(cur, f)
        counts["recipes"]              = etl_recipes(cur, f)
        counts["recipe_ingredients"]   = etl_recipe_ingredients(cur, f)
        counts["ingredient_nutrition"] = etl_ingredient_nutrition(cur, f)
        counts["ingredient_prices"]    = etl_ingredient_prices(cur, f)
        counts["ingredient_allergens"] = etl_ingredient_allergens(cur, f)
        counts["ingredient_additives"] = etl_ingredient_additives(cur, f)
        counts["ingredient_units"]     = etl_ingredient_units(cur, f)

        f.write("\nSET session_replication_role = 'origin'; -- re-enable FK checks\n")

        f.write("\n-- Summary\n")
        # Note: COMMIT is written after the post-load fixes block below
        total = 0
        for tbl, n in counts.items():
            f.write(f"-- {tbl:<35} {n:>6} rows\n")
            total += n
        f.write(f"-- {'TOTAL':<35} {total:>6} rows\n")

        f.write("\nCOMMIT;\n")

    conn.close()

    # Copy to Docker init location
    shutil.copy2(OUTPUT_SEED, OUTPUT_INIT)
    print(f"Copied  → {OUTPUT_INIT}")

    print("\nSummary:")
    for tbl, n in counts.items():
        print(f"  {tbl:<35} {n:>6}")
    print(f"  {'TOTAL':<35} {sum(counts.values()):>6}")
    print("\nDone. Restart Docker with a fresh volume to load the seed:")
    print("  make fclean && make dev")


if __name__ == "__main__":
    main()
