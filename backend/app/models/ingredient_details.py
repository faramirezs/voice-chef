from typing import TYPE_CHECKING
from uuid import UUID
from sqlmodel import (
    Field, SQLModel, Relationship,
)
from sqlalchemy import (
    CheckConstraint, UniqueConstraint, PrimaryKeyConstraint, ForeignKeyConstraint, 
    Index, Column, Uuid, String, Integer, Numeric, text, DateTime
)
from datetime import datetime
from decimal import Decimal

if TYPE_CHECKING:
    from app.models.ingredient import Ingredient


# ─── ORM SQLMOdel model for additives ─────────────────────────────────────────────────
# Food additives are substances added to food to preserve flavor or enhance 
# taste, appearance, or other sensory qualities. 

class Additives(SQLModel, table=True):
    __tablename__ = "additives"
    __table_args__ = (
        PrimaryKeyConstraint('id', name='additives_pkey'),
        UniqueConstraint('code', name='additives_code_key')
    )
    # Primary key, Timestamps
    id: UUID = Field(default=None, primary_key=True, sa_column_kwargs={"server_default": text("gen_random_uuid()")})
    code: int = Field(
        sa_column=Column('code', Integer, nullable=False))
    
    # Core fields
    name_de: str = Field(
        sa_column=Column('name_de', String(255), nullable=False))
    name_en: str | None = Field(
        default=None, sa_column=Column('name_en', String(255)))

    # Relationship attributes
    ingredient: list['Ingredient'] = Relationship(
        back_populates='additive', 
        sa_relationship_kwargs={'secondary': 'ingredient_additives'}
    )


# ─── ORM SQLMOdel model for allergens ─────────────────────────────────────────────────

class Allergens(SQLModel, table=True):
    __table_args__ = (
        PrimaryKeyConstraint('id', name='allergens_pkey'),
        UniqueConstraint('code', name='allergens_code_key')
    )
    # Primary key, Timestamps
    id: UUID = Field(default=None, primary_key=True, sa_column_kwargs={"server_default": text("gen_random_uuid()")})
    code: int = Field(
        sa_column=Column('code', Integer, nullable=False))
    
    # Core fields
    name_de: str = Field(
        sa_column=Column('name_de', String(255), nullable=False))
    name_en: str | None = Field(
        default=None, sa_column=Column('name_en', String(255)))
    parent_code: int | None = Field(
        default=None, sa_column=Column('parent_code', Integer))
    
    # Relationship attributes
    ingredient: list['Ingredient'] = Relationship(
        back_populates='allergen', 
        sa_relationship_kwargs={'secondary': 'ingredient_allergens'})


class IngredientPrices(SQLModel, table=True):
    __tablename__ = 'ingredient_prices'
    __table_args__ = (
        CheckConstraint('price_per_gram IS NULL OR price_per_gram > 0::numeric', name='ingredient_prices_price_per_gram_positive'),
        CheckConstraint('price_per_unit > 0::numeric', name='positive_price'),
        ForeignKeyConstraint(['ingredient_id'], ['ingredients.id'], ondelete='CASCADE', name='ingredient_prices_ingredient_id_fkey'),
        PrimaryKeyConstraint('id', name='ingredient_prices_pkey'),
        Index('idx_ingredient_prices_ing', 'ingredient_id'),
        Index('idx_ingredient_prices_latest_lookup', 'ingredient_id', 'unit', text('updated_at DESC'), text('created_at DESC'), text('id DESC')),
        Index('uq_ingredient_no_supplier', 'ingredient_id', postgresql_where='(supplier_id IS NULL)', unique=True),
        Index('uq_ingredient_supplier', 'ingredient_id', 'supplier_id', postgresql_where='(supplier_id IS NOT NULL)', unique=True)
    )

    id: UUID = Field(default=None, primary_key=True, sa_column_kwargs={"server_default": text("gen_random_uuid()")})
    currency: str = Field(sa_column=Column('currency', String(10), nullable=False, server_default=text("'EUR'::character varying")))
    created_at: datetime = Field(sa_column=Column('created_at', DateTime(True), nullable=False, server_default=text('now()')))
    updated_at: datetime = Field(sa_column=Column('updated_at', DateTime(True), nullable=False, server_default=text('now()')))
    price_per_unit: Decimal | None = Field(default=None, sa_column=Column('price_per_unit', Numeric(10, 4)))
    unit: str | None = Field(default=None, sa_column=Column('unit', String(50)))
    supplier_name: str | None = Field(default=None, sa_column=Column('supplier_name', String(255)))
    supplier_id: str | None = Field(default=None, sa_column=Column('supplier_id', String(100)))
    article_number: str | None = Field(default=None, sa_column=Column('article_number', String(100)))
    price_per_gram: Decimal | None = Field(default=None, sa_column=Column('price_per_gram', Numeric(14, 8)))
    
    # Foreign keys
    ingredient_id: UUID = Field(nullable=False)
    # Relationship attributes
    ingredient: 'Ingredient' = Relationship(back_populates='ingredient_prices')
