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
    Numeric,
    PrimaryKeyConstraint,
    String,
    UniqueConstraint,
    Uuid,
    text,
)

if TYPE_CHECKING:
    from app.models.tmp_draft import (
        Additives,
        Allergens,
        IngredientPrices,
        IngredientUnits,
    )
    from app.models.recipe_ingredients import RecipeIngredient
    from app.models.users import Tenants


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
    id: UUID = Field(sa_column=Column('id', Uuid, primary_key=True, server_default=text('gen_random_uuid()')))
    name: str = Field(sa_column=Column('name', String(255), nullable=False))
    created_at: datetime = Field(sa_column=Column('created_at', DateTime(True), nullable=False, server_default=text('now()')))
    updated_at: datetime = Field(sa_column=Column('updated_at', DateTime(True), nullable=False, server_default=text('now()')))

    # Varying character fields
    source: str = Field(sa_column=Column('source', String(50), nullable=False, server_default=text("'standard'::character varying")))
    name_english: str | None = Field(default=None, sa_column=Column('name_english', String(255)))
    bls_key: str | None = Field(default=None, sa_column=Column('bls_key', String(50)))
    default_unit: str | None = Field(default=None, sa_column=Column('default_unit', String(50)))

    # Booleans
    is_custom: bool = Field(sa_column=Column('is_custom', Boolean, nullable=False, server_default=text('false')))

    # Foreign keys
    tenant_id: UUID | None = Field(default=None, sa_column=Column('tenant_id', Uuid))
    parent_id: UUID | None = Field(default=None, sa_column=Column('parent_id', Uuid))

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





class NutritionFacts(SQLModel, table=True):
    __tablename__ = "ingredient_nutrition"
    __table_args__ = (
        ForeignKeyConstraint(['ingredient_id'], ['ingredients.id'], ondelete='CASCADE', name='ingredient_nutrition_ingredient_id_fkey'),
        PrimaryKeyConstraint('id', name='ingredient_nutrition_pkey'),
        UniqueConstraint('ingredient_id', name='ingredient_nutrition_ingredient_id_key')
    )

    # Primary key, Core fields, Timestamps
    id: UUID = Field(sa_column=Column('id', Uuid, primary_key=True, server_default=text('gen_random_uuid()')))
    ingredient_id: UUID = Field(sa_column=Column('ingredient_id', Uuid, nullable=False))
    created_at: datetime = Field(sa_column=Column('created_at', DateTime(True), nullable=False, server_default=text('now()')))
    updated_at: datetime = Field(sa_column=Column('updated_at', DateTime(True), nullable=False, server_default=text('now()')))

    # Decimal nutrition fields
    energy_kj: Decimal | None = Field(sa_column=Column(Numeric))
    energy_kcal: Decimal | None = Field(sa_column=Column(Numeric))
    fat: Decimal | None = Field(sa_column=Column(Numeric))
    saturates: Decimal | None = Field(sa_column=Column(Numeric))
    carbs: Decimal | None = Field(sa_column=Column(Numeric))
    sugars: Decimal | None = Field(sa_column=Column(Numeric))
    protein: Decimal | None = Field(sa_column=Column(Numeric))
    fiber: Decimal | None = Field(sa_column=Column(Numeric))
    salt: Decimal | None = Field(sa_column=Column(Numeric))
    alcohol: Decimal | None = Field(sa_column=Column(Numeric))
    water: Decimal | None = Field(sa_column=Column(Numeric))

    # Relationship attributes
    ingredient: 'Ingredient' = Relationship(back_populates='ingredient_nutrition')
