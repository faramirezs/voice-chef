from typing import TYPE_CHECKING
from sqlmodel import SQLModel, Field, Relationship
from sqlalchemy import (
    CheckConstraint, ForeignKeyConstraint, PrimaryKeyConstraint, UniqueConstraint,
    Index, Column, String, Uuid, text, 
)
from uuid import UUID
from decimal import Decimal

if TYPE_CHECKING:
    from app.models.ingredient import Ingredient


# ─── ORM SQLMOdel model for units ─────────────────────────────────────────────────

class Units(SQLModel, table=True):
    __table_args__ = (
        CheckConstraint("unit_type::text = ANY (ARRAY['weight'::character varying, 'volume'::character varying, 'piece'::character varying, 'custom'::character varying]::text[])", name='valid_unit_type'),
        PrimaryKeyConstraint('id', name='units_pkey'),
        UniqueConstraint('code', name='units_code_key')
    )

    id: UUID = Field(default=None, primary_key=True, sa_column_kwargs={"server_default": text("gen_random_uuid()")})
    code: str = Field(sa_column=Column('code', String(20), nullable=False))
    name_de: str = Field(sa_column=Column('name_de', String(100), nullable=False))
    unit_type: str = Field(sa_column=Column('unit_type', String(20), nullable=False))
    is_base: bool = Field(nullable=False, sa_column_kwargs={"server_default": text("false")})
    name_en: str | None = Field(default=None, sa_column=Column('name_en', String(100)))
    grams_per_unit: Decimal | None = Field(default=None)


# ─── ORM SQLMOdel model for ingredient_units ─────────────────────────────────────────────────

class IngredientUnits(SQLModel, table=True):
    __tablename__ = 'ingredient_units'
    __table_args__ = (
        CheckConstraint('grams_per_unit > 0::numeric', name='ingredient_units_grams_per_unit_positive'),
        ForeignKeyConstraint(['ingredient_id'], ['ingredients.id'], ondelete='CASCADE', name='ingredient_units_ingredient_id_fkey'),
        PrimaryKeyConstraint('id', name='ingredient_units_pkey'),
        UniqueConstraint('ingredient_id', 'unit_code', name='uq_ingredient_unit'),
        Index('idx_ingredient_units_ingredient', 'ingredient_id')
    )

    id: UUID = Field(
        default=None, 
        primary_key=True, 
        sa_column_kwargs={"server_default": text("gen_random_uuid()")}
    )
    ingredient_id: UUID = Field(sa_column=Column('ingredient_id', Uuid, nullable=False))
    unit_code: str = Field(sa_column=Column('unit_code', String(20), nullable=False))
    grams_per_unit: Decimal = Field(nullable=False)
    label: str | None = Field(default=None, sa_column=Column('label', String(100)))

    ingredient: 'Ingredient' = Relationship(back_populates='ingredient_units')