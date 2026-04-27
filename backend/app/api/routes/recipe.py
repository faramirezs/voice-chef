from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select
from sqlalchemy.orm import selectinload
from sqlalchemy import or_
from sqlalchemy.exc import IntegrityError
from app.core.database import get_session, engine
from uuid import UUID

from app.core.pagination import pagination_params, PaginationParams, paginate
from app.schemas.pagination import PaginatedResponse

from app.core.database import get_session
from app.models.recipe import Recipe
from app.models.ingredient import Ingredient
from app.schemas.ingredient import IngredientWrite
from app.schemas.pagination import PaginatedResponse
from app.utils.recipe_utils import to_recipe_detail, ensure_unique_recipe_name
from app.schemas.recipe import (
    RecipeWrite, RecipeSummaryResponse, RecipeUpdate, 
    RecipeDetailResponse, RecipeFilters, RecipeSort
)
from app.models.recipe_ingredients import RecipeIngredient


# -----------------------------------------------------------------------------
# Constants and Global Instances
# -----------------------------------------------------------------------------

router = APIRouter(prefix="/recipes", tags=["Recipes"])

# TEMP DEV DEFAULT: remove once tenant is resolved from auth context.
DEFAULT_TENANT_ID = UUID("0b796544-6414-4d62-8f1f-cd2f9f0ac0a0")


# ─── Routes ──────────────────────────────────────────────────────────────────

@router.get("", response_model=PaginatedResponse[RecipeSummaryResponse])
def retrieve_recipes(
    session: Session = Depends(get_session),
    pagination: PaginationParams = Depends(pagination_params),
    filters: RecipeFilters = Depends(),
):

    query = select(Recipe)
    if filters.status:
        query = query.where(Recipe.status == filters.status.strip())

    # Apply broad "search" across name and description for user-facing search bars.
    if filters.search:
        term = f"%{filters.search.strip()}%"
        query = query.where(or_(
            Recipe.name.ilike(term), 
            Recipe.description.ilike(term)))

    # Apply precise "name" filter for exact matching or programmatic filtering.
    if filters.name:
        term = f"%{filters.name.strip()}%"
        query = query.where(Recipe.name.ilike(term))

    sort_options = {
        RecipeSort.name_asc: (Recipe.name.asc(), Recipe.id.asc()),
        RecipeSort.name_desc: (Recipe.name.desc(), Recipe.id.desc()),
        RecipeSort.updated_at_asc: (Recipe.updated_at.asc(), Recipe.id.asc()),
        RecipeSort.updated_at_desc: (Recipe.updated_at.desc(), Recipe.id.desc()),
        RecipeSort.created_at_asc: (Recipe.created_at.asc(), Recipe.id.asc()),
        RecipeSort.created_at_desc: (Recipe.created_at.desc(), Recipe.id.desc()),
    }

    selected_sort = sort_options.get(
        filters.sort_by,
        sort_options[RecipeSort.updated_at_desc]
    )
    query = query.order_by(*selected_sort)

    recipes = paginate(query, session, pagination)
    return recipes


@router.get("/{id}", response_model=RecipeDetailResponse)
def retrieve_recipe(
    id: UUID, 
    session: Session = Depends(get_session)
):
    statement = (
        select(Recipe)
        .where(Recipe.id == id)
        .options(
            # Eagerly load the related RecipeIngredient objects in a separate query.
            selectinload(Recipe.recipe_ingredients) 
            # For each RecipeIngredient, also eagerly load its related Ingredient.
            .selectinload(RecipeIngredient.ingredient) 
        )
    )

    recipe = session.exec(statement).first()
    if not recipe:
        raise HTTPException(404, "Recipe not found")

    return to_recipe_detail(recipe)


@router.post("", response_model=RecipeSummaryResponse, status_code=201)
def create_recipe(
    recipe: RecipeWrite,
    tenant_id: UUID = DEFAULT_TENANT_ID,
    session: Session = Depends(get_session),
):
    ensure_unique_recipe_name(session, recipe.name, tenant_id)
    # Temporary dev-safe mode: fallback tenant_id until auth-based tenant resolution is implemented.
    payload = recipe.model_dump(exclude={"ingredients"})
    payload["tenant_id"] = tenant_id
    new_recipe = Recipe(**payload)

    # NOTE: mpeshko - try-catch block guarantees integrity in the presence 
    # of concurrent queries (race conditions).
    try:
        session.add(new_recipe)
        session.flush()
        session.commit()
        session.refresh(new_recipe)
    except IntegrityError:
        session.rollback()
        raise HTTPException(status_code=409, detail="Recipe name already exists")
    except Exception as e:
        session.rollback()
        raise HTTPException(status_code=400, detail=f"Database error: {str(e)}")

    return to_recipe_detail(new_recipe)


@router.patch("/{id}", response_model=RecipeSummaryResponse)
def update_recipe(
    id: UUID, 
    recipe_update: RecipeUpdate, 
    session: Session = Depends(get_session)
):
    """
    Update recipe fields with partial merge semantics
    """
    query = select(Recipe).where(Recipe.id == id)
    recipe = session.exec(query).first()
    if not recipe:
        raise HTTPException(status_code=404, detail="Recipe not found")

    # NOTE: mpeshko - Convert the input to a dict, EXCLUDING fields not sent by the client
    updates = recipe_update.model_dump(exclude_unset=True)

    # If name is being changed, validate uniqueness first
    if "name" in updates and updates["name"] != recipe.name:
        ensure_unique_recipe_name(session, updates["name"], recipe.tenant_id, exclude_id=id)

    for key, value in updates.items():
        setattr(recipe, key, value)
    try:
        session.add(recipe)
        session.commit()
        session.refresh(recipe)
    except IntegrityError:
        session.rollback()
        raise HTTPException(status_code=409, detail="Recipe name already exists")
    except Exception as e:
        session.rollback()
        raise HTTPException(status_code=400, detail=f"Database error: {str(e)}")
    return recipe


@router.delete("/{id}", response_model=RecipeSummaryResponse)
def delete_recipe(
    id: UUID, 
    session: Session = Depends(get_session)
):
    recipe = session.get(Recipe, id)
    if not recipe:
        raise HTTPException(status_code=404, detail="Recipe not found")

    session.refresh(recipe)

    result = to_recipe_detail(recipe)

    session.delete(recipe)
    session.commit()
    return result
