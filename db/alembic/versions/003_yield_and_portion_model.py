"""Add canonical yield and portion model

Revision ID: 003
Revises: 002
Create Date: 2026-03-15

Adds recipe-level fields required to support dual yield authoring
(portion-first and weight-first) with deterministic display math.
"""

from alembic import op
import sqlalchemy as sa

revision = "003"
down_revision = "002"
branch_labels = None
depends_on = None


VALID_YIELD_MODE = "yield_mode IN ('count', 'weight')"


def upgrade() -> None:
    op.add_column(
        "recipes",
        sa.Column(
            "yield_mode",
            sa.String(20),
            nullable=False,
            server_default=sa.text("'count'"),
        ),
    )
    op.add_column("recipes", sa.Column("portion_size_grams", sa.Numeric, nullable=True))
    op.add_column("recipes", sa.Column("total_raw_weight_grams", sa.Numeric, nullable=True))
    op.add_column("recipes", sa.Column("total_cooked_weight_grams", sa.Numeric, nullable=True))
    op.add_column("recipes", sa.Column("portions_count_resolved", sa.Numeric, nullable=True))

    op.create_check_constraint("valid_yield_mode", "recipes", VALID_YIELD_MODE)
    op.create_check_constraint(
        "positive_portion_size_grams",
        "recipes",
        "portion_size_grams IS NULL OR portion_size_grams > 0",
    )
    op.create_check_constraint(
        "positive_total_raw_weight_grams",
        "recipes",
        "total_raw_weight_grams IS NULL OR total_raw_weight_grams >= 0",
    )
    op.create_check_constraint(
        "positive_total_cooked_weight_grams",
        "recipes",
        "total_cooked_weight_grams IS NULL OR total_cooked_weight_grams >= 0",
    )
    op.create_check_constraint(
        "positive_portions_count_resolved",
        "recipes",
        "portions_count_resolved IS NULL OR portions_count_resolved > 0",
    )
    op.create_check_constraint(
        "weight_mode_requires_portion_size_when_active",
        "recipes",
        "status <> 'active' OR yield_mode <> 'weight' OR (portion_size_grams IS NOT NULL AND portion_size_grams > 0)",
    )

    op.create_index("idx_recipes_yield_mode", "recipes", ["yield_mode"])


def downgrade() -> None:
    op.drop_index("idx_recipes_yield_mode", table_name="recipes")

    op.drop_constraint("positive_portions_count_resolved", "recipes", type_="check")
    op.drop_constraint("weight_mode_requires_portion_size_when_active", "recipes", type_="check")
    op.drop_constraint("positive_total_cooked_weight_grams", "recipes", type_="check")
    op.drop_constraint("positive_total_raw_weight_grams", "recipes", type_="check")
    op.drop_constraint("positive_portion_size_grams", "recipes", type_="check")
    op.drop_constraint("valid_yield_mode", "recipes", type_="check")

    op.drop_column("recipes", "portions_count_resolved")
    op.drop_column("recipes", "total_cooked_weight_grams")
    op.drop_column("recipes", "total_raw_weight_grams")
    op.drop_column("recipes", "portion_size_grams")
    op.drop_column("recipes", "yield_mode")
