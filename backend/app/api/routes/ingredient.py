from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select
from app.core.database import get_session, engine

from app.core.pagination import pagination_params, PaginationParams, paginate
from app.schemas.pagination import PaginatedResponse

from app.core.database import get_session
from app.models.ingredient import Ingredients
from app.schemas.ingredient import IngredientWrite, IngredientSummaryResponse
from app.schemas.pagination import PaginatedResponse

router = APIRouter(prefix="/ingredients", tags=["Ingredients"])


@router.get("", response_model=PaginatedResponse[Ingredients])
def retrieve_ingredient(
    session: Session = Depends(get_session),
    pagination: PaginationParams = Depends(pagination_params),
    search: str | None = None,
    source: str | None = None,
):

    query = select(Ingredients)

    normalized_search = (search or "").strip()
    if normalized_search:
        query = query.where(Ingredients.name.ilike(f"%{normalized_search}%"))

    normalized_source = (source or "").strip()
    if normalized_source:
        query = query.where(Ingredients.source.ilike(f"%{normalized_source}%"))

    query = query.order_by(Ingredients.name.asc(), Ingredients.id.asc())

    ingredients = paginate(query, session, pagination)
    return ingredients


@router.post("", response_model=IngredientSummaryResponse, status_code=201)
def create_ingredient(
    ingredient: IngredientWrite, 
    session: Session = Depends(get_session)
):
    
    new_ingredient = Ingredients(**ingredient.model_dump())

    session.add(new_ingredient)
    session.flush()
    session.commit()
    session.refresh(new_ingredient)

    return new_ingredient


# @router.delete("/{ingredient_id}", response_model=IngredientSummaryResponse)
# def delete_ingredient(ingredient_id: UUID, session: Session = Depends(get_session)):
#     ingredient = session.get(Ingredient, ingredient_id)

#     if not ingredient:
#         raise HTTPException(status_code=404, detail="Ingredient not found")

#     session.refresh(ingredient)

#     session.delete(ingredient)
#     session.commit()

#     return ingredient
