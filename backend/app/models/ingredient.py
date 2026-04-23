from datetime import datetime
from decimal import Decimal
from uuid import UUID
from typing import TYPE_CHECKING
from sqlmodel import Field, SQLModel, Relationship
from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    ForeignKeyConstraint,
    Index,
    PrimaryKeyConstraint,
    String,
    UniqueConstraint,
    text,
)

if TYPE_CHECKING:
    from app.models.units import IngredientUnits
    from app.models.recipe_ingredients import RecipeIngredient
    from app.models.users import Tenants
    from app.models.ingredient_details import Additives, Allergens, IngredientPrices


# ─── ORM SQLMOdel model for ingredients ─────────────────────────────────────────────────

class Ingredient(SQLModel, table=True):
    __tablename__ = "ingredients"
    __table_args__ = (
        ForeignKeyConstraint(['parent_id'], ['ingredients.id'], name='ingredients_parent_id_fkey'),
        ForeignKeyConstraint(['tenant_id'], ['tenants.id'], name='ingredients_tenant_id_fkey'),
        PrimaryKeyConstraint('id', name='ingredients_pkey'),
        Index('idx_ingredients_name', 'name'),
        Index('idx_ingredients_parent', 'parent_id'),
        Index('idx_ingredients_tenant', 'tenant_id')
    )

    # Primary key, Core fields, Timestamps
    id: UUID = Field(default=None, primary_key=True, sa_column_kwargs={"server_default": text("gen_random_uuid()")})
    name: str = Field(max_length=255, nullable=False)
    created_at: datetime = Field(sa_column=Column('created_at', DateTime(True), nullable=False, server_default=text('now()')))
    updated_at: datetime = Field(sa_column=Column('updated_at', DateTime(True), nullable=False, server_default=text('now()')))

    # Varying character fields
    source: str = Field(sa_column=Column('source', String(50), nullable=False, server_default=text("'standard'")))
    name_english: str | None = Field(default=None, max_length=255)
    bls_key: str | None = Field(default=None, max_length=50)
    default_unit: str | None = Field(default=None, max_length=50)

    # Booleans
    is_custom: bool = Field(nullable=False, sa_column_kwargs={"server_default": text("false")})

    # Foreign keys
    tenant_id: UUID | None = Field(default=None)
    parent_id: UUID | None = Field(default=None)

    # Relationship attributes
    additive: list['Additives'] = Relationship(back_populates='ingredient', sa_relationship_kwargs={'secondary': 'ingredient_additives'})
    allergen: list['Allergens'] = Relationship(back_populates='ingredient', sa_relationship_kwargs={'secondary': 'ingredient_allergens'})
    parent: 'Ingredient' = Relationship(back_populates='parent_reverse', sa_relationship_kwargs={'remote_side': '[Ingredient.id]'})
    parent_reverse: list['Ingredient'] = Relationship(back_populates='parent', sa_relationship_kwargs={'remote_side': '[Ingredient.parent_id]'})
    tenant: 'Tenants' = Relationship(back_populates='ingredients')
    ingredient_nutrition: 'NutritionFacts' = Relationship(back_populates='ingredient', sa_relationship_kwargs={'uselist': False})
    ingredient_prices: list['IngredientPrices'] = Relationship(back_populates='ingredient')
    ingredient_units: list['IngredientUnits'] = Relationship(back_populates='ingredient')
    recipe_ingredients: list['RecipeIngredient'] = Relationship(back_populates='ingredient')


# Backward-compatible alias for older imports that still use plural naming.
Ingredients = Ingredient



# ─── ORM SQLMOdel model for ingredient_nutrition ─────────────────────────────────────────────────

class NutritionFacts(SQLModel, table=True):
    __tablename__ = "ingredient_nutrition"
    __table_args__ = (
        ForeignKeyConstraint(['ingredient_id'], ['ingredients.id'], ondelete='CASCADE', name='ingredient_nutrition_ingredient_id_fkey'),
        PrimaryKeyConstraint('id', name='ingredient_nutrition_pkey'),
        UniqueConstraint('ingredient_id', name='ingredient_nutrition_ingredient_id_key')
    )

    # Primary key, Core fields, Timestamps
    id: UUID = Field(default=None, primary_key=True, sa_column_kwargs={"server_default": text("gen_random_uuid()")})
    created_at: datetime = Field(sa_column=Column('created_at', DateTime(True), nullable=False, server_default=text('now()')))
    updated_at: datetime = Field(sa_column=Column('updated_at', DateTime(True), nullable=False, server_default=text('now()')))

    # Decimal nutrition fields
    energy_kj: Decimal | None = Field(default=None)
    energy_kcal: Decimal | None = Field(default=None)
    fat: Decimal | None = Field(default=None)
    saturates: Decimal | None = Field(default=None)
    carbs: Decimal | None = Field(default=None)
    sugars: Decimal | None = Field(default=None)
    protein: Decimal | None = Field(default=None)
    fiber: Decimal | None = Field(default=None)
    salt: Decimal | None = Field(default=None)
    alcohol: Decimal | None = Field(default=None)
    water: Decimal | None = Field(default=None)

    # Foreign keys
    ingredient_id: UUID = Field(nullable=False)

    # Relationship attributes
    ingredient: 'Ingredient' = Relationship(back_populates='ingredient_nutrition')
