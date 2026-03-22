"""Add grams-canonical unit system

Revision ID: 002
Revises: 001
Create Date: 2026-03-15

Adds:
- units reference table (global unit definitions with gram conversion factors)
- ingredient_units table (ingredient-specific unit overrides, e.g. 1 egg = 58g)
- quantity_grams column on recipe_ingredients (canonical weight for all math)
- price_per_gram column on ingredient_prices (derived, enables trivial cost calc)
- quantity_grams column on shopping_list_items (enables aggregation across recipes)
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID

revision = "002"
down_revision = "001"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ------------------------------------------------------------------ #
    #  1. units — global unit reference table                              #
    # ------------------------------------------------------------------ #
    op.create_table(
        "units",
        sa.Column("id", UUID, primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("code", sa.String(20), nullable=False, unique=True),
        sa.Column("name_de", sa.String(100), nullable=False),
        sa.Column("name_en", sa.String(100), nullable=True),
        sa.Column("grams_per_unit", sa.Numeric, nullable=True),
        sa.Column("unit_type", sa.String(20), nullable=False),
        sa.Column("is_base", sa.Boolean, nullable=False, server_default=sa.text("false")),
        sa.CheckConstraint(
            "unit_type IN ('weight', 'volume', 'piece', 'custom')",
            name="valid_unit_type",
        ),
    )

    # ------------------------------------------------------------------ #
    #  2. ingredient_units — per-ingredient unit overrides                 #
    # ------------------------------------------------------------------ #
    op.create_table(
        "ingredient_units",
        sa.Column("id", UUID, primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column(
            "ingredient_id",
            UUID,
            sa.ForeignKey("ingredients.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("unit_code", sa.String(20), nullable=False),
        sa.Column("grams_per_unit", sa.Numeric, nullable=False),
        sa.Column("label", sa.String(100), nullable=True),
        sa.UniqueConstraint("ingredient_id", "unit_code", name="uq_ingredient_unit"),
    )

    op.create_index(
        "idx_ingredient_units_ingredient", "ingredient_units", ["ingredient_id"]
    )

    # ------------------------------------------------------------------ #
    #  3. recipe_ingredients — add canonical grams column                  #
    # ------------------------------------------------------------------ #
    op.add_column(
        "recipe_ingredients",
        sa.Column("quantity_grams", sa.Numeric, nullable=True),
    )

    # ------------------------------------------------------------------ #
    #  4. ingredient_prices — add derived price-per-gram                   #
    # ------------------------------------------------------------------ #
    op.add_column(
        "ingredient_prices",
        sa.Column("price_per_gram", sa.Numeric(14, 8), nullable=True),
    )

    # ------------------------------------------------------------------ #
    #  5. shopping_list_items — add canonical grams column                 #
    # ------------------------------------------------------------------ #
    op.add_column(
        "shopping_list_items",
        sa.Column("quantity_grams", sa.Numeric, nullable=True),
    )


def downgrade() -> None:
    op.drop_column("shopping_list_items", "quantity_grams")
    op.drop_column("ingredient_prices", "price_per_gram")
    op.drop_column("recipe_ingredients", "quantity_grams")
    op.drop_index("idx_ingredient_units_ingredient", table_name="ingredient_units")
    op.drop_table("ingredient_units")
    op.drop_table("units")
