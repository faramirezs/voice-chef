from sqlmodel import SQLModel, Field
from typing import List
from uuid import UUID
from decimal import Decimal
from datetime import datetime
from pydantic import field_validator
from fastapi import Query
from enum import Enum
import re # Regular Expression

# --- Shared Logic Utility ---
def validate_recipe_name_string(v: str) -> str:
    """The core logic used by all name validators."""
    v = v.strip()
    if not v:
        raise ValueError("Invalid recipe name. Recipe name cannot be empty")
    if not re.search(r"[a-zA-Z]", v):
        raise ValueError("Invalid recipe name. It should contain at least 1 letter")
    return v


# ─── CREATE/UPDATE RECIPE INGREDIENT ────────────────────────────────────────────────

# NOTE: We cannot have the same ingredient in the same recipe twice
# You cannot have two different ingredients in the same recipe with the same sort_order

class RecipeIngredient(SQLModel):
    quantity: Decimal | None = Field(default=None, gt=0)
    unit: str | None = None
    preparation: str | None = None

class RecipeIngredientWrite(RecipeIngredient):
    ingredient_id: UUID
    sort_order: int = Field(ge=0)

class RecipeIngredientUpdate(RecipeIngredient):
    ingredient_id: UUID | None = None
    sort_order: int | None = Field(ge=0)

# ─── CREATE RECIPE ──────────────────────────────────────────────────────────────────


class RecipeWrite(SQLModel):
    # In Pydantic the ... (Ellipsis) signifies that a field is required
    name: str = Field(..., min_length=1)
    description: str | None = None
    instructions: str | None = None

    status: str = "draft"
    yield_mode: str = "count"

    portion_size_grams: Decimal | None = Field(default=None, gt=0)
    portions_count_resolved: Decimal | None = Field(default=None, gt=0)
    total_raw_weight_grams: Decimal | None = Field(default=None, ge=0)
    total_cooked_weight_grams: Decimal | None = Field(default=None, ge=0)

    # `default_factory` - it's essential for avoiding mutable default errors, 
    # such as sharing the same list across instances.
    ingredients: List[RecipeIngredientWrite] = Field(default_factory=list)
    #                                          ↑ HAS default: OPTIONAL

    @field_validator("name")
    @classmethod
    def validate_name_content(cls, v: str):
        # if v is None Pydantic will catch that before the validator runs
        return validate_recipe_name_string(v)


# ─── UPDATE RECIPE ──────────────────────────────────────────────────────────────────


class RecipeUpdate(SQLModel):
    # min_length=1 : it must be at least one character long
    name: str | None = Field(default=None, min_length=1)
    description: str | None = None
    instructions: str | None = None
    preparation_time_minutes: int | None = Field(default=None)
    cooking_time_minutes: int | None = Field(default=None)

    status: str | None = None
    yield_mode: str | None = None

    portion_size_grams: Decimal | None = Field(default=None, gt=0)
    portions_count_resolved: Decimal | None = Field(default=None, gt=0)
    total_raw_weight_grams: Decimal | None = Field(default=None, ge=0)
    total_cooked_weight_grams: Decimal | None = Field(default=None, ge=0)

    @field_validator("name")
    @classmethod
    def validate_optional_name(cls, v: str | None):
        # only validate if the user actually sent a value
        if v is not None:
            return validate_recipe_name_string(v)
        return v

    # ingredients: List[RecipeIngredientUpdate] | None = None


# ─── RESPONSES ──────────────────────────────────────────────────────────────────


class RecipeIngredientResponse(SQLModel):
    id: UUID
    ingredient_id: UUID
    ingredient_name: str
    ingredient_default_unit: str

    quantity: str | None
    unit: str | None
    quantity_grams: str

    preparation: str | None = None
    sort_order: int


class RecipeSummaryResponse(SQLModel):
    id: UUID
    name: str
    description: str | None
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
    instructions: str | None
    preparation_time_minutes: int | None
    cooking_time_minutes: int | None
    is_component: bool
    ingredients: List[RecipeIngredientResponse]


# ─── SORT, FILTERS ──────────────────────────────────────────────────────────────────


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
