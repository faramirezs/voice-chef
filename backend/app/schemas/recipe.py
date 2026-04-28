from sqlmodel import SQLModel, Field
from typing import List
from uuid import UUID
from decimal import Decimal
from datetime import datetime
from pydantic import field_validator

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

    quantity: str
    unit: str
    quantity_grams: str

    preparation: str | None = None
    sort_order: int


class RecipeSummaryResponse(SQLModel):
    id: UUID
    name: str
    description: str | None
    instructions: str | None
    status: str
    yield_mode: str
    portion_size_grams: str | None
    total_raw_weight_grams: str | None
    total_cooked_weight_grams: str | None
    portions_count_resolved: str | None
    photo_url: str | None
    created_at: datetime | None
    updated_at: datetime | None

class RecipeDetailResponse(RecipeSummaryResponse):
    preparation_time_minutes: int | None
    cooking_time_minutes: int | None
    is_component: bool
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
    yield_mode: str | None = None

    portion_size_grams: Decimal | None = Field(default=None, gt=0)
    portions_count_resolved: Decimal | None = Field(default=None, gt=0)
    total_raw_weight_grams: Decimal | None = Field(default=None, ge=0)
    total_cooked_weight_grams: Decimal | None = Field(default=None, ge=0)

    @field_validator("name")
    @classmethod
    def name_must_not_be_empty(cls, v: str | None):
        if v is not None:
            v = v.strip()
            if not v:
                raise ValueError("Recipe name cannot be empty")
        return v

    # ingredients: List[RecipeIngredientUpdate] | None = None
