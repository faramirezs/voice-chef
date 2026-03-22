"""Bulk-merge case-insensitive exact-name duplicate ingredients

Revision ID: 008
Revises: 007
Create Date: 2026-03-17

This migration merges all duplicate rows where lower(name) matches exactly.
It rewires FK references, resolves uniqueness collisions, merges nutrition data,
and deletes duplicate ingredient rows while preserving canonical metadata.
"""

from alembic import op

revision = "008"
down_revision = "007"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute(
        """
        CREATE TABLE IF NOT EXISTS public.ingredient_merge_audit (
            id bigserial PRIMARY KEY,
            merged_at timestamptz NOT NULL DEFAULT NOW(),
            normalized_name text NOT NULL,
            keep_id uuid NOT NULL,
            drop_id uuid NOT NULL,
            table_name text NOT NULL,
            row_data jsonb NOT NULL
        );
        """
    )

    op.execute(
        """
        DO $$
        DECLARE
            pair RECORD;
            keep_nutrition_id uuid;
            drop_nutrition_id uuid;
        BEGIN
            FOR pair IN
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
                    SELECT normalized_name
                    FROM ingredient_stats
                    GROUP BY normalized_name
                    HAVING COUNT(*) > 1
                ),
                ranked AS (
                    SELECT
                        s.*,
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
                    SELECT normalized_name, id AS keep_id
                    FROM ranked
                    WHERE rn = 1
                )
                SELECT
                    k.normalized_name,
                    k.keep_id,
                    r.id AS drop_id
                FROM keepers k
                JOIN ranked r
                  ON r.normalized_name = k.normalized_name
                 AND r.rn > 1
                ORDER BY k.normalized_name, r.rn
            LOOP
                IF pair.keep_id = pair.drop_id THEN
                    CONTINUE;
                END IF;

                IF NOT EXISTS (SELECT 1 FROM public.ingredients WHERE id = pair.keep_id)
                   OR NOT EXISTS (SELECT 1 FROM public.ingredients WHERE id = pair.drop_id) THEN
                    CONTINUE;
                END IF;

                -- Snapshot full pre-merge rows for traceability and rollback support.
                INSERT INTO public.ingredient_merge_audit (normalized_name, keep_id, drop_id, table_name, row_data)
                SELECT pair.normalized_name, pair.keep_id, pair.drop_id, 'ingredients', to_jsonb(i)
                FROM public.ingredients i
                WHERE i.id IN (pair.keep_id, pair.drop_id);

                INSERT INTO public.ingredient_merge_audit (normalized_name, keep_id, drop_id, table_name, row_data)
                SELECT pair.normalized_name, pair.keep_id, pair.drop_id, 'ingredient_prices', to_jsonb(ip)
                FROM public.ingredient_prices ip
                WHERE ip.ingredient_id IN (pair.keep_id, pair.drop_id);

                INSERT INTO public.ingredient_merge_audit (normalized_name, keep_id, drop_id, table_name, row_data)
                SELECT pair.normalized_name, pair.keep_id, pair.drop_id, 'ingredient_units', to_jsonb(iu)
                FROM public.ingredient_units iu
                WHERE iu.ingredient_id IN (pair.keep_id, pair.drop_id);

                INSERT INTO public.ingredient_merge_audit (normalized_name, keep_id, drop_id, table_name, row_data)
                SELECT pair.normalized_name, pair.keep_id, pair.drop_id, 'ingredient_nutrition', to_jsonb(n)
                FROM public.ingredient_nutrition n
                WHERE n.ingredient_id IN (pair.keep_id, pair.drop_id);

                INSERT INTO public.ingredient_merge_audit (normalized_name, keep_id, drop_id, table_name, row_data)
                SELECT pair.normalized_name, pair.keep_id, pair.drop_id, 'recipe_ingredients', to_jsonb(ri)
                FROM public.recipe_ingredients ri
                WHERE ri.ingredient_id IN (pair.keep_id, pair.drop_id);

                UPDATE public.ingredients keep_i
                SET
                    bls_key = COALESCE(keep_i.bls_key, drop_i.bls_key),
                    default_unit = COALESCE(keep_i.default_unit, drop_i.default_unit),
                    ingredient_type = COALESCE(keep_i.ingredient_type, drop_i.ingredient_type),
                    nutrition_id = COALESCE(keep_i.nutrition_id, drop_i.nutrition_id),
                    is_custom = COALESCE(keep_i.is_custom, drop_i.is_custom),
                    has_parent = COALESCE(keep_i.has_parent, drop_i.has_parent),
                    parent_id = CASE
                        WHEN keep_i.parent_id IS NOT NULL THEN keep_i.parent_id
                        WHEN drop_i.parent_id IS NOT NULL AND drop_i.parent_id <> pair.drop_id THEN drop_i.parent_id
                        ELSE keep_i.parent_id
                    END,
                    initial_recipe_id = COALESCE(keep_i.initial_recipe_id, drop_i.initial_recipe_id),
                    tenant_id = COALESCE(keep_i.tenant_id, drop_i.tenant_id),
                    usage_count = GREATEST(COALESCE(keep_i.usage_count, 0), COALESCE(drop_i.usage_count, 0)),
                    recipe_count = GREATEST(COALESCE(keep_i.recipe_count, 0), COALESCE(drop_i.recipe_count, 0)),
                    updated_at = NOW()
                FROM public.ingredients drop_i
                WHERE keep_i.id = pair.keep_id
                  AND drop_i.id = pair.drop_id;

                UPDATE public.ingredients
                SET parent_id = pair.keep_id,
                    updated_at = NOW()
                WHERE parent_id = pair.drop_id;

                                -- Preserve all unit rows: if a unit_code collides after merge,
                                -- suffix the duplicate unit_code so the row is retained.
                                UPDATE public.ingredient_units du
                                SET
                                        unit_code = CONCAT(du.unit_code, '__dup_', SUBSTRING(pair.drop_id::text, 1, 6)),
                                        label = CONCAT(COALESCE(du.label, ''), ' [merged duplicate]')
                                FROM public.ingredient_units ku
                                WHERE du.ingredient_id = pair.drop_id
                                    AND ku.ingredient_id = pair.keep_id
                                    AND du.unit_code = ku.unit_code;

                UPDATE public.ingredient_units
                SET ingredient_id = pair.keep_id
                WHERE ingredient_id = pair.drop_id;

                                -- Preserve all price rows: avoid unique collisions on
                                -- (ingredient_id, supplier_id) by re-keying conflicting supplier_id.
                                UPDATE public.ingredient_prices dp
                                SET
                                        supplier_id = CONCAT(dp.supplier_id, '__dup__', SUBSTRING(pair.drop_id::text, 1, 8)),
                                        supplier_name = COALESCE(dp.supplier_name, '[merged duplicate supplier]'),
                                        updated_at = NOW()
                                FROM public.ingredient_prices kp
                                WHERE dp.ingredient_id = pair.drop_id
                                    AND kp.ingredient_id = pair.keep_id
                                    AND dp.supplier_id IS NOT NULL
                                    AND dp.supplier_id = kp.supplier_id;

                UPDATE public.ingredient_prices
                SET ingredient_id = pair.keep_id,
                    updated_at = NOW()
                WHERE ingredient_id = pair.drop_id;

                                -- Preserve all recipe ingredient rows. If merge would violate
                                -- (recipe_id, ingredient_id, sort_order), move the drop-side
                                -- row to the next available sort_order in that recipe.
                                UPDATE public.recipe_ingredients dr
                                SET
                                    sort_order = (
                                        SELECT COALESCE(MAX(r2.sort_order), 0) + 1
                                        FROM public.recipe_ingredients r2
                                        WHERE r2.recipe_id = dr.recipe_id
                                    ),
                                    updated_at = NOW()
                                FROM public.recipe_ingredients kr
                                WHERE dr.ingredient_id = pair.drop_id
                                  AND kr.ingredient_id = pair.keep_id
                                  AND dr.recipe_id = kr.recipe_id
                                  AND dr.sort_order = kr.sort_order;

                UPDATE public.recipe_ingredients
                SET ingredient_id = pair.keep_id,
                    updated_at = NOW()
                WHERE ingredient_id = pair.drop_id;

                SELECT id INTO keep_nutrition_id
                FROM public.ingredient_nutrition
                WHERE ingredient_id = pair.keep_id;

                SELECT id INTO drop_nutrition_id
                FROM public.ingredient_nutrition
                WHERE ingredient_id = pair.drop_id;

                IF keep_nutrition_id IS NULL AND drop_nutrition_id IS NOT NULL THEN
                    UPDATE public.ingredient_nutrition
                    SET ingredient_id = pair.keep_id,
                        updated_at = NOW()
                    WHERE id = drop_nutrition_id;
                ELSIF keep_nutrition_id IS NOT NULL AND drop_nutrition_id IS NOT NULL THEN
                    UPDATE public.ingredient_nutrition k
                    SET
                        energy_kj = CASE WHEN COALESCE(k.energy_kj, 0) = 0 THEN d.energy_kj ELSE k.energy_kj END,
                        energy_kcal = CASE WHEN COALESCE(k.energy_kcal, 0) = 0 THEN d.energy_kcal ELSE k.energy_kcal END,
                        carbs = CASE WHEN COALESCE(k.carbs, 0) = 0 THEN d.carbs ELSE k.carbs END,
                        protein = CASE WHEN COALESCE(k.protein, 0) = 0 THEN d.protein ELSE k.protein END,
                        fat = CASE WHEN COALESCE(k.fat, 0) = 0 THEN d.fat ELSE k.fat END,
                        sugars = CASE WHEN COALESCE(k.sugars, 0) = 0 THEN d.sugars ELSE k.sugars END,
                        fiber = CASE WHEN COALESCE(k.fiber, 0) = 0 THEN d.fiber ELSE k.fiber END,
                        saturates = CASE WHEN COALESCE(k.saturates, 0) = 0 THEN d.saturates ELSE k.saturates END,
                        salt = CASE WHEN COALESCE(k.salt, 0) = 0 THEN d.salt ELSE k.salt END,
                        alcohol = CASE WHEN COALESCE(k.alcohol, 0) = 0 THEN d.alcohol ELSE k.alcohol END,
                        water = CASE WHEN COALESCE(k.water, 0) = 0 THEN d.water ELSE k.water END,
                        updated_at = NOW()
                    FROM public.ingredient_nutrition d
                    WHERE k.id = keep_nutrition_id
                      AND d.id = drop_nutrition_id;

                    UPDATE public.ingredients
                    SET nutrition_id = keep_nutrition_id,
                        updated_at = NOW()
                    WHERE nutrition_id = drop_nutrition_id
                       OR id = pair.keep_id;

                    DELETE FROM public.ingredient_nutrition
                    WHERE id = drop_nutrition_id;
                END IF;

                DELETE FROM public.ingredients
                WHERE id = pair.drop_id;
            END LOOP;
        END
        $$;
        """
    )


def downgrade() -> None:
    # No safe automatic split possible after bulk merge.
    pass
