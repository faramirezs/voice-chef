from sqlmodel import SQLModel
from typing import List
from uuid import UUID
from decimal import Decimal
from datetime import datetime

class RecipeIngredientWrite(SQLModel):
    ingredient_id: UUID
    quantity: Decimal
    unit: str
    preparation: str | None = None
    sort_order: int


class RecipeWrite(SQLModel):
    name: str
    description: str | None = None
    instructions: str | None = None

    status: str = "draft"
    yield_mode: str = "count"

    portion_size_grams: Decimal | None = None
    total_raw_weight_grams: Decimal | None = None
    total_cooked_weight_grams: Decimal | None = None

    portions_count_resolved: Decimal | None = None

    # ingredients: List[RecipeIngredientWrite] = []


class RecipeIngredientResponse(SQLModel):
    id: UUID
    ingredient_id: UUID
    ingredient_name: str
    ingredient_default_unit: str

    quantity: Decimal
    unit: str
    quantity_grams: Decimal

    preparation: str | None = None
    sort_order: int


class RecipeSummaryResponse(SQLModel):
    id: UUID
    name: str
    description: str | None
    instructions: str | None
    status: str
    yield_mode: str
    portion_size_grams: Decimal | None
    total_raw_weight_grams: Decimal | None
    total_cooked_weight_grams: Decimal | None
    portions_count_resolved: Decimal | None
    created_at: datetime | None
    updated_at: datetime | None

class RecipeDetailResponse(RecipeSummaryResponse):
    ingredients: List[RecipeIngredientResponse]


class RecipeIngredientUpdate(SQLModel):
    ingredient_id: UUID | None = None
    quantity: Decimal | None = None
    unit: str | None = None
    preparation: str | None = None
    sort_order: int | None = None


class RecipeUpdate(SQLModel):
    name: str | None = None
    description: str | None = None
    instructions: str | None = None

    status: str | None = None
    yield_mode: str | None = "count"

    portion_size_grams: Decimal | None = None
    total_raw_weight_grams: Decimal | None = None
    total_cooked_weight_grams: Decimal | None = None

    portions_count_resolved: Decimal | None = None

    # ingredients: List[RecipeIngredientUpdate] | None = None
