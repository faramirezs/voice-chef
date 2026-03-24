"""Drop user-approved legacy fields and merge audit table

Revision ID: 011
Revises: 010
Create Date: 2026-03-19

Drops:
- public.ingredient_merge_audit and related sequence
- selected legacy columns on public.recipes

This migration only applies the exact drop scope approved by the user.
"""

from alembic import op

revision = "011"
down_revision = "010"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute(
        """
        ALTER TABLE public.recipes
            DROP COLUMN IF EXISTS branch_ids,
            DROP COLUMN IF EXISTS preference_price,
            DROP COLUMN IF EXISTS ingredient_list_product_pass,
            DROP COLUMN IF EXISTS preference_allergens,
            DROP COLUMN IF EXISTS layout_id,
            DROP COLUMN IF EXISTS row_height,
            DROP COLUMN IF EXISTS rezeptblatt_image_width,
            DROP COLUMN IF EXISTS vat_rate,
            DROP COLUMN IF EXISTS sales_price_points,
            DROP COLUMN IF EXISTS bio_label_eu;
        """
    )

    op.execute("DROP TABLE IF EXISTS public.ingredient_merge_audit;")
    op.execute("DROP SEQUENCE IF EXISTS public.ingredient_merge_audit_id_seq;")


def downgrade() -> None:
    op.execute(
        """
        ALTER TABLE public.recipes
            ADD COLUMN IF NOT EXISTS branch_ids text,
            ADD COLUMN IF NOT EXISTS preference_price numeric(10,2),
            ADD COLUMN IF NOT EXISTS ingredient_list_product_pass text,
            ADD COLUMN IF NOT EXISTS preference_allergens text,
            ADD COLUMN IF NOT EXISTS layout_id character varying(50),
            ADD COLUMN IF NOT EXISTS row_height integer,
            ADD COLUMN IF NOT EXISTS rezeptblatt_image_width integer,
            ADD COLUMN IF NOT EXISTS vat_rate numeric(5,2),
            ADD COLUMN IF NOT EXISTS sales_price_points numeric(10,2),
            ADD COLUMN IF NOT EXISTS bio_label_eu boolean;
        """
    )

    op.execute(
        """
        CREATE TABLE IF NOT EXISTS public.ingredient_merge_audit (
            id bigint NOT NULL,
            merged_at timestamp with time zone DEFAULT now() NOT NULL,
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
        CREATE SEQUENCE IF NOT EXISTS public.ingredient_merge_audit_id_seq
            START WITH 1
            INCREMENT BY 1
            NO MINVALUE
            NO MAXVALUE
            CACHE 1;
        """
    )

    op.execute(
        """
        ALTER SEQUENCE public.ingredient_merge_audit_id_seq
        OWNED BY public.ingredient_merge_audit.id;
        """
    )

    op.execute(
        """
        ALTER TABLE ONLY public.ingredient_merge_audit
        ALTER COLUMN id SET DEFAULT nextval('public.ingredient_merge_audit_id_seq'::regclass);
        """
    )

    op.execute(
        """
        DO $$
        BEGIN
            IF NOT EXISTS (
                SELECT 1
                FROM pg_constraint
                WHERE conname = 'ingredient_merge_audit_pkey'
                  AND conrelid = 'public.ingredient_merge_audit'::regclass
            ) THEN
                ALTER TABLE ONLY public.ingredient_merge_audit
                ADD CONSTRAINT ingredient_merge_audit_pkey PRIMARY KEY (id);
            END IF;
        END
        $$;
        """
    )
