"""Seed piece-unit defaults and backfill price_per_gram

Revision ID: 006
Revises: 005
Create Date: 2026-03-17

Applies deterministic ingredient-specific piece conversions for currently
unresolved rows and computes price_per_gram using those conversions.
"""

from alembic import op

revision = "006"
down_revision = "005"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute(
        """
        INSERT INTO public.ingredient_units (ingredient_id, unit_code, grams_per_unit, label)
        VALUES
            ('f603175a-a720-5841-bd3b-8bb4b58f84f6', 'stck', 500,  'Balsamicoessig 1 Stck in g'),
            ('1c0510ee-6447-5f10-b7ca-e52644b9de08', 'stck', 1200, 'Blumenkohl 1 Stck in g'),
            ('f662257f-5e60-5eb9-896a-bef62d61d485', 'stck', 58,   'Eier 1 Stck in g'),
            ('a8af4063-5b26-5389-9dad-f266ae5e4333', 'stck', 350,  'Gurke 1 Stck in g'),
            ('34754ab5-53f2-594c-a99e-a952f92bead0', 'stk', 80,    'rote zwiebel 1 Stk in g'),
            ('d690bf27-7a51-5ac2-b801-198058bd835d', 'stck', 8,    'Vanillezucker 1 Stck in g'),
            ('3fd1ffda-3064-5c51-8a40-9bffda6fd925', 'stck', 750,   'Weisswein trocken 1 Stck in g')
        ON CONFLICT (ingredient_id, unit_code)
        DO UPDATE SET
            grams_per_unit = EXCLUDED.grams_per_unit,
            label = EXCLUDED.label;
        """
    )

    op.execute(
        """
        UPDATE public.ingredient_prices ip
        SET price_per_gram = ip.price_per_unit / iu.grams_per_unit
        FROM public.ingredient_units iu
        WHERE ip.price_per_gram IS NULL
          AND ip.price_per_unit IS NOT NULL
          AND iu.grams_per_unit > 0
          AND ip.ingredient_id = iu.ingredient_id
          AND LOWER(TRIM(COALESCE(ip.unit, ''))) = LOWER(TRIM(COALESCE(iu.unit_code, '')));
        """
    )


def downgrade() -> None:
    # Intentional no-op: data migration should not drop historical conversions/prices.
    pass
