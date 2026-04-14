from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select
from sqlalchemy import inspect
from sqlalchemy.orm import selectinload
from app.core.database import get_session, engine

from app.core.pagination import pagination_params, PaginationParams, paginate
from app.schemas.pagination import PaginatedResponse

from app.core.database import get_session
from app.models.recipe import Recipe
from app.models.ingredient import Ingredient
from app.schemas.ingredient import IngredientWrite
from app.schemas.pagination import PaginatedResponse
from app.schemas.recipe_utils import to_recipe_detail
from app.schemas.recipe import RecipeWrite, RecipeSummaryResponse, RecipeUpdate
from app.models.recipe_ingredients import RecipeIngredient

router = APIRouter(prefix="/ingredient", tags=["Ingredients"])


@router.get("", response_model=PaginatedResponse[Ingredient])
def retrieve_ingredients(
    session: Session = Depends(get_session),
    pagination: PaginationParams = Depends(pagination_params)):

    query = select(Ingredient)
    ingredients = paginate(query, session, pagination)
    return ingredients


@router.post("")
def create_ingredient(ingredient: IngredientWrite, session: Session = Depends(get_session)):
    new_ingredient = Ingredient(**ingredient.model_dump())
        
    session.add(new_ingredient)
    session.commit()
    session.refresh(new_ingredient)

    return new_ingredient