from sqlmodel import SQLModel, Field
from typing import List
from uuid import UUID
from decimal import Decimal
from datetime import datetime
from pydantic import field_validator
from fastapi import Query
from enum import Enum


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

    portion_size_grams: Decimal | None = Field(default=None, gt=0)
    portions_count_resolved: Decimal | None = Field(default=None, gt=0)
    total_raw_weight_grams: Decimal | None = Field(default=None, ge=0)
    total_cooked_weight_grams: Decimal | None = Field(default=None, ge=0)

    ingredients: List[RecipeIngredientWrite] = []


class RecipeIngredientResponse(SQLModel):
    id: UUID
    ingredient_id: UUID
    ingredient_name: str
    ingredient_default_unit: str

    quantity: float
    unit: str
    quantity_grams: float

    preparation: str | None = None
    sort_order: int


class RecipeSummaryResponse(SQLModel):
    id: UUID
    name: str
    description: str | None
    status: str
    yield_mode: str
    portions_count_resolved: float | None
    portion_size_grams: float | None
    created_at: datetime | None
    updated_at: datetime | None
    photo_url: str | None


class RecipeDetailResponse(RecipeSummaryResponse):
    instructions: str | None
    preparation_time_minutes: int | None
    cooking_time_minutes: int | None
    total_raw_weight_grams: float | None
    total_cooked_weight_grams: float | None
    is_component: bool | None
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


class RecipeSort(str, Enum):
    name_asc = "name_asc"
    name_desc = "name_desc"
    updated_at_asc = "updated_at_asc"
    updated_at_desc = "updated_at_desc"
    created_at_asc = "created_at_asc"
    created_at_desc = "created_at_desc"


# NOTE: mpeshko - Here __init__ is for OpenAPI documentation. 
# FastAPI documents only those query parameters that are declared in the 
# function signature or in a dependency (__init__), not inside models.
# __init__ is a special method in Python (also called a constructor)
# self is a reference to the object itself, which is currently being created or used.
class RecipeFilters:
    def __init__(
        self,
        status: str | None = Query(None, max_length=50, pattern="^(draft|active)$"),
        search: str | None = Query(
            None, description="Broad search across name and description"
        ),
        name: str | None = Query(
            None, description="Filter for exact or partial match in name only"
        ),
        sort_by: RecipeSort = Query(
            RecipeSort.updated_at_desc,
            description="List sorting. Format: field_direction",
        ),
    ):
        self.status = status
        self.search = search
        self.name = name
        self.sort_by = sort_by
