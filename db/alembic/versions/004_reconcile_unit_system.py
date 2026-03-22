"""Reconcile canonical unit system artifacts on legacy databases

Revision ID: 004
Revises: 003
Create Date: 2026-03-16

This migration is intentionally idempotent and focuses on ensuring that the
002 canonical unit-system objects exist on databases that were bootstrapped
from legacy dumps.
"""

from alembic import op

revision = "004"
down_revision = "003"
branch_labels = None
depends_on = None


def _create_check_if_missing(constraint_name: str, table_name: str, check_sql: str) -> None:
    op.execute(
        f"""
        DO $$
        BEGIN
            IF NOT EXISTS (
                SELECT 1
                FROM pg_constraint
                WHERE conname = '{constraint_name}'
                  AND conrelid = 'public.{table_name}'::regclass
            ) THEN
                ALTER TABLE public.{table_name}
                ADD CONSTRAINT {constraint_name}
                CHECK ({check_sql});
            END IF;
        END $$;
        """
    )


def _add_column_if_table_exists(table_name: str, add_column_sql: str) -> None:
    op.execute(
        f"""
        DO $$
        BEGIN
            IF EXISTS (
                SELECT 1
                FROM information_schema.tables
                WHERE table_schema = 'public'
                  AND table_name = '{table_name}'
            ) THEN
                ALTER TABLE public.{table_name}
                ADD COLUMN IF NOT EXISTS {add_column_sql};
            END IF;
        END $$;
        """
    )


def upgrade() -> None:
    op.execute('CREATE EXTENSION IF NOT EXISTS "pgcrypto"')

    op.execute(
        """
        CREATE TABLE IF NOT EXISTS public.units (
            id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
            code varchar(20) NOT NULL UNIQUE,
            name_de varchar(100) NOT NULL,
            name_en varchar(100),
            grams_per_unit numeric,
            unit_type varchar(20) NOT NULL,
            is_base boolean NOT NULL DEFAULT false,
            CONSTRAINT valid_unit_type CHECK (unit_type IN ('weight', 'volume', 'piece', 'custom'))
        );
        """
    )

    op.execute(
        """
        CREATE TABLE IF NOT EXISTS public.ingredient_units (
            id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
            ingredient_id uuid NOT NULL,
            unit_code varchar(20) NOT NULL,
            grams_per_unit numeric NOT NULL,
            label varchar(100),
            CONSTRAINT ingredient_units_ingredient_id_fkey
                FOREIGN KEY (ingredient_id) REFERENCES public.ingredients(id) ON DELETE CASCADE,
            CONSTRAINT uq_ingredient_unit UNIQUE (ingredient_id, unit_code)
        );
        """
    )

    op.execute(
        """
        CREATE INDEX IF NOT EXISTS idx_ingredient_units_ingredient
        ON public.ingredient_units (ingredient_id);
        """
    )

    _add_column_if_table_exists("recipe_ingredients", "quantity_grams numeric")
    _add_column_if_table_exists("ingredient_prices", "price_per_gram numeric(14, 8)")
    _add_column_if_table_exists("shopping_list_items", "quantity_grams numeric")

    _create_check_if_missing(
        constraint_name="ingredient_units_grams_per_unit_positive",
        table_name="ingredient_units",
        check_sql="grams_per_unit > 0",
    )

    _create_check_if_missing(
        constraint_name="recipe_ingredients_quantity_grams_non_negative",
        table_name="recipe_ingredients",
        check_sql="quantity_grams IS NULL OR quantity_grams >= 0",
    )

    _create_check_if_missing(
        constraint_name="ingredient_prices_price_per_gram_positive",
        table_name="ingredient_prices",
        check_sql="price_per_gram IS NULL OR price_per_gram > 0",
    )

    op.execute(
        """
        DO $$
        BEGIN
            IF EXISTS (
                SELECT 1
                FROM information_schema.tables
                WHERE table_schema = 'public'
                  AND table_name = 'shopping_list_items'
            ) THEN
                IF NOT EXISTS (
                    SELECT 1
                    FROM pg_constraint
                    WHERE conname = 'shopping_list_items_quantity_grams_non_negative'
                      AND conrelid = 'public.shopping_list_items'::regclass
                ) THEN
                    ALTER TABLE public.shopping_list_items
                    ADD CONSTRAINT shopping_list_items_quantity_grams_non_negative
                    CHECK (quantity_grams IS NULL OR quantity_grams >= 0);
                END IF;
            END IF;
        END $$;
        """
    )

    op.execute(
        """
        INSERT INTO public.units (code, name_de, name_en, grams_per_unit, unit_type, is_base)
        VALUES
            ('g', 'Gramm', 'gram', 1, 'weight', true),
            ('kg', 'Kilogramm', 'kilogram', 1000, 'weight', false),
            ('mg', 'Milligramm', 'milligram', 0.001, 'weight', false),
            ('l', 'Liter', 'liter', NULL, 'volume', false),
            ('ml', 'Milliliter', 'milliliter', NULL, 'volume', false),
            ('pc', 'Stueck', 'piece', NULL, 'piece', false)
        ON CONFLICT (code) DO NOTHING;
        """
    )


def downgrade() -> None:
    # Reconciliation migration is intentionally non-destructive and not auto-reverted.
    pass
