from datetime import datetime
from decimal import Decimal
from uuid import UUID
from typing import Optional, TYPE_CHECKING

from sqlmodel import SQLModel, Field, Relationship
from sqlalchemy import (
    CheckConstraint, ForeignKeyConstraint, PrimaryKeyConstraint, UniqueConstraint,
    Index, Boolean, Column, DateTime, Integer, Numeric, String, text,
)

if TYPE_CHECKING:
    from app.models.recipe import Recipe
    from app.models.ingredient import Ingredient


# ─── ORM SQLMOdel model for recipe_ingredients ─────────────────────────────────────────────────

class RecipeIngredient(SQLModel, table=True):
    __tablename__ = "recipe_ingredients"
    __table_args__ = (
        CheckConstraint('quantity_grams IS NULL OR quantity_grams >= 0::numeric', name='recipe_ingredients_quantity_grams_non_negative'),
        CheckConstraint('num_nonnulls(ingredient_id, sub_recipe_id) = 1', name='recipe_ingredients_exactly_one_item'),
        ForeignKeyConstraint(['ingredient_id'], ['ingredients.id'], ondelete='CASCADE', name='recipe_ingredients_ingredient_id_fkey'),
        ForeignKeyConstraint(['recipe_id'], ['recipes.id'], ondelete='CASCADE', name='recipe_ingredients_recipe_id_fkey'),
        ForeignKeyConstraint(['sub_recipe_id'], ['recipes.id'], ondelete='CASCADE', name='recipe_ingredients_sub_recipe_id_fkey'),
        PrimaryKeyConstraint('id', name='recipe_ingredients_pkey'),
        UniqueConstraint('recipe_id', 'ingredient_id', 'sort_order', name='uq_recipe_ingredient_order'),
        Index('idx_recipe_ingredients_ingredient', 'ingredient_id'),
        Index('idx_recipe_ingredients_recipe', 'recipe_id'),
        Index('idx_recipe_ingredients_sub_recipe', 'sub_recipe_id'),
    )

    # Primary key, Timestamps
    id: UUID = Field(default=None, primary_key=True, sa_column_kwargs={"server_default": text("gen_random_uuid()")})
    created_at: datetime = Field(sa_column=Column('created_at', DateTime(True), nullable=False, server_default=text('now()')))

    # Core fields
    quantity: Decimal | None = Field(default=None)
    quantity_grams: Decimal | None = Field(default=None)
    quid_percent: Decimal | None = Field(default=None)
    sort_order: int = Field(sa_column=Column('sort_order', Integer, nullable=False, server_default=text('0')))
    unit: str | None = Field(default=None, max_length=50)
    preparation: str | None = Field(default=None, max_length=255)
    item_type: str | None = Field(default=None, max_length=50)
    is_organic: bool | None = Field(default=None, sa_column_kwargs={"server_default": text("false")})

    # Foreign keys
    recipe_id: UUID = Field(nullable=False)
    ingredient_id: UUID | None = Field(default=None, nullable=True)
    sub_recipe_id: UUID | None = Field(default=None, nullable=True)

    # Relationship attributes
    ingredient: Optional["Ingredient"] = Relationship(back_populates="recipe_ingredients")
    recipe: "Recipe" = Relationship(back_populates="recipe_ingredients", sa_relationship_kwargs={'foreign_keys': '[RecipeIngredient.recipe_id]'})
    sub_recipe: Optional["Recipe"] = Relationship(sa_relationship_kwargs={'foreign_keys': '[RecipeIngredient.sub_recipe_id]'})
