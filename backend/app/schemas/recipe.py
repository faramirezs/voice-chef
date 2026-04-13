
from sqlmodel import SQLModel, Field, SQLModel, Relationship
from typing import Optional, List
from uuid import UUID, uuid4
from decimal import Decimal
from datetime import datetime

# class RecipeWrite(SQLModel):
#     name: str
#     description: Optional[str] = None
#     instructions: Optional[str] = None

# class RecipeRead(SQLModel):
#     id: UUID = Field(default_factory=uuid4, primary_key=True)
#     name: str = Field(max_length=255)
#     # description: Optional[str] = None
#     # instructions: Optional[str] = None

# class RecipeUpdate(SQLModel):
#     name: str | None = None
#     description: str | None = None
#     instructions: str | None = None


class RecipeIngredientWrite(SQLModel):
    ingredient_id: UUID
    quantity: Decimal
    unit: str
    preparation: Optional[str] = None
    sort_order: int


class RecipeWrite(SQLModel):
    name: str
    description: Optional[str] = None
    instructions: Optional[str] = None

    status: str = "draft"
    yield_mode: str = "count"

    portion_size_grams: Optional[Decimal] = None
    total_raw_weight_grams: Optional[Decimal] = None
    total_cooked_weight_grams: Optional[Decimal] = None

    portions_count_resolved: Optional[Decimal] = None

    # ingredients: List[RecipeIngredientWrite] = []


class RecipeIngredientResponse(SQLModel):
    id: UUID
    ingredient_id: UUID
    ingredient_name: str
    ingredient_default_unit: str

    quantity: Decimal
    unit: str
    quantity_grams: Decimal

    preparation: Optional[str] = None
    sort_order: int


class RecipeSummaryResponse(SQLModel):
    id: UUID
    name: str
    description: Optional[str]
    instructions: Optional[str]

    status: str
    yield_mode: str

    portion_size_grams: Optional[Decimal]
    total_raw_weight_grams: Optional[Decimal]
    total_cooked_weight_grams: Optional[Decimal]

    portions_count_resolved: Optional[Decimal]

    created_at: Optional[datetime]
    updated_at: Optional[datetime]


class RecipeDetailResponse(RecipeSummaryResponse):
    ingredients: List[RecipeIngredientResponse]


class RecipeIngredientUpdate(SQLModel):
    ingredient_id: Optional[UUID] = None
    quantity: Optional[Decimal] = None
    unit: Optional[str] = None
    preparation: Optional[str] = None
    sort_order: Optional[int] = None


class RecipeUpdate(SQLModel):
    name: Optional[str] = None
    description: Optional[str] = None
    instructions: Optional[str] = None

    status: Optional[str] = None
    yield_mode: Optional[str] = "count"

    portion_size_grams: Optional[Decimal] = None
    total_raw_weight_grams: Optional[Decimal] = None
    total_cooked_weight_grams: Optional[Decimal] = None

    portions_count_resolved: Optional[Decimal] = None

    # ingredients: Optional[List[RecipeIngredientUpdate]] = None



