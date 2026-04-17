"""Add photo_url to recipes; add sub_recipe_id to recipe_ingredients

Revision ID: 013
Revises: 012
Create Date: 2026-04-11

Changes:
- recipes.photo_url (Text, nullable) — single URL for the recipe's primary photo
- recipe_ingredients.ingredient_id made nullable (was NOT NULL)
- recipe_ingredients.sub_recipe_id (UUID FK → recipes.id, nullable) — allows a
  recipe line-item to reference another recipe instead of a raw ingredient
- CHECK constraint enforces exactly one of (ingredient_id, sub_recipe_id) is set
"""

import sqlalchemy as sa
from alembic import op

revision = "013"
down_revision = "012"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # --- recipes: add photo_url ---
    op.add_column("recipes", sa.Column("photo_url", sa.Text(), nullable=True))

    # --- recipe_ingredients: make ingredient_id nullable ---
    op.alter_column(
        "recipe_ingredients",
        "ingredient_id",
        existing_type=sa.UUID(),
        nullable=True,
    )

    # --- recipe_ingredients: add sub_recipe_id ---
    op.add_column(
        "recipe_ingredients",
        sa.Column("sub_recipe_id", sa.UUID(), nullable=True),
    )

    op.create_foreign_key(
        "recipe_ingredients_sub_recipe_id_fkey",
        "recipe_ingredients",
        "recipes",
        ["sub_recipe_id"],
        ["id"],
        ondelete="CASCADE",
    )

    op.create_index(
        "idx_recipe_ingredients_sub_recipe",
        "recipe_ingredients",
        ["sub_recipe_id"],
    )

    # Exactly one of ingredient_id / sub_recipe_id must be non-null
    op.create_check_constraint(
        "recipe_ingredients_exactly_one_item",
        "recipe_ingredients",
        "num_nonnulls(ingredient_id, sub_recipe_id) = 1",
    )


def downgrade() -> None:
    op.drop_constraint(
        "recipe_ingredients_exactly_one_item",
        "recipe_ingredients",
        type_="check",
    )
    op.drop_index(
        "idx_recipe_ingredients_sub_recipe",
        table_name="recipe_ingredients",
    )
    op.drop_constraint(
        "recipe_ingredients_sub_recipe_id_fkey",
        "recipe_ingredients",
        type_="foreignkey",
    )
    op.drop_column("recipe_ingredients", "sub_recipe_id")
    op.alter_column(
        "recipe_ingredients",
        "ingredient_id",
        existing_type=sa.UUID(),
        nullable=False,
    )
    op.drop_column("recipes", "photo_url")
