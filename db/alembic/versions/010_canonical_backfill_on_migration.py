"""Apply canonical backfill during migrations

Revision ID: 010
Revises: 009
Create Date: 2026-03-17

Ensures canonical computed fields are backfilled as part of migration flow,
so fresh Docker starts that run `alembic upgrade head` do not require a manual
post-migration SQL script.
"""

from alembic import op

revision = "010"
down_revision = "009"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute(
        """
        INSERT INTO public.units (code, name_de, name_en, grams_per_unit, unit_type, is_base)
        VALUES
            ('stk', 'Stueck', 'piece', NULL, 'piece', false),
            ('stck', 'Stueck', 'piece', NULL, 'piece', false)
        ON CONFLICT (code) DO NOTHING;
        """
    )

    op.execute(
        """
        UPDATE public.recipe_ingredients ri
        SET quantity_grams = ri.quantity * u.grams_per_unit
        FROM public.units u
        WHERE ri.quantity_grams IS NULL
          AND ri.quantity IS NOT NULL
          AND u.grams_per_unit IS NOT NULL
          AND LOWER(TRIM(COALESCE(ri.unit, ''))) = LOWER(TRIM(u.code));
        """
    )

    op.execute(
        """
        UPDATE public.ingredient_prices ip
        SET price_per_gram = ip.price_per_unit / u.grams_per_unit
        FROM public.units u
        WHERE ip.price_per_gram IS NULL
          AND ip.price_per_unit IS NOT NULL
          AND u.grams_per_unit IS NOT NULL
          AND u.grams_per_unit > 0
          AND LOWER(TRIM(COALESCE(ip.unit, ''))) = LOWER(TRIM(u.code));
        """
    )

    op.execute(
        """
        WITH summed AS (
            SELECT
                ri.recipe_id,
                SUM(ri.quantity_grams) AS total_raw_weight_grams
            FROM public.recipe_ingredients ri
            WHERE ri.quantity_grams IS NOT NULL
            GROUP BY ri.recipe_id
        )
        UPDATE public.recipes r
        SET total_raw_weight_grams = s.total_raw_weight_grams
        FROM summed s
        WHERE r.id = s.recipe_id
          AND r.total_raw_weight_grams IS NULL;
        """
    )

    op.execute(
        """
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
          );
        """
    )


def downgrade() -> None:
    # Intentional no-op: this migration backfills canonical data in-place.
    pass
