from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select
from sqlalchemy.orm import selectinload
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from uuid import UUID
import os

from app.core.pagination import pagination_params, PaginationParams, paginate
from app.schemas.pagination import PaginatedResponse

from app.core.database import get_session, engine
from app.models.recipe import Recipe
from app.utils.recipe_utils import to_recipe_detail
from app.schemas.recipe import (
    RecipeWrite, RecipeSummaryResponse, RecipeUpdate, 
    RecipeDetailResponse
)
from app.models.recipe_ingredients import RecipeIngredient


# -----------------------------------------------------------------------------
# Constants and Global Instances
# -----------------------------------------------------------------------------

router = APIRouter(prefix="/recipes", tags=["Recipes"])

DEFAULT_TENANT_ID = UUID(os.getenv("DEFAULT_TENANT_ID", "0b796544-6414-4d62-8f1f-cd2f9f0ac0a0"))


# ─── Routes ──────────────────────────────────────────────────────────────────

@router.get("", response_model=PaginatedResponse[Recipe])
def retrieve_recipes(
    session: Session = Depends(get_session),
    pagination: PaginationParams = Depends(pagination_params),
    status: str | None = None,
    search: str | None = None,
    name: str | None = None,
    sort_by: str | None = None,
):

    query = select(Recipe)
    if status:
        query = query.where(Recipe.status == status.strip())

    search_term = (search or name or "").strip()
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


@router.get("/{id}", response_model=RecipeDetailResponse)
def retrieve_recipe(id: UUID, session: Session = Depends(get_session)):
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


@router.post("", response_model=RecipeSummaryResponse)
def create_recipe(
    recipe: RecipeWrite,
    tenant_id: UUID = DEFAULT_TENANT_ID,
    session: Session = Depends(get_session),
):
    payload = recipe.model_dump(exclude={"ingredients"})
    payload["tenant_id"] = tenant_id
    new_recipe = Recipe(**payload)

    session.add(new_recipe)
    session.flush()
    session.commit()
    session.refresh(new_recipe)

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

    for key, value in updates.items():
        setattr(recipe, key, value)
    
    try:
        session.add(recipe)
        session.commit()
        session.refresh(recipe)
    except IntegrityError as e:
        session.rollback()
        raise HTTPException(
            status_code=409, 
            detail="Update violates data constraints (e.g., duplicate name or invalid reference)"
        )
    except SQLAlchemyError as e:
        session.rollback()
        raise HTTPException(
            status_code=500, 
            detail="Internal server error while updating recipe"
        )
    except Exception as e:
        session.rollback()
        raise HTTPException(
            status_code=500, 
            detail="Internal server error"
        )
    
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
