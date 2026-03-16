\echo '=== Cost and Yield Audit ==='

\echo ''
\echo '1) Alembic revision'
SELECT version_num FROM public.alembic_version;

\echo ''
\echo '2) Canonical schema presence (002 + 003)'
SELECT
    'units table' AS object,
    CASE WHEN EXISTS (
        SELECT 1 FROM information_schema.tables
        WHERE table_schema = 'public' AND table_name = 'units'
    ) THEN 'present' ELSE 'missing' END AS status
UNION ALL
SELECT
    'ingredient_units table',
    CASE WHEN EXISTS (
        SELECT 1 FROM information_schema.tables
        WHERE table_schema = 'public' AND table_name = 'ingredient_units'
    ) THEN 'present' ELSE 'missing' END
UNION ALL
SELECT
    'recipe_ingredients.quantity_grams',
    CASE WHEN EXISTS (
        SELECT 1 FROM information_schema.columns
        WHERE table_schema = 'public' AND table_name = 'recipe_ingredients' AND column_name = 'quantity_grams'
    ) THEN 'present' ELSE 'missing' END
UNION ALL
SELECT
    'ingredient_prices.price_per_gram',
    CASE WHEN EXISTS (
        SELECT 1 FROM information_schema.columns
        WHERE table_schema = 'public' AND table_name = 'ingredient_prices' AND column_name = 'price_per_gram'
    ) THEN 'present' ELSE 'missing' END
UNION ALL
SELECT
    'shopping_list_items.quantity_grams',
    CASE WHEN EXISTS (
        SELECT 1 FROM information_schema.columns
        WHERE table_schema = 'public' AND table_name = 'shopping_list_items' AND column_name = 'quantity_grams'
    ) THEN 'present' ELSE 'missing' END
UNION ALL
SELECT
    'recipes.yield_mode',
    CASE WHEN EXISTS (
        SELECT 1 FROM information_schema.columns
        WHERE table_schema = 'public' AND table_name = 'recipes' AND column_name = 'yield_mode'
    ) THEN 'present' ELSE 'missing' END
UNION ALL
SELECT
    'recipes.portion_size_grams',
    CASE WHEN EXISTS (
        SELECT 1 FROM information_schema.columns
        WHERE table_schema = 'public' AND table_name = 'recipes' AND column_name = 'portion_size_grams'
    ) THEN 'present' ELSE 'missing' END
UNION ALL
SELECT
    'recipes.total_raw_weight_grams',
    CASE WHEN EXISTS (
        SELECT 1 FROM information_schema.columns
        WHERE table_schema = 'public' AND table_name = 'recipes' AND column_name = 'total_raw_weight_grams'
    ) THEN 'present' ELSE 'missing' END
UNION ALL
SELECT
    'recipes.total_cooked_weight_grams',
    CASE WHEN EXISTS (
        SELECT 1 FROM information_schema.columns
        WHERE table_schema = 'public' AND table_name = 'recipes' AND column_name = 'total_cooked_weight_grams'
    ) THEN 'present' ELSE 'missing' END
UNION ALL
SELECT
    'recipes.portions_count_resolved',
    CASE WHEN EXISTS (
        SELECT 1 FROM information_schema.columns
        WHERE table_schema = 'public' AND table_name = 'recipes' AND column_name = 'portions_count_resolved'
    ) THEN 'present' ELSE 'missing' END;

\echo ''
\echo '3) Core table counts'
SELECT 'recipes' AS table_name, COUNT(*) AS row_count FROM public.recipes
UNION ALL SELECT 'recipe_ingredients', COUNT(*) FROM public.recipe_ingredients
UNION ALL SELECT 'ingredient_prices', COUNT(*) FROM public.ingredient_prices
UNION ALL SELECT 'ingredients', COUNT(*) FROM public.ingredients;

\echo ''
\echo '4) Price coverage metrics (legacy and canonical)'
WITH latest_price AS (
    SELECT DISTINCT ON (ingredient_id, COALESCE(unit, ''))
        ingredient_id,
        unit,
        price_per_unit,
        price_per_gram,
        currency,
        updated_at,
        created_at
    FROM public.ingredient_prices
    ORDER BY ingredient_id, COALESCE(unit, ''), updated_at DESC NULLS LAST, created_at DESC NULLS LAST
),
exact_match AS (
    SELECT COUNT(*) AS cnt
    FROM public.recipe_ingredients ri
    JOIN latest_price lp
      ON lp.ingredient_id = ri.ingredient_id
     AND COALESCE(lp.unit, '') = COALESCE(ri.unit, '')
),
nullable_unit_match AS (
    SELECT COUNT(*) AS cnt
    FROM public.recipe_ingredients ri
    JOIN latest_price lp
      ON lp.ingredient_id = ri.ingredient_id
     AND (lp.unit IS NULL OR lp.unit = ri.unit)
),
canonical_match AS (
    SELECT COUNT(*) AS cnt
    FROM public.recipe_ingredients ri
    JOIN latest_price lp
      ON lp.ingredient_id = ri.ingredient_id
    WHERE lp.price_per_gram IS NOT NULL
      AND ri.quantity_grams IS NOT NULL
),
totals AS (
    SELECT COUNT(*) AS total_lines FROM public.recipe_ingredients
)
SELECT
    t.total_lines,
    e.cnt AS exact_unit_priced_lines,
    ROUND((e.cnt::numeric / NULLIF(t.total_lines, 0)) * 100, 2) AS exact_unit_coverage_pct,
    n.cnt AS nullable_unit_priced_lines,
    ROUND((n.cnt::numeric / NULLIF(t.total_lines, 0)) * 100, 2) AS nullable_unit_coverage_pct,
    c.cnt AS canonical_priced_lines,
    ROUND((c.cnt::numeric / NULLIF(t.total_lines, 0)) * 100, 2) AS canonical_coverage_pct
FROM totals t
CROSS JOIN exact_match e
CROSS JOIN nullable_unit_match n
CROSS JOIN canonical_match c;

\echo ''
\echo '5) Null rates for cost fields'
SELECT
    COUNT(*) AS total_prices,
    COUNT(*) FILTER (WHERE price_per_unit IS NULL) AS price_per_unit_nulls,
    ROUND((COUNT(*) FILTER (WHERE price_per_unit IS NULL))::numeric * 100 / NULLIF(COUNT(*), 0), 2) AS price_per_unit_null_pct,
    COUNT(*) FILTER (WHERE currency IS NULL) AS currency_nulls,
    ROUND((COUNT(*) FILTER (WHERE currency IS NULL))::numeric * 100 / NULLIF(COUNT(*), 0), 2) AS currency_null_pct
FROM public.ingredient_prices;

SELECT EXISTS (
    SELECT 1
    FROM information_schema.columns
    WHERE table_schema = 'public'
      AND table_name = 'ingredient_prices'
      AND column_name = 'price_per_gram'
) AS has_price_per_gram \gset

\if :has_price_per_gram
SELECT
    COUNT(*) FILTER (WHERE price_per_gram IS NULL) AS price_per_gram_nulls,
    ROUND((COUNT(*) FILTER (WHERE price_per_gram IS NULL))::numeric * 100 / NULLIF(COUNT(*), 0), 2) AS price_per_gram_null_pct
FROM public.ingredient_prices;
\else
SELECT
    NULL::bigint AS price_per_gram_nulls,
    NULL::numeric AS price_per_gram_null_pct,
    'price_per_gram column missing'::text AS note;
\endif

\echo ''
\echo '6) Duplicate prices by ingredient_id + unit'
SELECT ingredient_id, COALESCE(unit, '<null>') AS unit_key, COUNT(*) AS duplicate_count
FROM public.ingredient_prices
GROUP BY ingredient_id, COALESCE(unit, '<null>')
HAVING COUNT(*) > 1
ORDER BY duplicate_count DESC, ingredient_id
LIMIT 20;

\echo ''
\echo '7) Population of 003 recipe fields'
SELECT
    COUNT(*) AS total_recipes,
    COUNT(*) FILTER (WHERE yield_mode IS NOT NULL) AS recipes_with_yield_mode,
    COUNT(*) FILTER (WHERE portion_size_grams IS NOT NULL) AS recipes_with_portion_size_grams,
    COUNT(*) FILTER (WHERE total_raw_weight_grams IS NOT NULL) AS recipes_with_total_raw_weight_grams,
    COUNT(*) FILTER (WHERE total_cooked_weight_grams IS NOT NULL) AS recipes_with_total_cooked_weight_grams,
    COUNT(*) FILTER (WHERE portions_count_resolved IS NOT NULL) AS recipes_with_portions_count_resolved
FROM public.recipes;
