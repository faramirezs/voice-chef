\echo '=== Backfill canonical fields (002 + 003) ==='

BEGIN;

-- 1) Normalize/seed common unit aliases used in current dataset.
INSERT INTO public.units (code, name_de, name_en, grams_per_unit, unit_type, is_base)
VALUES
    ('stk', 'Stueck', 'piece', NULL, 'piece', false),
    ('stck', 'Stueck', 'piece', NULL, 'piece', false)
ON CONFLICT (code) DO NOTHING;

\echo ''
\echo '1) Backfill recipe_ingredients.quantity_grams'
WITH updated AS (
    UPDATE public.recipe_ingredients ri
    SET quantity_grams = ri.quantity * u.grams_per_unit
    FROM public.units u
    WHERE ri.quantity_grams IS NULL
      AND ri.quantity IS NOT NULL
      AND u.grams_per_unit IS NOT NULL
      AND LOWER(TRIM(COALESCE(ri.unit, ''))) = LOWER(TRIM(u.code))
    RETURNING ri.id
)
SELECT COUNT(*) AS recipe_ingredients_updated FROM updated;

\echo ''
\echo '2) Backfill ingredient_prices.price_per_gram'
WITH updated AS (
    UPDATE public.ingredient_prices ip
    SET price_per_gram = ip.price_per_unit / u.grams_per_unit
    FROM public.units u
    WHERE ip.price_per_gram IS NULL
      AND ip.price_per_unit IS NOT NULL
      AND u.grams_per_unit IS NOT NULL
      AND u.grams_per_unit > 0
      AND LOWER(TRIM(COALESCE(ip.unit, ''))) = LOWER(TRIM(u.code))
    RETURNING ip.id
)
SELECT COUNT(*) AS ingredient_prices_updated FROM updated;

\echo ''
\echo '3) Backfill recipes.total_raw_weight_grams from ingredient grams'
WITH summed AS (
    SELECT
        ri.recipe_id,
        SUM(ri.quantity_grams) AS total_raw_weight_grams
    FROM public.recipe_ingredients ri
    WHERE ri.quantity_grams IS NOT NULL
    GROUP BY ri.recipe_id
),
updated AS (
    UPDATE public.recipes r
    SET total_raw_weight_grams = s.total_raw_weight_grams
    FROM summed s
    WHERE r.id = s.recipe_id
      AND r.total_raw_weight_grams IS NULL
    RETURNING r.id
)
SELECT COUNT(*) AS recipes_total_raw_weight_updated FROM updated;

\echo ''
\echo '4) Backfill recipes.portions_count_resolved'
WITH updated AS (
    UPDATE public.recipes r
    SET portions_count_resolved = CASE
        WHEN r.yield_mode = 'count' AND r.yield_amount IS NOT NULL AND r.yield_amount > 0 THEN r.yield_amount
        WHEN r.yield_mode = 'weight' AND r.portion_size_grams IS NOT NULL AND r.portion_size_grams > 0
             AND COALESCE(r.total_cooked_weight_grams, r.total_raw_weight_grams) IS NOT NULL
             AND COALESCE(r.total_cooked_weight_grams, r.total_raw_weight_grams) > 0
        THEN COALESCE(r.total_cooked_weight_grams, r.total_raw_weight_grams) / r.portion_size_grams
        ELSE r.portions_count_resolved
    END
    WHERE r.portions_count_resolved IS NULL
      AND (
        (r.yield_mode = 'count' AND r.yield_amount IS NOT NULL AND r.yield_amount > 0)
        OR
        (r.yield_mode = 'weight' AND r.portion_size_grams IS NOT NULL AND r.portion_size_grams > 0
         AND COALESCE(r.total_cooked_weight_grams, r.total_raw_weight_grams) IS NOT NULL
         AND COALESCE(r.total_cooked_weight_grams, r.total_raw_weight_grams) > 0)
      )
    RETURNING r.id
)
SELECT COUNT(*) AS recipes_portions_resolved_updated FROM updated;

COMMIT;

\echo ''
\echo '=== Post-backfill quick metrics ==='
SELECT
    COUNT(*) FILTER (WHERE quantity_grams IS NOT NULL) AS recipe_ingredients_with_quantity_grams,
    COUNT(*) AS recipe_ingredients_total
FROM public.recipe_ingredients;

SELECT
    COUNT(*) FILTER (WHERE price_per_gram IS NOT NULL) AS ingredient_prices_with_price_per_gram,
    COUNT(*) AS ingredient_prices_total
FROM public.ingredient_prices;

SELECT
    COUNT(*) FILTER (WHERE total_raw_weight_grams IS NOT NULL) AS recipes_with_total_raw_weight_grams,
    COUNT(*) FILTER (WHERE portions_count_resolved IS NOT NULL) AS recipes_with_portions_count_resolved,
    COUNT(*) AS recipes_total
FROM public.recipes;
