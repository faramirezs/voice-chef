from datetime import date
from decimal import Decimal
from uuid import UUID, uuid4
from typing import List, Optional, TYPE_CHECKING
from sqlmodel import Field, SQLModel, Relationship
from sqlalchemy import Index, Integer, Column, text, Boolean, DateTime, Numeric

if TYPE_CHECKING:
    from app.models.recipe import Recipe
    from app.models.users import Users, Tenants
    from app.models.recipe_ingredients import RecipeIngredient


class Ingredient(SQLModel, table=True):
    __tablename__ = "ingredients"
    __table_args__ = (
        Index("ix_ingredients_name", "name"),
        Index("idx_ingredients_parent_id", "parent_id"),
        Index("idx_ingredients_usage_count", "usage_count"),
    )

    # Primary key, Core fields, Timestamps
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    name: str = Field(max_length=255)
    created_at: date | None = Field(default=None, sa_column=Column(DateTime(timezone=True), nullable=False, server_default=text("now()")))
    updated_at: date | None = Field(default=None, sa_column=Column(DateTime(timezone=True), nullable=False, server_default=text("now()"), onupdate=text("now()")))

    # Varying character fields
    default_unit: str | None = Field(max_length=50)
    ingredient_type: str | None = Field(max_length=50)
    bls_key: str | None = Field(max_length=100)

    # Integers
    usage_count: int | None = Field(default=0, sa_column=Column(Integer, server_default=text("0")))
    recipe_count: int | None = Field(default=0, sa_column=Column(Integer, server_default=text("0")))

    # Booleans
    is_custom: bool = Field(default=False, sa_column=Column(Boolean, server_default=text("false")))
    has_parent: bool = Field(default=False, sa_column=Column(Boolean, server_default=text("false")))

    # Foreign keys
    tenant_id: UUID | None = Field(default=None, foreign_key="tenants.id") 
    parent_id: UUID | None = Field(default=None, foreign_key="ingredients.id")

    # Optional foreign keys (for future relationships)    
    nutrition_id: UUID | None = None
    initial_recipe_id: UUID | None = None

    # Relationship attributes
    parent: Optional['Ingredient'] = Relationship(back_populates='children', sa_relationship_kwargs={"remote_side": "Ingredient.id"})
    children: List['Ingredient'] = Relationship(back_populates='parent')
    tenant: Optional['Tenants'] = Relationship(back_populates='ingredients')
    # ingredient_nutrition: Optional['IngredientNutrition'] = Relationship(sa_relationship_kwargs={'uselist': False}, back_populates='ingredient')
    # ingredient_prices: List['IngredientPrices'] = Relationship(back_populates='ingredient')
    recipe_ingredients: List['RecipeIngredient'] = Relationship(back_populates='ingredient')





class NutritionFacts(SQLModel, table=True):
    __tablename__ = "nutrition_facts"

    id: UUID = Field(default_factory=uuid4, primary_key=True)

    energy_kj: Decimal | None = Field(sa_column=Column(Numeric))    
    energy_kcal: Decimal | None = Field(sa_column=Column(Numeric))
    fat: Decimal | None = Field(sa_column=Column(Numeric))
    saturates: Decimal | None = Field(sa_column=Column(Numeric))
    carbs: Decimal | None = Field(sa_column=Column(Numeric))
    sugars: Decimal | None = Field(sa_column=Column(Numeric))
    protein: Decimal | None = Field(sa_column=Column(Numeric))
    salt: Decimal | None = Field(sa_column=Column(Numeric))

    # recipe_nutrition: List['RecipeNutrition'] = Relationship(back_populates='nutrition')