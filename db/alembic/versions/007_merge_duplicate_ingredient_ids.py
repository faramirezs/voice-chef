"""Merge duplicate ingredient ids for core costing ingredients

Revision ID: 007
Revises: 006
Create Date: 2026-03-17

Merges case-only duplicate ingredient rows for:
- knoblauch
- olivenoel
- tomatenmark

Goals:
- preserve existing recipe links
- move historical prices to canonical ingredient ids
- preserve and merge nutrition data
- preserve BLS key and related metadata
"""

from alembic import op

revision = "007"
down_revision = "006"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute(
        """
        DO $$
        DECLARE
            pair RECORD;
            keep_nutrition_id uuid;
            drop_nutrition_id uuid;
        BEGIN
            FOR pair IN
                SELECT *
                FROM (VALUES
                    ('5adfcc26-f8b0-5f48-8191-b118ea08f87d'::uuid, '8737599e-60dc-598d-a0c1-d161fe5a2fff'::uuid), -- knoblauch
                    ('957a285e-889a-5f8e-9fcc-b73bfd7304ea'::uuid, 'e5c2f101-08e1-5730-a66c-c0b60cb4c87c'::uuid), -- olivenoel
                    ('c4174230-c859-5c6e-8d91-0d1dd2081aef'::uuid, 'af2dea1e-d399-58c4-9b7f-c0f3be7934b4'::uuid)  -- tomatenmark
                ) AS t(keep_id, drop_id)
            LOOP
                IF NOT EXISTS (SELECT 1 FROM public.ingredients WHERE id = pair.keep_id)
                   OR NOT EXISTS (SELECT 1 FROM public.ingredients WHERE id = pair.drop_id) THEN
                    CONTINUE;
                END IF;

                -- Preserve non-null metadata on canonical row.
                UPDATE public.ingredients keep_i
                SET
                    bls_key = COALESCE(keep_i.bls_key, drop_i.bls_key),
                    default_unit = COALESCE(keep_i.default_unit, drop_i.default_unit),
                    ingredient_type = COALESCE(keep_i.ingredient_type, drop_i.ingredient_type),
                    is_custom = COALESCE(keep_i.is_custom, drop_i.is_custom),
                    has_parent = COALESCE(keep_i.has_parent, drop_i.has_parent),
                    initial_recipe_id = COALESCE(keep_i.initial_recipe_id, drop_i.initial_recipe_id),
                    tenant_id = COALESCE(keep_i.tenant_id, drop_i.tenant_id),
                    usage_count = GREATEST(COALESCE(keep_i.usage_count, 0), COALESCE(drop_i.usage_count, 0)),
                    recipe_count = GREATEST(COALESCE(keep_i.recipe_count, 0), COALESCE(drop_i.recipe_count, 0)),
                    updated_at = NOW()
                FROM public.ingredients drop_i
                WHERE keep_i.id = pair.keep_id
                  AND drop_i.id = pair.drop_id;

                -- Rewire any ingredient hierarchy links.
                UPDATE public.ingredients
                SET parent_id = pair.keep_id,
                    updated_at = NOW()
                WHERE parent_id = pair.drop_id;

                -- Prevent unique conflicts before moving ingredient_units.
                DELETE FROM public.ingredient_units du
                USING public.ingredient_units ku
                WHERE du.ingredient_id = pair.drop_id
                  AND ku.ingredient_id = pair.keep_id
                  AND du.unit_code = ku.unit_code;

                UPDATE public.ingredient_units
                SET ingredient_id = pair.keep_id
                WHERE ingredient_id = pair.drop_id;

                -- Prevent unique conflicts before moving ingredient_prices.
                DELETE FROM public.ingredient_prices dp
                USING public.ingredient_prices kp
                WHERE dp.ingredient_id = pair.drop_id
                  AND kp.ingredient_id = pair.keep_id
                  AND dp.supplier_id IS NOT DISTINCT FROM kp.supplier_id;

                UPDATE public.ingredient_prices
                SET ingredient_id = pair.keep_id,
                    updated_at = NOW()
                WHERE ingredient_id = pair.drop_id;

                -- Prevent unique conflicts before moving recipe_ingredients.
                DELETE FROM public.recipe_ingredients dr
                USING public.recipe_ingredients kr
                WHERE dr.ingredient_id = pair.drop_id
                  AND kr.ingredient_id = pair.keep_id
                  AND dr.recipe_id = kr.recipe_id
                  AND dr.sort_order = kr.sort_order;

                UPDATE public.recipe_ingredients
                SET ingredient_id = pair.keep_id,
                    updated_at = NOW()
                WHERE ingredient_id = pair.drop_id;

                -- Merge nutrition rows (one row per ingredient_id).
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

                -- Remove duplicate ingredient row after all references are moved.
                DELETE FROM public.ingredients
                WHERE id = pair.drop_id;
            END LOOP;
        END
        $$;
        """
    )


def downgrade() -> None:
    # No safe automatic split possible after merge.
    pass
