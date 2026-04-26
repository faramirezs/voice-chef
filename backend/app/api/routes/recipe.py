from fastapi import APIRouter, Depends, HTTPException, Query
from sqlmodel import Session, select
from sqlalchemy import inspect
from sqlalchemy.orm import selectinload
from app.core.database import get_session, engine
from uuid import UUID
from typing import Optional

from app.core.pagination import pagination_params, PaginationParams, paginate
from app.schemas.pagination import PaginatedResponse

from app.core.database import get_session
from app.models.recipe import Recipe
from app.models.ingredient import Ingredient
from app.schemas.ingredient import IngredientWrite
from app.schemas.pagination import PaginatedResponse
from app.utils.recipe_utils import to_recipe_detail
from app.schemas.recipe import RecipeWrite, RecipeSummaryResponse, RecipeDetailResponse, RecipeUpdate
from app.models.recipe_ingredients import RecipeIngredient

router = APIRouter(prefix="/recipes", tags=["Recipes"])

# TEMP DEV DEFAULT: remove once tenant is resolved from auth context.
DEFAULT_TENANT_ID = UUID("0b796544-6414-4d62-8f1f-cd2f9f0ac0a0")

@router.post("", response_model=RecipeSummaryResponse)
def create_recipe(
    recipe: RecipeWrite,
    tenant_id: UUID = DEFAULT_TENANT_ID,
    session: Session = Depends(get_session),
):
    # Temporary dev-safe mode: fallback tenant_id until auth-based tenant resolution is implemented.
    payload = recipe.model_dump(exclude={"ingredients"})
    payload["tenant_id"] = tenant_id
    new_recipe = Recipe(**payload)

    session.add(new_recipe)
    session.flush()

    # for ing in recipe.ingredients:
    #     link = RecipeIngredients(
    #         recipe_id=recipe.id,
    #         ingredient_id=ing.ingredient_id,
    #         quantity=ing.quantity,
    #         unit=ing.unit,
    #         preparation=ing.preparation,
    #         sort_order=ing.sort_order,
    #     )
    #     session.add(link)

    session.commit()
    session.refresh(new_recipe)

    return to_recipe_detail(new_recipe)


@router.get("", response_model=PaginatedResponse[Recipe])
def retrieve_recipes(
    search: str = Query("", alias="query"),
    session: Session = Depends(get_session),
    pagination: PaginationParams = Depends(pagination_params),
    status: str | None = None,
    sort_by: str | None = None,
):

    query = select(Recipe)

    if status:
        query = query.where(Recipe.status == status.strip())

    search_term = search.strip()
    if search_term:
        query = query.where(Recipe.name.ilike(f"%{search_term}%"))

    sort_options = {
        "name_asc": (Recipe.name.asc(), Recipe.id.asc()),
        "name_desc": (Recipe.name.desc(), Recipe.id.desc()),
        "updated_at_asc": (Recipe.updated_at.asc(), Recipe.id.asc()),
        "updated_at_desc": (Recipe.updated_at.desc(), Recipe.id.desc()),
        "created_at_asc": (Recipe.created_at.asc(), Recipe.id.asc()),
        "created_at_desc": (Recipe.created_at.desc(), Recipe.id.desc()),
    }

    selected_sort = sort_options.get((sort_by or "").strip(), (Recipe.updated_at.desc(), Recipe.id.desc()))
    query = query.order_by(*selected_sort)

    recipes = paginate(query, session, pagination)
    return recipes


@router.get("/{recipe_id}", response_model=RecipeDetailResponse)
def retrieve_recipe(recipe_id: UUID, session: Session = Depends(get_session)):
    statement = (
        select(Recipe)
        .where(Recipe.id == recipe_id)
        .options(
            selectinload(Recipe.recipe_ingredients)
            .selectinload(RecipeIngredient.ingredient)
        )
    )

    recipe = session.exec(statement).first()

    if not recipe:
        raise HTTPException(404, "Recipe not found")

    return to_recipe_detail(recipe)

# NOTE: MK - Update recipe fields with partial merge semantics
@router.put("/{recipe_id}", response_model=RecipeSummaryResponse)
def update_recipe(recipe_id: UUID, recipe_update: RecipeUpdate, session: Session = Depends(get_session)):
    query = select(Recipe).where(Recipe.id == recipe_id)
    recipe = session.exec(query).first()

    if not recipe:
        raise HTTPException(status_code=404, detail="Recipe not found")

    updates = recipe_update.model_dump(exclude_unset=True)

    if "name" in updates:
        name_value = updates["name"]
        if name_value is None or not str(name_value).strip():
            raise HTTPException(status_code=422, detail="Recipe name cannot be empty")
        updates["name"] = str(name_value).strip()

    for key, value in updates.items():
        setattr(recipe, key, value)

    session.add(recipe)
    session.commit()
    session.refresh(recipe)

    return recipe

@router.delete("/{recipe_id}", response_model=RecipeSummaryResponse)
def delete_recipe(recipe_id: UUID, session: Session = Depends(get_session)):
    recipe = session.get(Recipe, recipe_id)

    if not recipe:
        raise HTTPException(status_code=404, detail="Recipe not found")

    session.refresh(recipe)

    result = to_recipe_detail(recipe)

    session.delete(recipe)
    session.commit()

    return result


