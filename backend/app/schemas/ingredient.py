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
    default_unit: Optional[str]
    ingredient_type: Optional[str]
    bls_key: Optional[str]
    is_custom: bool
    has_parent: bool
    parent_id: Optional[UUID]
    created_at: Optional[datetime]
    updated_at: Optional[datetime]