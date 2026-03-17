\echo '=== Dry-run duplicate merge report (case-insensitive exact-name duplicates) ==='
\echo 'No data is modified. This report recommends keep/drop ids and estimates conflict risk.'

WITH ingredient_stats AS (
    SELECT
        i.id,
        i.name,
        lower(i.name) AS normalized_name,
        i.bls_key,
        i.updated_at,
        EXISTS (
            SELECT 1
            FROM public.ingredient_nutrition n
            WHERE n.ingredient_id = i.id
        ) AS has_nutrition,
        COALESCE((
            SELECT COUNT(*)
            FROM public.recipe_ingredients ri
            WHERE ri.ingredient_id = i.id
        ), 0) AS recipe_refs,
        COALESCE((
            SELECT COUNT(*)
            FROM public.ingredient_prices ip
            WHERE ip.ingredient_id = i.id
        ), 0) AS price_rows,
        COALESCE((
            SELECT COUNT(*)
            FROM public.ingredient_units iu
            WHERE iu.ingredient_id = i.id
        ), 0) AS unit_rows,
        COALESCE((
            SELECT COUNT(*)
            FROM public.ingredients c
            WHERE c.parent_id = i.id
        ), 0) AS child_rows,
        COALESCE((
            SELECT
                (CASE WHEN COALESCE(n.energy_kj, 0) <> 0 THEN 1 ELSE 0 END) +
                (CASE WHEN COALESCE(n.energy_kcal, 0) <> 0 THEN 1 ELSE 0 END) +
                (CASE WHEN COALESCE(n.carbs, 0) <> 0 THEN 1 ELSE 0 END) +
                (CASE WHEN COALESCE(n.protein, 0) <> 0 THEN 1 ELSE 0 END) +
                (CASE WHEN COALESCE(n.fat, 0) <> 0 THEN 1 ELSE 0 END) +
                (CASE WHEN COALESCE(n.sugars, 0) <> 0 THEN 1 ELSE 0 END) +
                (CASE WHEN COALESCE(n.fiber, 0) <> 0 THEN 1 ELSE 0 END) +
                (CASE WHEN COALESCE(n.saturates, 0) <> 0 THEN 1 ELSE 0 END) +
                (CASE WHEN COALESCE(n.salt, 0) <> 0 THEN 1 ELSE 0 END) +
                (CASE WHEN COALESCE(n.alcohol, 0) <> 0 THEN 1 ELSE 0 END) +
                (CASE WHEN COALESCE(n.water, 0) <> 0 THEN 1 ELSE 0 END)
            FROM public.ingredient_nutrition n
            WHERE n.ingredient_id = i.id
            LIMIT 1
        ), 0) AS nutrition_nonzero_fields
    FROM public.ingredients i
),
duplicates AS (
    SELECT normalized_name, COUNT(*) AS group_size
    FROM ingredient_stats
    GROUP BY normalized_name
    HAVING COUNT(*) > 1
),
ranked AS (
    SELECT
        s.*,
        d.group_size,
        ROW_NUMBER() OVER (
            PARTITION BY s.normalized_name
            ORDER BY
                s.recipe_refs DESC,
                s.price_rows DESC,
                (s.bls_key IS NOT NULL) DESC,
                s.nutrition_nonzero_fields DESC,
                s.unit_rows DESC,
                s.updated_at DESC NULLS LAST,
                s.id
        ) AS rn
    FROM ingredient_stats s
    JOIN duplicates d ON d.normalized_name = s.normalized_name
),
keepers AS (
    SELECT normalized_name, group_size, id AS keep_id, name AS keep_name,
           recipe_refs AS keep_recipe_refs,
           price_rows AS keep_price_rows,
           unit_rows AS keep_unit_rows,
           child_rows AS keep_child_rows,
           has_nutrition AS keep_has_nutrition,
           (bls_key IS NOT NULL) AS keep_has_bls,
           nutrition_nonzero_fields AS keep_nutrition_nonzero_fields
    FROM ranked
    WHERE rn = 1
),
pairs AS (
    SELECT
        k.normalized_name,
        k.group_size,
        k.keep_id,
        k.keep_name,
        k.keep_recipe_refs,
        k.keep_price_rows,
        k.keep_unit_rows,
        k.keep_child_rows,
        k.keep_has_nutrition,
        k.keep_has_bls,
        k.keep_nutrition_nonzero_fields,
        r.id AS drop_id,
        r.name AS drop_name,
        r.recipe_refs AS drop_recipe_refs,
        r.price_rows AS drop_price_rows,
        r.unit_rows AS drop_unit_rows,
        r.child_rows AS drop_child_rows,
        r.has_nutrition AS drop_has_nutrition,
        (r.bls_key IS NOT NULL) AS drop_has_bls,
        r.nutrition_nonzero_fields AS drop_nutrition_nonzero_fields
    FROM keepers k
    JOIN ranked r
      ON r.normalized_name = k.normalized_name
     AND r.rn > 1
),
conflicts AS (
    SELECT
        p.*,
        COALESCE((
            SELECT COUNT(*)
            FROM public.ingredient_prices dp
            JOIN public.ingredient_prices kp
              ON kp.ingredient_id = p.keep_id
             AND dp.ingredient_id = p.drop_id
             AND dp.supplier_id IS NOT DISTINCT FROM kp.supplier_id
        ), 0) AS price_conflicts,
        COALESCE((
            SELECT COUNT(*)
            FROM public.recipe_ingredients dr
            JOIN public.recipe_ingredients kr
              ON kr.ingredient_id = p.keep_id
             AND dr.ingredient_id = p.drop_id
             AND dr.recipe_id = kr.recipe_id
             AND dr.sort_order = kr.sort_order
        ), 0) AS recipe_conflicts,
        COALESCE((
            SELECT COUNT(*)
            FROM public.ingredient_units du
            JOIN public.ingredient_units ku
              ON ku.ingredient_id = p.keep_id
             AND du.ingredient_id = p.drop_id
             AND du.unit_code = ku.unit_code
        ), 0) AS unit_conflicts
    FROM pairs p
),
scored AS (
    SELECT
        c.*,
        (
            c.drop_recipe_refs * 10 +
            c.drop_price_rows * 6 +
            c.drop_unit_rows * 3 +
            c.drop_child_rows * 2 +
            (CASE WHEN c.drop_has_nutrition THEN 2 ELSE 0 END) +
            (CASE WHEN c.drop_has_bls THEN 2 ELSE 0 END)
        ) AS impact_score,
        (
            c.price_conflicts * 10 +
            c.recipe_conflicts * 8 +
            c.unit_conflicts * 6 +
            (CASE WHEN c.keep_has_nutrition AND c.drop_has_nutrition THEN 4 ELSE 0 END) +
            (CASE WHEN c.group_size > 2 THEN 2 ELSE 0 END)
        ) AS risk_score
    FROM conflicts c
)
SELECT
    ROW_NUMBER() OVER (
        ORDER BY impact_score DESC, risk_score DESC, normalized_name, drop_name, drop_id
    ) AS rank,
    normalized_name,
    group_size,
    keep_id,
    keep_name,
    drop_id,
    drop_name,
    keep_recipe_refs,
    drop_recipe_refs,
    keep_price_rows,
    drop_price_rows,
    keep_has_bls,
    drop_has_bls,
    keep_has_nutrition,
    drop_has_nutrition,
    keep_nutrition_nonzero_fields,
    drop_nutrition_nonzero_fields,
    price_conflicts,
    recipe_conflicts,
    unit_conflicts,
    impact_score,
    risk_score,
    CASE
        WHEN risk_score >= 20 THEN 'high'
        WHEN risk_score >= 8 THEN 'medium'
        ELSE 'low'
    END AS risk_level
FROM scored
ORDER BY impact_score DESC, risk_score DESC, normalized_name, drop_name, drop_id;
