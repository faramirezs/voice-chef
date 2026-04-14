from datetime import datetime
from decimal import Decimal
from uuid import UUID, uuid4
from typing import Optional, TYPE_CHECKING

from sqlmodel import SQLModel, Field, Relationship
from sqlalchemy import Column, DateTime, Integer, Numeric, text, UniqueConstraint, CheckConstraint, Index

if TYPE_CHECKING:
    from app.models.recipe import Recipe
    from app.models.ingredient import Ingredient


class RecipeIngredient(SQLModel, table=True):
    __tablename__ = "recipe_ingredients"
    __table_args__ = (
        # (indexes are already in DB; Alembic will detect if missing)
        Index("ix_recipe_ingredients_ingredient_id", "ingredient_id"),
        Index("ix_recipe_ingredients_recipe_id", "recipe_id"),
        Index("ix_recipe_ingredients_sort_order", "sort_order"),
        CheckConstraint("quantity_grams IS NULL OR quantity_grams >= 0", name="recipe_ingredients_quantity_grams_non_negative",),
        UniqueConstraint("recipe_id", "ingredient_id", "sort_order", name="uq_recipe_ingredient_order")
    )

    # Primary key, Timestamps
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    created_at: datetime | None = Field(default=None, sa_column=Column(DateTime(timezone=True), nullable=False, server_default=text("now()"),))
    updated_at: datetime | None = Field(default=None, sa_column=Column(DateTime(timezone=True), nullable=False, server_default=text("now()"), onupdate=text("now()")))

    # Core fields
    quantity: Decimal | None = Field(default=None, sa_column=Column(Numeric(10, 4)))
    quantity_grams: Decimal | None = Field(default=None, sa_column=Column(Numeric))
    quid: Decimal | None = Field(default=None, sa_column=Column(Numeric(10, 4)))
    sort_order: int = Field(default=0, sa_column=Column(Integer, nullable=False, server_default=text("0")))
    unit: str | None = Field(default=None, max_length=50)
    preparation: str | None = Field(default=None, max_length=255)
    item_type: str | None = Field(default=None, max_length=50)

    # Foreign keys
    recipe_id: UUID = Field(foreign_key="recipes.id", ondelete="CASCADE", nullable=False)
    ingredient_id: UUID = Field(foreign_key="ingredients.id", ondelete="CASCADE", nullable=False)

    # Relationship attributes
    recipe: Optional["Recipe"] = Relationship(back_populates="recipe_ingredients")
    ingredient: Optional["Ingredient"] = Relationship(back_populates="recipe_ingredients")