from uuid import UUID
from sqlmodel import SQLModel, Field


class IngredientWrite(SQLModel):
    name: str = Field(max_length=255)
    default_unit: str | None = Field(default=None, max_length=50)
    ingredient_type: str | None = Field(default=None, max_length=50)
    bls_key: str | None = Field(default=None, max_length=100)
    is_custom: bool = False
    parent_id: UUID | None = None


