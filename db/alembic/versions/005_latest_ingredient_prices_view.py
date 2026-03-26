"""Create canonical latest ingredient price view

Revision ID: 005
Revises: 004
Create Date: 2026-03-17

Ensures queries can always select exactly one latest row per
(ingredient_id, unit) key while preserving historical prices.
"""

from alembic import op

revision = "005"
down_revision = "004"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute(
        """
        CREATE INDEX IF NOT EXISTS idx_ingredient_prices_latest_lookup
        ON public.ingredient_prices
        (ingredient_id, unit, updated_at DESC, created_at DESC, id DESC);
        """
    )

    op.execute(
        """
        CREATE OR REPLACE VIEW public.ingredient_prices_latest AS
        SELECT DISTINCT ON (ip.ingredient_id, COALESCE(ip.unit, ''))
            ip.id,
            ip.ingredient_id,
            ip.price_per_unit,
            ip.price_per_gram,
            ip.currency,
            ip.unit,
            ip.supplier_name,
            ip.supplier_id,
            ip.article_number,
            ip.created_at,
            ip.updated_at
        FROM public.ingredient_prices ip
        ORDER BY
            ip.ingredient_id,
            COALESCE(ip.unit, ''),
            ip.updated_at DESC NULLS LAST,
            ip.created_at DESC NULLS LAST,
            ip.id DESC;
        """
    )


def downgrade() -> None:
    op.execute("DROP VIEW IF EXISTS public.ingredient_prices_latest;")
    op.execute("DROP INDEX IF EXISTS public.idx_ingredient_prices_latest_lookup;")
