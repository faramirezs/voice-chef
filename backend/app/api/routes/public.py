from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy import or_
from sqlalchemy.orm import selectinload
from sqlmodel import Session, select

from app.core.database import get_session
from app.core.deps import DEFAULT_TENANT_ID
from app.core.pagination import PaginationParams, paginate, pagination_params
from app.models.recipe import Recipe
from app.models.recipe_ingredients import RecipeIngredient
from app.schemas.pagination import PaginatedResponse
from app.schemas.recipe import RecipeFilters, RecipeSort, RecipeDetailResponse, RecipeSummaryResponse
from app.utils.recipe_utils import to_recipe_detail, to_recipe_summary
from app.limiter import limiter

router = APIRouter(prefix="",
                   tags=["Public"])


@router.get("/recipes", response_model=PaginatedResponse[RecipeSummaryResponse])
@limiter.limit("5/minute")
def get_recipes(
    request: Request,
    session: Session = Depends(get_session),
    pagination: PaginationParams = Depends(pagination_params),
    filters: RecipeFilters = Depends(),
):
    query = select(Recipe).where(Recipe.tenant_id == DEFAULT_TENANT_ID)

    # Public list can be narrowed explicitly with ?status=draft|active.
    # If omitted, return both so seeded draft data is visible in non-prod setups.
    if filters.status:
        query = query.where(Recipe.status == filters.status.strip())
    else:
        query = query.where(Recipe.status.in_(["draft", "active"]))

    if filters.search:
        term = f"%{filters.search.strip()}%"
        query = query.where(
            or_(
                Recipe.name.ilike(term),
                Recipe.description.ilike(term),
            )
        )

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
    query = query.order_by(*sort_options.get(filters.sort_by, sort_options[RecipeSort.updated_at_desc]))

    paginated = paginate(query, session, pagination)
    paginated["items"] = [to_recipe_summary(recipe) for recipe in paginated["items"]]
    return paginated


@router.get("/recipes/{id}", response_model=RecipeDetailResponse)
def get_recipe(
    id: UUID,
    session: Session = Depends(get_session),
):
    statement = (
        select(Recipe)
        .where(
            Recipe.id == id,
            Recipe.tenant_id == DEFAULT_TENANT_ID,
            Recipe.status.in_(["draft", "active"]),
        )
        .options(
            selectinload(Recipe.recipe_ingredients).selectinload(
                RecipeIngredient.ingredient
            )
        )
    )

    recipe = session.exec(statement).first()
    if not recipe:
        raise HTTPException(404, "Recipe not found")

    return to_recipe_detail(recipe)


# @router.get("/recipes/", response_model=RecipeDetailResponse)
# def get_public_recipes(db: Session = Depends(get_session)):
#     return retrieve_recipes(db=db)