from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select
from sqlalchemy import func
from app.core.database import get_session, engine
from typing import List

from app.core.pagination import pagination_params, PaginationParams, paginate
from app.schemas.pagination import PaginatedResponse

from app.core.database import get_session
from app.models.ingredient import Ingredients
from app.schemas.ingredient import IngredientWrite, IngredientResponse
from app.schemas.pagination import PaginatedResponse

router = APIRouter(prefix="/ingredients", tags=["Ingredients"])


@router.get("/autocomplete", response_model=List[dict])
def autocomplete_ingredients(
    query: str = "",
    limit: int = 10,
    session: Session = Depends(get_session),
):
    """
    Autocomplete (Typeahead) endpoint for ingredient search.
    
    Returns ingredients that START with the query (case-insensitive).
    Optimized for fast typeahead responses.
    """
    
    query = (query or "").lstrip()
    limit = max(1, min(limit, 10))
    
    # Validate query length
    if len(query) > 50:
        raise HTTPException(
            status_code=400, detail="Query must not exceed 50 characters"
        )
    
    if len(query) < 1:
        return []
    
    # Query: ingredients that START with the search term (word boundary)
    ingredient_list = session.exec(
        select(Ingredients).where(
            Ingredients.name.ilike(f"{query}%")
    #                                       ↑ SQL wildcard: matches anything after
        )
        .order_by(Ingredients.name.asc())
        .limit(limit)
    ).all()
    
    return [
        {
            "id": str(ingredient.id),
            "name": ingredient.name,
        }
        for ingredient in ingredient_list
    ]


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
        query = query.where(Ingredients.name.ilike(f"{normalized_search}%"))

    normalized_source = (source or "").strip()
    if normalized_source:
        query = query.where(Ingredients.source.ilike(f"%{normalized_source}%"))

    query = query.order_by(Ingredients.name.asc(), Ingredients.id.asc())

    ingredients = paginate(query, session, pagination)
    return ingredients


@router.post("", response_model=IngredientResponse)
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


# @router.delete("/{id}", response_model=IngredientResponse)
# def delete_ingredient(ingredient_id: UUID, session: Session = Depends(get_session)):
#     ingredient = session.get(Ingredient, ingredient_id)

#     if not ingredient:
#         raise HTTPException(status_code=404, detail="Ingredient not found")

#     session.refresh(ingredient)

#     session.delete(ingredient)
#     session.commit()

#     return ingredient


# @router.patch("/{id}", response_model=IngredientResponse)
# def update_ingredient(
#     id: UUID,
#     ingredient_update: IngredientUpdate,
#     session: Session = Depends(get_session)
# ):
#     # implementation...
