from typing import Optional, TYPE_CHECKING
import datetime
from datetime import datetime
from decimal import Decimal
from uuid import UUID

from sqlalchemy import (
    Boolean, CheckConstraint, Column, DateTime, ForeignKeyConstraint, Index, 
    Integer, Numeric, PrimaryKeyConstraint, String, Text, text
)
from sqlmodel import Field, Relationship, SQLModel


if TYPE_CHECKING:
    from app.models.users import Users, Tenants
    from app.models.recipe_ingredients import RecipeIngredient
    from app.models.recipe_versions import RecipeVersions
    from app.models.categories import Categories, Tag


# ─── ORM SQLMOdel model for recipes ─────────────────────────────────────────────────

class Recipe(SQLModel, table=True):
    __tablename__ = 'recipes'
    __table_args__ = (
        CheckConstraint("status IN ('draft', 'active', 'archived')", name='valid_status'),
        CheckConstraint('portion_size_grams IS NULL OR portion_size_grams > 0::numeric', name='positive_portion_size_grams'),
        CheckConstraint('portions_count_resolved IS NULL OR portions_count_resolved > 0::numeric', name='positive_portions_count_resolved'),
        CheckConstraint("status::text <> 'active'::text OR yield_mode::text <> 'weight'::text OR portion_size_grams IS NOT NULL AND portion_size_grams > 0::numeric", name='weight_mode_requires_portion_size_when_active'),
        CheckConstraint('total_cooked_weight_grams IS NULL OR total_cooked_weight_grams >= 0::numeric', name='positive_total_cooked_weight_grams'),
        CheckConstraint('total_raw_weight_grams IS NULL OR total_raw_weight_grams >= 0::numeric', name='positive_total_raw_weight_grams'),
        CheckConstraint("yield_mode::text = ANY (ARRAY['count', 'weight']::text[])", name='valid_yield_mode'),
        ForeignKeyConstraint(['created_by'], ['users.id'], name='recipes_created_by_fkey'),
        ForeignKeyConstraint(['tenant_id'], ['tenants.id'], name='recipes_tenant_id_fkey'),
        PrimaryKeyConstraint('id', name='recipes_pkey'),
        Index('idx_recipes_component', 'tenant_id', 'is_component'),
        Index('idx_recipes_name', 'name'),
        Index('idx_recipes_status', 'tenant_id', 'status'),
        Index('idx_recipes_tenant', 'tenant_id'),
        Index('idx_recipes_yield_mode', 'yield_mode'),
    )

    id: UUID = Field(default=None, primary_key=True, sa_column_kwargs={"server_default": text("gen_random_uuid()")})
    name: str = Field(max_length=255, nullable=False)
    description: str | None = Field(default=None, sa_type=Text)
    yield_amount: Decimal | None = Field(default=None)
    yield_unit: str | None = Field(default=None, max_length=50)
    instructions: str | None = Field(default=None, sa_type=Text)
    reduction_factor: Decimal | None = Field(default=None, sa_column=Column('reduction_factor', Numeric, server_default=text('1.0')))
    status: str = Field(max_length=50, sa_column_kwargs={"server_default": text("'draft'")}, nullable=False)
    is_component: bool = Field(nullable=False, sa_column_kwargs={"server_default": text("false")})
    recipe_number: str | None = Field(default=None, max_length=100)
    preparation_time_minutes: int | None = Field(default=None, nullable=True)
    cooking_time_minutes: int | None = Field(default=None, nullable=True)
    shelf_life_text: str | None = Field(default=None, sa_type=Text)
    storage_temperature: str | None = Field(default=None, max_length=50)
    notes: str | None = Field(default=None, sa_type=Text)
    photo_url: str | None = Field(default=None, sa_type=Text)
    yield_mode: str = Field(max_length=20, nullable=False, sa_column_kwargs={"server_default": text("'count'")})
    portion_size_grams: Decimal | None = Field(default=None)
    total_raw_weight_grams: Decimal | None = Field(default=None)
    total_cooked_weight_grams: Decimal | None = Field(default=None)
    portions_count_resolved: Decimal | None = Field(default=None)
    created_at: datetime = Field(sa_column=Column('created_at', DateTime(True), nullable=False, server_default=text('now()')))
    updated_at: datetime = Field(sa_column=Column('updated_at', DateTime(True), nullable=False, server_default=text('now()')))

    # Foreign keys
    tenant_id: UUID = Field(nullable=False)
    created_by: UUID | None = Field(default=None)
    # Relationship attributes
    category: list['Categories'] = Relationship(back_populates='recipe', sa_relationship_kwargs={'secondary': 'recipe_categories'})
    created_by_user: Optional['Users'] = Relationship(back_populates='recipes')
    tenant: 'Tenants' = Relationship(back_populates='recipes')
    tag: list['Tag'] = Relationship(back_populates='recipe', sa_relationship_kwargs={'secondary': 'recipe_tags'})
    recipe_ingredients: list['RecipeIngredient'] = Relationship(back_populates='recipe', sa_relationship_kwargs={'foreign_keys': '[RecipeIngredient.recipe_id]', 'passive_deletes': True})
    recipe_versions: list['RecipeVersions'] = Relationship(back_populates='recipe')


# ─── ORM SQLMOdel model for recipe_nutrition_cache ─────────────────────────────────────────────────

# NOTE: mpeshko. In this table, `recipe_id` serves a dual purpose: it is both 
# a primary key and a foreign key.
class RecipeNutritionCache(SQLModel, table=True):
    __tablename__ = 'recipe_nutrition_cache'
    __table_args__ = (
        ForeignKeyConstraint(['recipe_id'], ['recipes.id'], ondelete='CASCADE', name='recipe_nutrition_cache_recipe_id_fkey'),
        PrimaryKeyConstraint('recipe_id', name='recipe_nutrition_cache_pkey')
    )

    # Foreign keys, Primary key,  Timestamps
    # NOTE: mpeshko. In DB, this column is marked as NOT NULL and has no default value, 
    # which means that PostgreSQL expects you to provide the ID when creating the record.
    recipe_id: UUID = Field(primary_key=True, nullable=False)
    updated_at: datetime = Field(sa_column=Column('updated_at', DateTime(True), nullable=False, server_default=text('now()')))
    
    # Core fields
    energy_kj: Decimal | None = Field(default=None)
    energy_kcal: Decimal | None = Field(default=None)
    fat: Decimal | None = Field(default=None)
    saturates: Decimal | None = Field(default=None)
    carbs: Decimal | None = Field(default=None)
    sugars: Decimal | None = Field(default=None)
    protein: Decimal | None = Field(default=None)
    salt: Decimal | None = Field(default=None)
    fiber: Decimal | None = Field(default=None)
