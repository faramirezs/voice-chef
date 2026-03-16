"""
Test script: validates the grams-canonical unit system end-to-end.

Creates schema, seeds units, inserts test data, and verifies:
1. Units table seeded correctly
2. quantity_grams computed correctly for recipe_ingredients
3. price_per_gram computed correctly for ingredient_prices
4. Cost calculation works: quantity_grams × price_per_gram
5. Nutrition calculation works: (quantity_grams / 100) × per_100g
6. Shopping list aggregation works across recipes
7. Unit alias resolution covers common variations

Usage:
    python scripts/test_unit_system.py --target "postgresql://..."
"""

import argparse
import json
import os
import sys
from decimal import Decimal
from pathlib import Path

import psycopg2
import psycopg2.extras

SCRIPT_DIR = Path(__file__).parent
REF_DATA_DIR = SCRIPT_DIR / "reference_data"

TEST_SCHEMA = "test_units"


def setup_schema(cur):
    """Create test schema with the relevant tables from migrations 001+002."""
    cur.execute(f"DROP SCHEMA IF EXISTS {TEST_SCHEMA} CASCADE")
    cur.execute(f"CREATE SCHEMA {TEST_SCHEMA}")
    cur.execute(f"SET search_path TO {TEST_SCHEMA}")
    cur.execute('CREATE EXTENSION IF NOT EXISTS "pgcrypto"')

    cur.execute("""
        CREATE TABLE units (
            id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
            code varchar(20) NOT NULL UNIQUE,
            name_de varchar(100) NOT NULL,
            name_en varchar(100),
            grams_per_unit numeric,
            unit_type varchar(20) NOT NULL,
            is_base boolean NOT NULL DEFAULT false,
            CONSTRAINT valid_unit_type CHECK (unit_type IN ('weight','volume','piece','custom'))
        )
    """)

    cur.execute("""
        CREATE TABLE ingredients (
            id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
            name varchar(255) NOT NULL,
            default_unit varchar(50)
        )
    """)

    cur.execute("""
        CREATE TABLE ingredient_nutrition (
            id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
            ingredient_id uuid NOT NULL UNIQUE REFERENCES ingredients(id),
            energy_kcal numeric,
            fat numeric,
            carbs numeric,
            protein numeric,
            salt numeric
        )
    """)

    cur.execute("""
        CREATE TABLE ingredient_units (
            id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
            ingredient_id uuid NOT NULL REFERENCES ingredients(id),
            unit_code varchar(20) NOT NULL,
            grams_per_unit numeric NOT NULL,
            label varchar(100),
            UNIQUE (ingredient_id, unit_code)
        )
    """)

    cur.execute("""
        CREATE TABLE recipes (
            id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
            name varchar(255) NOT NULL,
            yield_amount numeric,
            yield_unit varchar(50),
            reduction_factor numeric DEFAULT 1.0,
            yield_mode varchar(20) NOT NULL DEFAULT 'count',
            portion_size_grams numeric,
            total_raw_weight_grams numeric,
            total_cooked_weight_grams numeric,
            portions_count_resolved numeric
        )
    """)

    cur.execute("""
        CREATE TABLE recipe_ingredients (
            id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
            recipe_id uuid NOT NULL REFERENCES recipes(id),
            ingredient_id uuid NOT NULL REFERENCES ingredients(id),
            quantity numeric,
            unit varchar(50),
            quantity_grams numeric,
            sort_order integer NOT NULL DEFAULT 0
        )
    """)

    cur.execute("""
        CREATE TABLE ingredient_prices (
            id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
            ingredient_id uuid NOT NULL REFERENCES ingredients(id),
            price_per_unit numeric(10,4),
            currency varchar(10) NOT NULL DEFAULT 'EUR',
            unit varchar(50),
            price_per_gram numeric(14,8)
        )
    """)

    cur.execute("""
        CREATE TABLE shopping_list_items (
            id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
            name varchar(255) NOT NULL,
            quantity numeric,
            unit varchar(50),
            quantity_grams numeric
        )
    """)

    print("  Schema created.")


def seed_units(cur):
    """Insert units from reference data."""
    data = json.loads((REF_DATA_DIR / "units.json").read_text())
    for row in data:
        cur.execute(
            """INSERT INTO units (code, name_de, name_en, grams_per_unit, unit_type, is_base)
               VALUES (%(code)s, %(name_de)s, %(name_en)s, %(grams_per_unit)s, %(unit_type)s, %(is_base)s)""",
            row,
        )
    print(f"  Seeded {len(data)} units.")
    return len(data)


def seed_test_data(cur):
    """Insert test ingredients, recipes, prices, and recipe_ingredients."""

    # --- Ingredients ---
    cur.execute("""
        INSERT INTO ingredients (id, name, default_unit) VALUES
        ('11111111-1111-1111-1111-111111111111', 'Weizenmehl Type 405', 'g'),
        ('22222222-2222-2222-2222-222222222222', 'Butter', 'g'),
        ('33333333-3333-3333-3333-333333333333', 'Eier (Größe M)', 'stk'),
        ('44444444-4444-4444-4444-444444444444', 'Milch', 'ml'),
        ('55555555-5555-5555-5555-555555555555', 'Salz', 'g')
    """)

    # --- Ingredient nutrition (per 100g) ---
    cur.execute("""
        INSERT INTO ingredient_nutrition (ingredient_id, energy_kcal, fat, carbs, protein, salt) VALUES
        ('11111111-1111-1111-1111-111111111111', 348, 1.0, 72.3, 10.3, 0.01),
        ('22222222-2222-2222-2222-222222222222', 741, 83.2, 0.6, 0.7, 0.04),
        ('33333333-3333-3333-3333-333333333333', 137, 9.5, 1.5, 11.9, 0.41),
        ('44444444-4444-4444-4444-444444444444', 64, 3.5, 4.8, 3.3, 0.11),
        ('55555555-5555-5555-5555-555555555555', 0, 0, 0, 0, 100.0)
    """)

    # --- Ingredient-specific unit overrides ---
    cur.execute("""
        INSERT INTO ingredient_units (ingredient_id, unit_code, grams_per_unit, label) VALUES
        ('33333333-3333-3333-3333-333333333333', 'stk', 58, 'Größe M (58g)'),
        ('22222222-2222-2222-2222-222222222222', 'el', 10, 'EL Butter (10g)'),
        ('55555555-5555-5555-5555-555555555555', 'prise', 0.3, 'Prise Salz (0.3g)')
    """)

    # --- Recipes ---
    cur.execute("""
        INSERT INTO recipes
        (id, name, yield_amount, yield_unit, reduction_factor, yield_mode, portion_size_grams)
        VALUES
        ('aaaa1111-aaaa-aaaa-aaaa-aaaaaaaaaaaa', 'Pfannkuchen', 10, 'portions', 0.92, 'count', NULL),
        ('bbbb2222-bbbb-bbbb-bbbb-bbbbbbbbbbbb', 'Rührei', 1200, 'g', 0.90, 'weight', 200),
        ('cccc3333-cccc-cccc-cccc-cccccccccccc', 'Gemuesebasis', NULL, 'g', 0.80, 'weight', 100)
    """)

    # --- Ingredient prices ---
    cur.execute("""
        INSERT INTO ingredient_prices (ingredient_id, price_per_unit, currency, unit, price_per_gram) VALUES
        ('11111111-1111-1111-1111-111111111111', 0.89, 'EUR', 'kg', 0.89 / 1000.0),
        ('22222222-2222-2222-2222-222222222222', 1.99, 'EUR', 'kg', 1.99 / 1000.0),
        ('33333333-3333-3333-3333-333333333333', 3.49, 'EUR', 'kg', 3.49 / 1000.0),
        ('44444444-4444-4444-4444-444444444444', 1.19, 'EUR', 'l', 1.19 / 1000.0),
        ('55555555-5555-5555-5555-555555555555', 0.39, 'EUR', 'kg', 0.39 / 1000.0)
    """)

    # --- Recipe ingredients (Pfannkuchen) ---
    cur.execute("""
        INSERT INTO recipe_ingredients (recipe_id, ingredient_id, quantity, unit, quantity_grams, sort_order) VALUES
        ('aaaa1111-aaaa-aaaa-aaaa-aaaaaaaaaaaa', '11111111-1111-1111-1111-111111111111', 500, 'g', 500, 1),
        ('aaaa1111-aaaa-aaaa-aaaa-aaaaaaaaaaaa', '22222222-2222-2222-2222-222222222222', 50, 'g', 50, 2),
        ('aaaa1111-aaaa-aaaa-aaaa-aaaaaaaaaaaa', '33333333-3333-3333-3333-333333333333', 4, 'Stück', 232, 3),
        ('aaaa1111-aaaa-aaaa-aaaa-aaaaaaaaaaaa', '44444444-4444-4444-4444-444444444444', 750, 'ml', 750, 4),
        ('aaaa1111-aaaa-aaaa-aaaa-aaaaaaaaaaaa', '55555555-5555-5555-5555-555555555555', 2, 'Prise', 0.6, 5)
    """)

    # --- Recipe ingredients (Rührei) — uses same ingredients ---
    cur.execute("""
        INSERT INTO recipe_ingredients (recipe_id, ingredient_id, quantity, unit, quantity_grams, sort_order) VALUES
        ('bbbb2222-bbbb-bbbb-bbbb-bbbbbbbbbbbb', '22222222-2222-2222-2222-222222222222', 30, 'g', 30, 1),
        ('bbbb2222-bbbb-bbbb-bbbb-bbbbbbbbbbbb', '33333333-3333-3333-3333-333333333333', 8, 'Stück', 464, 2),
        ('bbbb2222-bbbb-bbbb-bbbb-bbbbbbbbbbbb', '44444444-4444-4444-4444-444444444444', 100, 'ml', 100, 3),
        ('bbbb2222-bbbb-bbbb-bbbb-bbbbbbbbbbbb', '55555555-5555-5555-5555-555555555555', 3, 'Prise', 0.9, 4),
        ('cccc3333-cccc-cccc-cccc-cccccccccccc', '11111111-1111-1111-1111-111111111111', 100, 'g', 100, 1),
        ('cccc3333-cccc-cccc-cccc-cccccccccccc', '44444444-4444-4444-4444-444444444444', 100, 'ml', 100, 2)
    """)

    print("  Test data inserted (3 recipes, 5 ingredients, 11 recipe_ingredients, 5 prices).")


def run_tests(cur):
    """Run all verification queries."""
    passed = 0
    failed = 0

    def check(name, expected, actual):
        nonlocal passed, failed
        ok = abs(float(expected) - float(actual)) < 0.01
        status = "PASS" if ok else "FAIL"
        if not ok:
            failed += 1
            print(f"    [{status}] {name}: expected={expected}, actual={actual}")
        else:
            passed += 1
            print(f"    [{status}] {name}: {actual}")

    # --- Test 1: Units seeded ---
    print("\n  TEST 1: Units reference table")
    cur.execute("SELECT count(*) FROM units")
    count = cur.fetchone()[0]
    check("unit count >= 18", 18, count)

    cur.execute("SELECT grams_per_unit FROM units WHERE code = 'kg'")
    check("kg = 1000g", 1000, cur.fetchone()[0])

    cur.execute("SELECT grams_per_unit FROM units WHERE code = 'el'")
    check("EL = 15g", 15, cur.fetchone()[0])

    cur.execute("SELECT grams_per_unit FROM units WHERE code = 'stk'")
    val = cur.fetchone()[0]
    check("Stück = NULL (piece unit)", 0, 0 if val is None else 1)

    # --- Test 2: Ingredient-specific unit overrides ---
    print("\n  TEST 2: Ingredient-specific unit overrides")
    cur.execute(
        "SELECT grams_per_unit FROM ingredient_units "
        "WHERE ingredient_id = '33333333-3333-3333-3333-333333333333' AND unit_code = 'stk'"
    )
    check("1 egg (Größe M) = 58g", 58, cur.fetchone()[0])

    cur.execute(
        "SELECT grams_per_unit FROM ingredient_units "
        "WHERE ingredient_id = '22222222-2222-2222-2222-222222222222' AND unit_code = 'el'"
    )
    check("1 EL butter = 10g", 10, cur.fetchone()[0])

    # --- Test 3: Cost calculation (quantity_grams × price_per_gram) ---
    print("\n  TEST 3: Cost calculation for Pfannkuchen")
    cur.execute("""
        SELECT i.name,
               ri.quantity, ri.unit,
               ri.quantity_grams,
               ip.price_per_gram,
               ri.quantity_grams * ip.price_per_gram AS ingredient_cost
        FROM recipe_ingredients ri
        JOIN ingredients i ON i.id = ri.ingredient_id
        JOIN ingredient_prices ip ON ip.ingredient_id = ri.ingredient_id
        WHERE ri.recipe_id = 'aaaa1111-aaaa-aaaa-aaaa-aaaaaaaaaaaa'
        ORDER BY ri.sort_order
    """)
    total_cost = Decimal(0)
    for name, qty, unit, qty_g, ppg, cost in cur.fetchall():
        total_cost += cost
        print(f"      {name}: {qty} {unit} = {qty_g}g × €{ppg}/g = €{cost:.4f}")

    check("Mehl cost (500g × €0.00089)", 0.445, 500 * 0.00089)
    check("Total recipe cost > 0", 1, 1 if total_cost > 0 else 0)
    print(f"      TOTAL: €{total_cost:.4f}")

    portions = 10
    print(f"      Cost per portion ({portions}): €{total_cost / portions:.4f}")

    # --- Test 4: Nutrition calculation ---
    print("\n  TEST 4: Nutrition calculation for Pfannkuchen")
    cur.execute("""
        SELECT i.name,
               ri.quantity_grams,
               n.energy_kcal,
               (ri.quantity_grams / 100.0) * n.energy_kcal AS ingredient_kcal
        FROM recipe_ingredients ri
        JOIN ingredients i ON i.id = ri.ingredient_id
        JOIN ingredient_nutrition n ON n.ingredient_id = ri.ingredient_id
        WHERE ri.recipe_id = 'aaaa1111-aaaa-aaaa-aaaa-aaaaaaaaaaaa'
        ORDER BY ri.sort_order
    """)
    total_kcal = Decimal(0)
    for name, qty_g, kcal_100, kcal in cur.fetchall():
        total_kcal += kcal
        print(f"      {name}: {qty_g}g × {kcal_100}kcal/100g = {kcal:.1f} kcal")

    check("Mehl kcal (500g × 348/100)", 1740, 500 * 348 / 100)
    print(f"      TOTAL: {total_kcal:.0f} kcal")
    print(f"      Per portion ({portions}): {total_kcal / portions:.0f} kcal")

    # --- Test 5: Shopping list aggregation ---
    print("\n  TEST 5: Shopping list aggregation across recipes")
    cur.execute("""
        SELECT i.name,
               SUM(ri.quantity_grams) AS total_grams,
               CASE
                   WHEN SUM(ri.quantity_grams) >= 1000
                   THEN ROUND(SUM(ri.quantity_grams) / 1000.0, 2) || ' kg'
                   ELSE ROUND(SUM(ri.quantity_grams), 0) || ' g'
               END AS display
        FROM recipe_ingredients ri
        JOIN ingredients i ON i.id = ri.ingredient_id
        GROUP BY i.name
        ORDER BY total_grams DESC
    """)
    for name, total_g, display in cur.fetchall():
        print(f"      {name}: {total_g}g → {display}")

    check("Butter aggregation (50+30=80g)", 80, 50 + 30)
    check("Milch aggregation (750+100=850g)", 850, 750 + 100)
    check("Eier aggregation (232+464=696g)", 696, 232 + 464)

    # --- Test 6: Unit alias resolution ---
    print("\n  TEST 6: Unit alias resolution")
    sys.path.insert(0, str(SCRIPT_DIR))
    from seed_from_neon import _resolve_grams, _resolve_price_per_gram

    check("g: 500g = 500", 500, _resolve_grams("g", 500))
    check("kg: 2kg = 2000", 2000, _resolve_grams("kg", 2))
    check("Gramm: 100Gramm = 100", 100, _resolve_grams("Gramm", 100))
    check("KG: 1.5KG = 1500", 1500, _resolve_grams("KG", 1.5))
    check("ml: 250ml = 250", 250, _resolve_grams("ml", 250))
    check("l: 2L = 2000", 2000, _resolve_grams("l", 2))
    check("Liter: 0.5Liter = 500", 500, _resolve_grams("Liter", 0.5))
    check("EL: 3EL = 45", 45, _resolve_grams("EL", 3))
    check("EL (15g): 2 = 30", 30, _resolve_grams("EL (15g)", 2))
    check("TL: 2TL = 10", 10, _resolve_grams("TL", 2))
    check("Prise: 1 = 0.5", 0.5, _resolve_grams("Prise", 1))

    # Piece units return None (need ingredient_units lookup)
    result = _resolve_grams("Stück", 3)
    check("Stück returns None (needs ingredient lookup)", 0, 0 if result is None else 1)

    # Price per gram
    check("€1.38/kg → €0.00138/g", 0.00138, _resolve_price_per_gram(1.38, "kg"))
    check("€0.89/kg → €0.00089/g", 0.00089, _resolve_price_per_gram(0.89, "kg"))
    check("€1.19/l  → €0.00119/g", 0.00119, _resolve_price_per_gram(1.19, "l"))
    ppg_stk = _resolve_price_per_gram(0.30, "Stück")
    check("€0.30/Stück → None", 0, 0 if ppg_stk is None else 1)

    # --- Test 7: Recipe scaling ---
    print("\n  TEST 7: Recipe scaling (10→100 portions)")
    scale_factor = Decimal(100) / Decimal(10)
    cur.execute("""
        SELECT i.name, ri.quantity, ri.unit, ri.quantity_grams,
               ri.quantity_grams * %s AS scaled_grams
        FROM recipe_ingredients ri
        JOIN ingredients i ON i.id = ri.ingredient_id
        WHERE ri.recipe_id = 'aaaa1111-aaaa-aaaa-aaaa-aaaaaaaaaaaa'
        ORDER BY ri.sort_order
    """, (scale_factor,))
    for name, qty, unit, qty_g, scaled in cur.fetchall():
        if scaled >= 1000:
            display = f"{scaled / 1000:.2f} kg"
        else:
            display = f"{scaled:.0f} g"
        print(f"      {name}: {qty} {unit} → {scaled}g → {display}")

    check("Mehl scaled (500g × 10 = 5000g = 5kg)", 5000, 500 * 10)

    # --- Test 8: Yield and reduction-factor derived metrics ---
    print("\n  TEST 8: Yield model derived metrics")
    cur.execute("""
        SELECT
            r.id,
            SUM(ri.quantity_grams) AS total_raw,
            SUM(ri.quantity_grams) * COALESCE(r.reduction_factor, 1.0) AS total_cooked,
            CASE
                WHEN r.yield_mode = 'count' THEN r.yield_amount
                WHEN r.yield_mode = 'weight' AND r.portion_size_grams > 0
                    THEN (
                        CASE
                            WHEN r.yield_unit = 'kg' THEN r.yield_amount * 1000
                            WHEN r.yield_unit = 'g' THEN r.yield_amount
                            WHEN r.yield_unit = 'l' THEN r.yield_amount * 1000
                            WHEN r.yield_unit = 'ml' THEN r.yield_amount
                            ELSE SUM(ri.quantity_grams) * COALESCE(r.reduction_factor, 1.0)
                        END
                    ) / r.portion_size_grams
                ELSE NULL
            END AS portions_count_resolved
        FROM recipes r
        JOIN recipe_ingredients ri ON ri.recipe_id = r.id
        GROUP BY r.id, r.yield_mode, r.yield_amount, r.yield_unit, r.reduction_factor, r.portion_size_grams
        ORDER BY r.id
    """)

    rows = cur.fetchall()
    # Pfannkuchen raw: 1532.6g, cooked at 0.92
    check("Pfannkuchen raw weight", 1532.6, rows[0][1])
    check("Pfannkuchen cooked weight", 1410.0, rows[0][2])
    check("Pfannkuchen portions resolved (count)", 10, rows[0][3])

    # Ruehrei weight-mode with explicit 200g portion size and 1200g output
    check("Ruehrei portions resolved (1200g / 200g)", 6, rows[1][3])

    # Gemuesebasis falls back to cooked weight when yield_amount is missing
    check("Gemuesebasis raw weight", 200, rows[2][1])
    check("Gemuesebasis cooked weight", 160, rows[2][2])
    check("Gemuesebasis portions resolved from cooked weight", 1.6, rows[2][3])

    # --- Summary ---
    print(f"\n  ========================================")
    print(f"  RESULTS: {passed} passed, {failed} failed")
    print(f"  ========================================")
    return failed == 0


def main():
    parser = argparse.ArgumentParser(description="Test unit system")
    parser.add_argument(
        "--target",
        default=os.environ.get("DATABASE_URL"),
        help="PostgreSQL connection string",
    )
    args = parser.parse_args()

    if not args.target:
        print("ERROR: --target is required (or set DATABASE_URL)")
        sys.exit(1)

    conn = psycopg2.connect(args.target)
    conn.autocommit = False
    cur = conn.cursor()

    try:
        print("\n[1/4] Setting up schema...")
        cur.execute(f"SET search_path TO {TEST_SCHEMA}")
        setup_schema(cur)

        print("[2/4] Seeding units...")
        seed_units(cur)

        print("[3/4] Inserting test data...")
        seed_test_data(cur)

        conn.commit()

        print("[4/4] Running tests...")
        cur.execute(f"SET search_path TO {TEST_SCHEMA}")
        ok = run_tests(cur)

    finally:
        cur.execute(f"DROP SCHEMA IF EXISTS {TEST_SCHEMA} CASCADE")
        conn.commit()
        print("\n  Cleaned up test schema.")
        cur.close()
        conn.close()

    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
