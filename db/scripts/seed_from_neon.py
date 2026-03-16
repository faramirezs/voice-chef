"""
Seed script: migrate data from Neon PostgreSQL to Docker PostgreSQL.

Reads from the Neon source database (read-only) and inserts transformed
data into the new Docker PostgreSQL schema created by Alembic migrations
001 (initial schema) and 002 (unit system).

Usage:
    python scripts/seed_from_neon.py \
        --source "postgresql://...@neon/neondb?sslmode=require" \
        --target "postgresql://user:pass@localhost:5432/voicechef"

Environment variables (alternative to CLI flags):
    NEON_DATABASE_URL   - source connection string
    DATABASE_URL        - target connection string
"""

import argparse
import json
import os
import sys
from pathlib import Path
from uuid import uuid4

import psycopg2
import psycopg2.extras

REAL_TENANT_ID = "0b796544-6414-4d62-8f1f-cd2f9f0ac0a0"
SCRIPT_DIR = Path(__file__).parent
REF_DATA_DIR = SCRIPT_DIR / "reference_data"


def get_connections(source_url: str, target_url: str):
    src = psycopg2.connect(source_url)
    src.set_session(readonly=True)
    tgt = psycopg2.connect(target_url)
    return src, tgt


def step_seed_allergens(tgt_cur):
    """Insert all 31 allergens from reference data with English names and parent codes."""
    data = json.loads((REF_DATA_DIR / "allergens.json").read_text())
    print(f"  Seeding {len(data)} allergens from reference data...")
    for row in data:
        tgt_cur.execute(
            """INSERT INTO allergens (id, code, name_de, name_en, parent_code)
               VALUES (gen_random_uuid(), %(code)s, %(name_de)s, %(name_en)s, %(parent_code)s)
               ON CONFLICT (code) DO NOTHING""",
            row,
        )
    return len(data)


def step_seed_additives(tgt_cur):
    """Insert all 32 additives from reference data with English names."""
    data = json.loads((REF_DATA_DIR / "additives.json").read_text())
    print(f"  Seeding {len(data)} additives from reference data...")
    for row in data:
        tgt_cur.execute(
            """INSERT INTO additives (id, code, name_de, name_en)
               VALUES (gen_random_uuid(), %(code)s, %(name_de)s, %(name_en)s)
               ON CONFLICT (code) DO NOTHING""",
            row,
        )
    return len(data)


def step_seed_units(tgt_cur):
    """Insert all unit definitions from reference data."""
    data = json.loads((REF_DATA_DIR / "units.json").read_text())
    print(f"  Seeding {len(data)} units from reference data...")
    for row in data:
        tgt_cur.execute(
            """INSERT INTO units (id, code, name_de, name_en, grams_per_unit, unit_type, is_base)
               VALUES (gen_random_uuid(), %(code)s, %(name_de)s, %(name_en)s,
                       %(grams_per_unit)s, %(unit_type)s, %(is_base)s)
               ON CONFLICT (code) DO NOTHING""",
            row,
        )
    return len(data)


# Map of free-text unit strings (as they appear in the source data) to
# canonical unit codes and their gram conversion factors.  Used to backfill
# quantity_grams and price_per_gram after migration.
UNIT_ALIAS_MAP = {
    "g": ("g", 1),
    "gr": ("g", 1),
    "gram": ("g", 1),
    "gramm": ("g", 1),
    "kg": ("kg", 1000),
    "kilo": ("kg", 1000),
    "kilogram": ("kg", 1000),
    "kilogramm": ("kg", 1000),
    "mg": ("mg", 0.001),
    "ml": ("ml", 1),
    "milliliter": ("ml", 1),
    "cl": ("cl", 10),
    "dl": ("dl", 100),
    "l": ("l", 1000),
    "liter": ("l", 1000),
    "el": ("el", 15),
    "el (15g)": ("el", 15),
    "el (10g)": ("el", 10),
    "el (10.0g)": ("el", 10),
    "tl": ("tl", 5),
    "tl (5g)": ("tl", 5),
    "tl (4g)": ("tl", 4),
    "prise": ("prise", 0.5),
    "stk": ("stk", None),
    "stück": ("stk", None),
    "stck": ("stk", None),
    "pck": ("pck", None),
    "packung": ("pck", None),
    "bund": ("bund", None),
    "dose": ("dose", None),
    "blatt": ("blatt", None),
    "zehe": ("zehe", None),
    "scheibe": ("scheibe", None),
    "tasse": ("tasse", 240),
    "eur": None,  # currency, not a unit
}


YIELD_ALIAS_MAP = {
    "portion": ("portions", "count"),
    "portionen": ("portions", "count"),
    "portions": ("portions", "count"),
    "serving": ("portions", "count"),
    "servings": ("portions", "count"),
    "stk": ("stk", "count"),
    "stuck": ("stk", "count"),
    "stueck": ("stk", "count"),
    "piece": ("stk", "count"),
    "pieces": ("stk", "count"),
    "g": ("g", "weight"),
    "gram": ("g", "weight"),
    "gramm": ("g", "weight"),
    "kg": ("kg", "weight"),
    "kilogram": ("kg", "weight"),
    "kilogramm": ("kg", "weight"),
    "ml": ("ml", "weight"),
    "milliliter": ("ml", "weight"),
    "l": ("l", "weight"),
    "liter": ("l", "weight"),
}


def _to_float(val):
    if val is None:
        return None
    return float(val)


def _normalize_yield_unit(unit_str: str | None) -> tuple[str | None, str]:
    """Normalize yield unit and infer canonical yield mode.

    Defaults to count-mode when unit is unknown, preserving the original unit.
    """
    if unit_str is None:
        return None, "count"

    cleaned = unit_str.strip()
    if not cleaned:
        return None, "count"

    mapped = YIELD_ALIAS_MAP.get(cleaned.lower())
    if mapped is not None:
        return mapped

    return cleaned, "count"


def _resolve_grams(unit_str: str | None, quantity: float | None) -> float | None:
    """Convert quantity + unit string to grams. Returns None if unresolvable."""
    if quantity is None:
        return None
    if unit_str is None:
        return None

    key = unit_str.strip().lower()
    entry = UNIT_ALIAS_MAP.get(key)

    if entry is None:
        return None
    if isinstance(entry, tuple):
        _code, grams_per = entry
        if grams_per is None:
            return None
        return float(quantity) * grams_per
    return None


def _resolve_price_per_gram(price: float | None, unit_str: str | None) -> float | None:
    """Convert price-per-unit to price-per-gram. Returns None if unresolvable."""
    if price is None or unit_str is None:
        return None

    key = unit_str.strip().lower()
    entry = UNIT_ALIAS_MAP.get(key)

    if entry is None or not isinstance(entry, tuple):
        return None
    _code, grams_per = entry
    if grams_per is None or grams_per == 0:
        return None
    return float(price) / grams_per


def step_migrate_tenants(src_cur, tgt_cur):
    """Migrate only the real tenant, skip test scaffolds."""
    src_cur.execute(
        "SELECT id, name, slug, is_active, settings, created_at, updated_at "
        "FROM tenants WHERE id = %s",
        (REAL_TENANT_ID,),
    )
    row = src_cur.fetchone()
    if not row:
        print(f"  WARNING: Real tenant {REAL_TENANT_ID} not found in source!")
        return 0

    tgt_cur.execute(
        """INSERT INTO tenants (id, name, slug, is_active, settings, created_at, updated_at)
           VALUES (%s, %s, %s, %s, %s, %s, %s)
           ON CONFLICT (id) DO NOTHING""",
        (row[0], row[1], row[2], row[3], row[4] or "{}", row[5], row[6]),
    )
    print(f"  Migrated tenant: {row[1]} ({row[2]})")
    return 1


def step_migrate_ingredients(src_cur, tgt_cur):
    """Migrate all 12,427 ingredients with source derivation."""
    src_cur.execute(
        "SELECT id, tenant_id, name, default_unit, bls_key, is_custom, "
        "has_parent, parent_id, created_at, updated_at "
        "FROM ingredients ORDER BY created_at"
    )
    rows = src_cur.fetchall()
    print(f"  Migrating {len(rows)} ingredients...")

    batch = []
    for r in rows:
        (
            id_, tenant_id, name, default_unit, bls_key,
            is_custom, has_parent, parent_id, created_at, updated_at,
        ) = r

        if bls_key:
            source = "bls"
        elif is_custom:
            source = "custom"
        else:
            source = "standard"

        batch.append((
            id_, tenant_id, name, None, source, bls_key,
            default_unit, bool(is_custom) if is_custom else False,
            parent_id, created_at, updated_at,
        ))

    psycopg2.extras.execute_batch(
        tgt_cur,
        """INSERT INTO ingredients
           (id, tenant_id, name, name_english, source, bls_key,
            default_unit, is_custom, parent_id, created_at, updated_at)
           VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
           ON CONFLICT (id) DO NOTHING""",
        batch,
        page_size=1000,
    )
    return len(rows)


def step_migrate_ingredient_nutrition(src_cur, tgt_cur):
    """Migrate ingredient nutrition data (322 rows)."""
    src_cur.execute(
        "SELECT id, ingredient_id, energy_kj, energy_kcal, carbs, protein, "
        "fat, sugars, fiber, saturates, salt, alcohol, water, created_at, updated_at "
        "FROM ingredient_nutrition"
    )
    rows = src_cur.fetchall()
    print(f"  Migrating {len(rows)} ingredient nutrition records...")

    psycopg2.extras.execute_batch(
        tgt_cur,
        """INSERT INTO ingredient_nutrition
           (id, ingredient_id, energy_kj, energy_kcal, carbs, protein,
            fat, sugars, fiber, saturates, salt, alcohol, water, created_at, updated_at)
           VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
           ON CONFLICT (ingredient_id) DO NOTHING""",
        rows,
        page_size=500,
    )
    return len(rows)


def step_migrate_ingredient_prices(src_cur, tgt_cur):
    """Migrate ingredient prices (201 rows), normalizing empty strings to NULL.
    Also computes price_per_gram from price_per_unit and the unit's gram factor."""
    src_cur.execute(
        "SELECT id, ingredient_id, price_per_unit, currency, unit, "
        "supplier_name, supplier_id, article_number, created_at, updated_at "
        "FROM ingredient_prices"
    )
    rows = src_cur.fetchall()
    print(f"  Migrating {len(rows)} ingredient prices...")

    batch = []
    resolved = 0
    for r in rows:
        (
            id_, ingredient_id, price, currency, unit,
            supplier_name, supplier_id, article_number, created_at, updated_at,
        ) = r
        supplier_name = supplier_name.strip() if supplier_name else None
        supplier_name = supplier_name or None
        supplier_id = supplier_id.strip() if supplier_id else None
        supplier_id = supplier_id or None

        ppg = _resolve_price_per_gram(float(price) if price else None, unit)
        if ppg is not None:
            resolved += 1

        batch.append((
            id_, ingredient_id, price, currency or "EUR", unit,
            supplier_name, supplier_id, article_number,
            ppg, created_at, updated_at,
        ))

    psycopg2.extras.execute_batch(
        tgt_cur,
        """INSERT INTO ingredient_prices
           (id, ingredient_id, price_per_unit, currency, unit,
            supplier_name, supplier_id, article_number,
            price_per_gram, created_at, updated_at)
           VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
           ON CONFLICT DO NOTHING""",
        batch,
        page_size=500,
    )
    print(f"    price_per_gram resolved: {resolved}/{len(rows)}")
    return len(rows)


def step_migrate_ingredient_allergens(src_cur, tgt_cur):
    """Migrate ingredient-allergen junction rows, remapping allergen IDs."""
    # Build code->new_id lookup from target
    tgt_cur.execute("SELECT id, code FROM allergens")
    allergen_map = {str(row[1]): row[0] for row in tgt_cur.fetchall()}

    # Source uses old allergen UUIDs; we need to map via allergen code
    src_cur.execute(
        "SELECT ia.ingredient_id, a.code "
        "FROM ingredient_allergens ia "
        "JOIN allergens a ON a.id = ia.allergen_id"
    )
    rows = src_cur.fetchall()
    print(f"  Migrating {len(rows)} ingredient-allergen links...")

    batch = []
    skipped = 0
    for ingredient_id, allergen_code in rows:
        new_allergen_id = allergen_map.get(str(allergen_code))
        if new_allergen_id:
            batch.append((ingredient_id, new_allergen_id))
        else:
            skipped += 1

    if skipped:
        print(f"    Skipped {skipped} rows with unknown allergen codes")

    psycopg2.extras.execute_batch(
        tgt_cur,
        """INSERT INTO ingredient_allergens (ingredient_id, allergen_id)
           VALUES (%s, %s) ON CONFLICT DO NOTHING""",
        batch,
        page_size=500,
    )
    return len(batch)


def step_migrate_ingredient_additives(src_cur, tgt_cur):
    """Migrate ingredient-additive junction rows, remapping additive IDs."""
    tgt_cur.execute("SELECT id, code FROM additives")
    additive_map = {str(row[1]): row[0] for row in tgt_cur.fetchall()}

    src_cur.execute(
        "SELECT iad.ingredient_id, a.code "
        "FROM ingredient_additives iad "
        "JOIN additives a ON a.id = iad.additive_id"
    )
    rows = src_cur.fetchall()
    print(f"  Migrating {len(rows)} ingredient-additive links...")

    batch = []
    skipped = 0
    for ingredient_id, additive_code in rows:
        new_additive_id = additive_map.get(str(additive_code))
        if new_additive_id:
            batch.append((ingredient_id, new_additive_id))
        else:
            skipped += 1

    if skipped:
        print(f"    Skipped {skipped} rows with unknown additive codes")

    psycopg2.extras.execute_batch(
        tgt_cur,
        """INSERT INTO ingredient_additives (ingredient_id, additive_id)
           VALUES (%s, %s) ON CONFLICT DO NOTHING""",
        batch,
        page_size=500,
    )
    return len(batch)


def step_migrate_categories(src_cur, tgt_cur):
    """Migrate categories (7 rows)."""
    src_cur.execute("SELECT id, name FROM categories")
    rows = src_cur.fetchall()
    print(f"  Migrating {len(rows)} categories...")

    for id_, name in rows:
        tgt_cur.execute(
            """INSERT INTO categories (id, tenant_id, name)
               VALUES (%s, %s, %s) ON CONFLICT (id) DO NOTHING""",
            (id_, REAL_TENANT_ID, name),
        )
    return len(rows)


def _parse_time_to_minutes(val: str | None) -> int | None:
    """Convert text time values to integer minutes. Returns None for empty/unparseable."""
    if not val or not val.strip():
        return None
    cleaned = val.strip()
    try:
        return int(cleaned)
    except ValueError:
        pass
    try:
        return int(float(cleaned))
    except ValueError:
        return None


def step_migrate_recipes(src_cur, tgt_cur):
    """Migrate recipes (83 rows), converting 63 columns down to ~18."""
    src_cur.execute(
        "SELECT id, tenant_id, name, description, instructions, "
        "yield_amount, yield_unit, reduction_factor, status, "
        "portion_weight, "
        "is_component, recipe_number, preparation_time, cooking_time, "
        "shelf_life, storage_temperature, notes, created_by, "
        "created_at, updated_at "
        "FROM recipes WHERE tenant_id = %s",
        (REAL_TENANT_ID,),
    )
    rows = src_cur.fetchall()
    print(f"  Migrating {len(rows)} recipes...")

    batch = []
    for r in rows:
        (
            id_, tenant_id, name, description, instructions,
            yield_amount, yield_unit, reduction_factor, status, portion_weight,
            is_component, recipe_number, prep_time, cook_time,
            shelf_life, storage_temp, notes, created_by,
            created_at, updated_at,
        ) = r

        norm_yield_unit, yield_mode = _normalize_yield_unit(yield_unit)
        portion_size_grams = _to_float(portion_weight)

        batch.append((
            id_, tenant_id, name, description, instructions,
            yield_amount, norm_yield_unit, reduction_factor,
            yield_mode, portion_size_grams,
            status or "draft",
            bool(is_component) if is_component else False,
            recipe_number,
            _parse_time_to_minutes(prep_time),
            _parse_time_to_minutes(cook_time),
            shelf_life if shelf_life and shelf_life.strip() else None,
            storage_temp,
            notes,
            created_by,
            created_at, updated_at,
        ))

    psycopg2.extras.execute_batch(
        tgt_cur,
        """INSERT INTO recipes
           (id, tenant_id, name, description, instructions,
            yield_amount, yield_unit, reduction_factor,
            yield_mode, portion_size_grams, status,
            is_component, recipe_number, preparation_time_minutes,
            cooking_time_minutes, shelf_life_text, storage_temperature,
            notes, created_by, created_at, updated_at)
           VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
           ON CONFLICT (id) DO NOTHING""",
        batch,
        page_size=100,
    )
    return len(rows)


def step_backfill_recipe_yield_metrics(tgt_cur):
    """Compute recipe-level raw/cooked weights and resolved portions.

    Uses recipe_ingredients.quantity_grams as source-of-truth for raw weight.
    """
    tgt_cur.execute(
        """
        WITH ingredient_totals AS (
            SELECT recipe_id, SUM(quantity_grams) AS total_raw_weight_grams
            FROM recipe_ingredients
            WHERE quantity_grams IS NOT NULL
            GROUP BY recipe_id
        )
        UPDATE recipes r
        SET total_raw_weight_grams = it.total_raw_weight_grams,
            total_cooked_weight_grams = it.total_raw_weight_grams * COALESCE(r.reduction_factor, 1.0),
            portions_count_resolved = CASE
                WHEN r.yield_mode = 'count' AND r.yield_amount IS NOT NULL AND r.yield_amount > 0
                    THEN r.yield_amount
                WHEN r.yield_mode = 'weight'
                     AND r.portion_size_grams IS NOT NULL
                     AND r.portion_size_grams > 0
                    THEN
                        (
                            CASE
                                WHEN r.yield_amount IS NOT NULL AND r.yield_amount > 0 THEN
                                    CASE
                                        WHEN r.yield_unit = 'kg' THEN r.yield_amount * 1000
                                        WHEN r.yield_unit = 'g' THEN r.yield_amount
                                        WHEN r.yield_unit = 'l' THEN r.yield_amount * 1000
                                        WHEN r.yield_unit = 'ml' THEN r.yield_amount
                                        ELSE it.total_raw_weight_grams * COALESCE(r.reduction_factor, 1.0)
                                    END
                                ELSE it.total_raw_weight_grams * COALESCE(r.reduction_factor, 1.0)
                            END
                        ) / r.portion_size_grams
                ELSE NULL
            END
        FROM ingredient_totals it
        WHERE r.id = it.recipe_id
        """
    )
    updated = tgt_cur.rowcount

    tgt_cur.execute(
        """
        UPDATE recipes
        SET portions_count_resolved = NULL
        WHERE portions_count_resolved IS NOT NULL AND portions_count_resolved <= 0
        """
    )
    cleaned = tgt_cur.rowcount
    if cleaned:
        print(f"    cleaned invalid portions_count_resolved rows: {cleaned}")

    return updated


def step_migrate_recipe_ingredients(src_cur, tgt_cur):
    """Migrate recipe_ingredients (861 rows).
    Also computes quantity_grams from quantity and unit."""
    src_cur.execute(
        "SELECT ri.id, ri.recipe_id, ri.ingredient_id, ri.quantity, "
        "ri.unit, ri.preparation, ri.sort_order, ri.quid, ri.item_type, "
        "ri.created_at "
        "FROM recipe_ingredients ri "
        "JOIN recipes r ON r.id = ri.recipe_id "
        "WHERE r.tenant_id = %s",
        (REAL_TENANT_ID,),
    )
    rows = src_cur.fetchall()
    print(f"  Migrating {len(rows)} recipe ingredients...")

    batch = []
    resolved = 0
    unresolved_units = set()
    for r in rows:
        (
            id_, recipe_id, ingredient_id, quantity,
            unit, preparation, sort_order, quid, item_type, created_at,
        ) = r

        qty_g = _resolve_grams(unit, float(quantity) if quantity else None)
        if qty_g is not None:
            resolved += 1
        elif unit:
            unresolved_units.add(unit)

        batch.append((
            id_, recipe_id, ingredient_id, quantity,
            unit, preparation, sort_order or 0, quid,
            False, item_type, qty_g, created_at,
        ))

    psycopg2.extras.execute_batch(
        tgt_cur,
        """INSERT INTO recipe_ingredients
           (id, recipe_id, ingredient_id, quantity, unit, preparation,
            sort_order, quid_percent, is_organic, item_type,
            quantity_grams, created_at)
           VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
           ON CONFLICT (id) DO NOTHING""",
        batch,
        page_size=500,
    )
    print(f"    quantity_grams resolved: {resolved}/{len(rows)}")
    if unresolved_units:
        print(f"    unresolved units: {sorted(unresolved_units)}")
    return len(rows)


def step_migrate_recipe_nutrition_cache(src_cur, tgt_cur):
    """Migrate recipe-level nutrition from recipe_nutrition + nutrition_facts."""
    src_cur.execute(
        "SELECT rn.recipe_id, nf.energy_kj, nf.energy_kcal, nf.fat, "
        "nf.saturates, nf.carbs, nf.sugars, nf.protein, nf.salt "
        "FROM recipe_nutrition rn "
        "JOIN nutrition_facts nf ON nf.id = rn.nutrition_id "
        "JOIN recipes r ON r.id = rn.recipe_id "
        "WHERE r.tenant_id = %s",
        (REAL_TENANT_ID,),
    )
    rows = src_cur.fetchall()
    print(f"  Migrating {len(rows)} recipe nutrition cache records...")

    psycopg2.extras.execute_batch(
        tgt_cur,
        """INSERT INTO recipe_nutrition_cache
           (recipe_id, energy_kj, energy_kcal, fat, saturates,
            carbs, sugars, protein, salt)
           VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
           ON CONFLICT (recipe_id) DO NOTHING""",
        rows,
        page_size=100,
    )
    return len(rows)


def step_create_default_agent(tgt_cur):
    """Create a default chat agent for the migrated tenant."""
    agent_id = str(uuid4())
    tgt_cur.execute(
        """INSERT INTO agents (id, tenant_id, agent_type, name, capabilities)
           VALUES (%s, %s, 'chat_assistant', 'Voice Chef',
                   '["recipe_read","recipe_scale","recipe_crud","shopping_write","task_write","nutrition_read","cost_calc"]'::jsonb)
           ON CONFLICT DO NOTHING""",
        (agent_id, REAL_TENANT_ID),
    )
    print(f"  Created default agent: Voice Chef ({agent_id})")
    return 1


def validate(src, tgt):
    """Compare row counts between source and target to verify migration."""
    src_cur = src.cursor()
    tgt_cur = tgt.cursor()

    checks = [
        ("ingredients", "SELECT count(*) FROM ingredients", "SELECT count(*) FROM ingredients"),
        ("recipes", f"SELECT count(*) FROM recipes WHERE tenant_id = '{REAL_TENANT_ID}'", "SELECT count(*) FROM recipes"),
        (
            "recipe_ingredients",
            f"SELECT count(*) FROM recipe_ingredients ri JOIN recipes r ON r.id = ri.recipe_id WHERE r.tenant_id = '{REAL_TENANT_ID}'",
            "SELECT count(*) FROM recipe_ingredients",
        ),
        ("ingredient_nutrition", "SELECT count(*) FROM ingredient_nutrition", "SELECT count(*) FROM ingredient_nutrition"),
        ("ingredient_prices", "SELECT count(*) FROM ingredient_prices", "SELECT count(*) FROM ingredient_prices"),
        ("allergens", None, "SELECT count(*) FROM allergens"),
        ("additives", None, "SELECT count(*) FROM additives"),
        ("categories", "SELECT count(*) FROM categories", "SELECT count(*) FROM categories"),
        ("recipe_nutrition_cache", None, "SELECT count(*) FROM recipe_nutrition_cache"),
        ("agents", None, "SELECT count(*) FROM agents"),
    ]

    print("\n=== VALIDATION ===")
    all_ok = True
    for name, src_q, tgt_q in checks:
        src_count = None
        if src_q:
            src_cur.execute(src_q)
            src_count = src_cur.fetchone()[0]

        tgt_cur.execute(tgt_q)
        tgt_count = tgt_cur.fetchone()[0]

        if src_count is not None:
            status = "OK" if tgt_count >= src_count else "MISMATCH"
            if status == "MISMATCH":
                all_ok = False
            print(f"  {name}: source={src_count}, target={tgt_count} [{status}]")
        else:
            status = "OK" if tgt_count > 0 else "EMPTY"
            print(f"  {name}: target={tgt_count} [{status}]")

    # Verify allergens have English names
    tgt_cur.execute("SELECT count(*) FROM allergens WHERE name_en IS NOT NULL")
    en_count = tgt_cur.fetchone()[0]
    print(f"  allergens with English names: {en_count}/31 [{'OK' if en_count == 31 else 'MISSING'}]")

    # Verify additives count matches reference (32)
    tgt_cur.execute("SELECT count(*) FROM additives")
    add_count = tgt_cur.fetchone()[0]
    print(f"  additives (expected 32): {add_count} [{'OK' if add_count == 32 else 'MISSING'}]")

    # Verify ingredient source derivation
    tgt_cur.execute("SELECT source, count(*) FROM ingredients GROUP BY source ORDER BY source")
    print("  ingredient sources:")
    for source, count in tgt_cur.fetchall():
        print(f"    {source}: {count}")

    # Verify units seeded
    tgt_cur.execute("SELECT count(*) FROM units")
    units_count = tgt_cur.fetchone()[0]
    print(f"  units seeded: {units_count} [{'OK' if units_count >= 18 else 'MISSING'}]")

    # Verify quantity_grams backfill coverage
    tgt_cur.execute("SELECT count(*) FROM recipe_ingredients WHERE quantity_grams IS NOT NULL")
    qg_count = tgt_cur.fetchone()[0]
    tgt_cur.execute("SELECT count(*) FROM recipe_ingredients")
    ri_total = tgt_cur.fetchone()[0]
    pct = (qg_count / ri_total * 100) if ri_total > 0 else 0
    print(f"  recipe_ingredients with quantity_grams: {qg_count}/{ri_total} ({pct:.0f}%)")

    # Verify price_per_gram backfill coverage
    tgt_cur.execute("SELECT count(*) FROM ingredient_prices WHERE price_per_gram IS NOT NULL")
    ppg_count = tgt_cur.fetchone()[0]
    tgt_cur.execute("SELECT count(*) FROM ingredient_prices")
    ip_total = tgt_cur.fetchone()[0]
    pct = (ppg_count / ip_total * 100) if ip_total > 0 else 0
    print(f"  ingredient_prices with price_per_gram: {ppg_count}/{ip_total} ({pct:.0f}%)")

    # Show unresolved units in recipe_ingredients
    tgt_cur.execute(
        "SELECT DISTINCT unit FROM recipe_ingredients "
        "WHERE quantity_grams IS NULL AND unit IS NOT NULL ORDER BY unit"
    )
    unresolved = [row[0] for row in tgt_cur.fetchall()]
    if unresolved:
        print(f"  unresolved recipe_ingredient units: {unresolved}")

    # Show unresolved units in ingredient_prices
    tgt_cur.execute(
        "SELECT DISTINCT unit FROM ingredient_prices "
        "WHERE price_per_gram IS NULL AND unit IS NOT NULL ORDER BY unit"
    )
    unresolved_p = [row[0] for row in tgt_cur.fetchall()]
    if unresolved_p:
        print(f"  unresolved price units: {unresolved_p}")

    # Verify recipe yield metrics coverage
    tgt_cur.execute(
        "SELECT count(*) FROM recipes WHERE total_raw_weight_grams IS NOT NULL"
    )
    raw_count = tgt_cur.fetchone()[0]
    tgt_cur.execute("SELECT count(*) FROM recipes")
    recipes_total = tgt_cur.fetchone()[0]
    pct = (raw_count / recipes_total * 100) if recipes_total > 0 else 0
    print(
        f"  recipes with total_raw_weight_grams: {raw_count}/{recipes_total} ({pct:.0f}%)"
    )

    tgt_cur.execute(
        "SELECT count(*) FROM recipes WHERE portions_count_resolved IS NOT NULL"
    )
    portions_count = tgt_cur.fetchone()[0]
    pct = (portions_count / recipes_total * 100) if recipes_total > 0 else 0
    print(
        f"  recipes with portions_count_resolved: {portions_count}/{recipes_total} ({pct:.0f}%)"
    )

    src_cur.close()
    tgt_cur.close()
    return all_ok


def main():
    parser = argparse.ArgumentParser(description="Seed Docker PostgreSQL from Neon")
    parser.add_argument(
        "--source",
        default=os.environ.get("NEON_DATABASE_URL"),
        help="Neon source connection string",
    )
    parser.add_argument(
        "--target",
        default=os.environ.get("DATABASE_URL"),
        help="Docker PostgreSQL target connection string",
    )
    args = parser.parse_args()

    if not args.source or not args.target:
        print("ERROR: Both --source and --target are required (or set NEON_DATABASE_URL / DATABASE_URL)")
        sys.exit(1)

    print(f"Source: {args.source[:50]}...")
    print(f"Target: {args.target[:50]}...")
    print()

    src, tgt = get_connections(args.source, args.target)
    src_cur = src.cursor()
    tgt_cur = tgt.cursor()

    # Disable RLS for the migration session so we can insert without setting tenant context
    tgt_cur.execute("SET app.current_tenant_id = %s", (REAL_TENANT_ID,))

    steps = [
        ("Seed allergens", lambda: step_seed_allergens(tgt_cur)),
        ("Seed additives", lambda: step_seed_additives(tgt_cur)),
        ("Seed units", lambda: step_seed_units(tgt_cur)),
        ("Migrate tenants", lambda: step_migrate_tenants(src_cur, tgt_cur)),
        ("Migrate ingredients", lambda: step_migrate_ingredients(src_cur, tgt_cur)),
        ("Migrate ingredient nutrition", lambda: step_migrate_ingredient_nutrition(src_cur, tgt_cur)),
        ("Migrate ingredient prices", lambda: step_migrate_ingredient_prices(src_cur, tgt_cur)),
        ("Migrate ingredient-allergen links", lambda: step_migrate_ingredient_allergens(src_cur, tgt_cur)),
        ("Migrate ingredient-additive links", lambda: step_migrate_ingredient_additives(src_cur, tgt_cur)),
        ("Migrate categories", lambda: step_migrate_categories(src_cur, tgt_cur)),
        ("Migrate recipes", lambda: step_migrate_recipes(src_cur, tgt_cur)),
        ("Migrate recipe ingredients", lambda: step_migrate_recipe_ingredients(src_cur, tgt_cur)),
        ("Backfill recipe yield metrics", lambda: step_backfill_recipe_yield_metrics(tgt_cur)),
        ("Migrate recipe nutrition cache", lambda: step_migrate_recipe_nutrition_cache(src_cur, tgt_cur)),
        ("Create default agent", lambda: step_create_default_agent(tgt_cur)),
    ]

    for i, (name, func) in enumerate(steps, 1):
        print(f"[{i}/{len(steps)}] {name}")
        try:
            count = func()
            print(f"  -> {count} rows\n")
        except Exception as e:
            print(f"  -> ERROR: {e}")
            tgt.rollback()
            src_cur.close()
            tgt_cur.close()
            src.close()
            tgt.close()
            sys.exit(1)

    tgt.commit()
    print("All steps committed successfully.\n")

    ok = validate(src, tgt)

    src_cur.close()
    tgt_cur.close()
    src.close()
    tgt.close()

    if ok:
        print("\nMigration completed successfully.")
    else:
        print("\nMigration completed with warnings. Review mismatches above.")
        sys.exit(1)


if __name__ == "__main__":
    main()
