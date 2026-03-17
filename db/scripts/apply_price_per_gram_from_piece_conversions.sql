\echo '=== Apply price_per_gram from ingredient_units piece conversions ==='

BEGIN;

-- Update ONLY unresolved price rows, using ingredient-specific conversion first.
WITH updated AS (
    UPDATE public.ingredient_prices ip
    SET price_per_gram = ip.price_per_unit / iu.grams_per_unit
    FROM public.ingredient_units iu
    WHERE ip.price_per_gram IS NULL
      AND ip.price_per_unit IS NOT NULL
      AND iu.grams_per_unit > 0
      AND ip.ingredient_id = iu.ingredient_id
      AND LOWER(TRIM(COALESCE(ip.unit, ''))) = LOWER(TRIM(COALESCE(iu.unit_code, '')))
    RETURNING ip.id, ip.ingredient_id, ip.unit, ip.price_per_unit, ip.price_per_gram
)
SELECT COUNT(*) AS updated_price_rows FROM updated;

COMMIT;

\echo ''
\echo '=== Remaining unresolved price_per_gram rows ==='
SELECT
    ip.id AS price_id,
    ip.ingredient_id,
    i.name AS ingredient,
    ip.unit,
    ip.price_per_unit,
    ip.currency
FROM public.ingredient_prices ip
JOIN public.ingredients i ON i.id = ip.ingredient_id
WHERE ip.price_per_gram IS NULL
ORDER BY ingredient, ip.unit;

\echo ''
\echo '=== Current null rate ==='
SELECT
    COUNT(*) FILTER (WHERE ip.price_per_gram IS NULL) AS price_per_gram_nulls,
    COUNT(*) AS total_price_rows,
    ROUND((COUNT(*) FILTER (WHERE ip.price_per_gram IS NULL))::numeric * 100 / NULLIF(COUNT(*), 0), 2) AS price_per_gram_null_pct
FROM public.ingredient_prices ip;
