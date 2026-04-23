from sqlmodel import SQLModel, Field, SQLModel, Relationship
from typing import Optional
from uuid import UUID
from decimal import Decimal
from datetime import datetime


class IngredientWrite(SQLModel):
    name: str = Field(max_length=255)
    default_unit: str | None = Field(default=None, max_length=50)
    ingredient_type: str | None = Field(default=None, max_length=50)
    bls_key: str | None = Field(default=None, max_length=100)
    is_custom: bool = False
    parent_id: UUID | None = None


class IngredientSummaryResponse(SQLModel):
    id: UUID
    name: str
    default_unit: str | None
    ingredient_type: str | None
    bls_key: str | None
    is_custom: bool
    has_parent: bool
    parent_id: UUID | None
    created_at: datetime | None
    updated_at: datetime | None
