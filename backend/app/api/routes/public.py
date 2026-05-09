from fastapi import APIRouter, Depends, HTTPException, Request, Response
from sqlalchemy import or_
from sqlalchemy.orm import selectinload
from sqlmodel import Session, select
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from uuid import UUID
from typing import Annotated, Tuple

from app.core.database import get_session
from app.core.deps import DEFAULT_TENANT_ID
from app.core.pagination import (
    pagination_params, PaginationParams, paginate
)
from app.core.deps import get_current_user
from app.utils.recipe_utils import (
    to_recipe_detail, to_recipe_summary, ensure_unique_recipe_name,
    validate_recipe_business_rules, validate_all_ingredients_exist_no_duplicates,
    validate_ingredient_sort_order
)
from app.models.recipe import Recipe
from app.models.ingredient import Ingredient
from app.models.recipe_ingredients import RecipeIngredient
from app.models.users import Users
from app.schemas.pagination import PaginatedResponse
from app.schemas.recipe import (
    RecipeWrite, RecipeSummaryResponse, RecipeUpdate, 
    RecipeDetailResponse, RecipeFilters, RecipeSort
)
from app.utils.file_service_image_utils import delete_file
from app.utils.api_key_utils import require_api_key
from app.core.limiter import limiter

router = APIRouter(prefix="", tags=["Public"])


@router.get("/recipes", response_model=PaginatedResponse[RecipeSummaryResponse])
@limiter.limit("5/minute")
def get_recipes(
    request: Request,
    session: Session = Depends(get_session),
    pagination: PaginationParams = Depends(pagination_params),
    filters: RecipeFilters = Depends(),
):
    """
    Public endpoint to list recipes from the default tenant.
    No authentication required, but rate-limited.
    """
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
@limiter.limit("10/minute")
def get_recipe(
    request: Request,
    id: UUID,
    api_key: Annotated[Tuple[UUID, str], Depends(require_api_key)],
    session: Session = Depends(get_session),
):
    """
    Public endpoint to retrieve a single recipe.
    Requires API key authentication.
    """
    # Use API key's tenant if provided, otherwise use default tenant
    tenant_id = api_key[0] if api_key else DEFAULT_TENANT_ID
    
    statement = (
        select(Recipe)
        .where(Recipe.id == id, Recipe.tenant_id == tenant_id)
        .options(
            selectinload(Recipe.recipe_ingredients) 
            .selectinload(RecipeIngredient.ingredient) 
        )
    )

    recipe = session.exec(statement).first()
    if not recipe:
        raise HTTPException(404, "Recipe not found")

    return to_recipe_detail(recipe)


@router.post("/recipes", response_model=RecipeDetailResponse, status_code=201)
@limiter.limit("5/minute")
def create_recipe(
    request: Request,
    api_key: Annotated[Tuple[UUID, str], Depends(require_api_key)],
    recipe: RecipeWrite,
    session: Session = Depends(get_session),
):
    """
    Public endpoint to create a recipe.
    Requires API key authentication.
    """
    tenant_id = api_key[0]
    ensure_unique_recipe_name(session, recipe.name, tenant_id)
    validate_recipe_business_rules(recipe)
    validate_ingredient_sort_order(recipe)
    validate_all_ingredients_exist_no_duplicates(session, recipe)

    try:
        payload = recipe.model_dump(exclude={"ingredients"})
        payload["tenant_id"] = tenant_id
        new_recipe = Recipe(**payload)
        ingredients_data = recipe.ingredients or []

        session.add(new_recipe)
        session.flush()
        
        # Create ingredient links for each ingredient
        for ing_data in ingredients_data:
            ingredient = session.get(Ingredient, ing_data.ingredient_id)
            if not ingredient:
                session.rollback()
                raise HTTPException(
                    status_code=404, 
                    detail=f"Ingredient {ing_data.ingredient_id} not found"
                )
            
            # Create recipe_ingredient link
            recipe_ingredient = RecipeIngredient(
                recipe_id=new_recipe.id,
                ingredient_id=ing_data.ingredient_id,
                quantity=ing_data.quantity,
                unit=ing_data.unit,
                preparation=ing_data.preparation,
                sort_order=ing_data.sort_order
            )
            session.add(recipe_ingredient)
        
        session.commit()
        session.refresh(new_recipe, ["recipe_ingredients"])
        
        # Eagerly load ingredients for response
        statement = (
            select(Recipe)
            .where(Recipe.id == new_recipe.id)
            .options(
                selectinload(Recipe.recipe_ingredients)
                .selectinload(RecipeIngredient.ingredient)
            )
        )
        new_recipe = session.exec(statement).first()

        return to_recipe_detail(new_recipe)
        
    except IntegrityError as e:
        session.rollback()
        raise HTTPException(
            status_code=409, 
            detail="Recipe name already exists or constraint violation"
        )
    except HTTPException:
        raise
    except SQLAlchemyError as e:
        session.rollback()
        raise HTTPException(
            status_code=500, 
            detail="Internal server error while creating recipe"
        )
    except Exception as e:
        session.rollback()
        raise HTTPException(
            status_code=500, 
            detail="Internal server error"
        )
    
@router.patch("/{id}", response_model=RecipeSummaryResponse)
@limiter.limit("5/minute")
def update_recipe(
    request: Request,
    id: UUID, 
    recipe_update: RecipeUpdate, 
    api_key: Annotated[Tuple[UUID, str], Depends(require_api_key)],
    session: Session = Depends(get_session)
):
    """
    Public endpoint to update a recipe.
    Requires API key authentication.
    """
    tenant_id = api_key[0]
    query = select(Recipe).where(
        Recipe.id == id, 
        Recipe.tenant_id == tenant_id)
    recipe = session.exec(query).first()
    if not recipe:
        raise HTTPException(status_code=404, detail="Recipe not found")

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
    return to_recipe_summary(recipe)


@router.delete("/{id}", status_code=204)
@limiter.limit("5/minute")
def delete_recipe(
    request: Request,
    id: UUID, 
    api_key: Annotated[Tuple[UUID, str], Depends(require_api_key)],
    session: Session = Depends(get_session)
):
    """
    Public endpoint to delete a recipe.
    Requires API key authentication.
    """
    statement = select(Recipe).where(
        Recipe.id == id,
        Recipe.tenant_id == api_key[0]
    )
    recipe = session.exec(statement).first()
    if not recipe:
        raise HTTPException(status_code=404, detail="Recipe not found")

    try:
        photo_url = recipe.photo_url
        session.delete(recipe)
        session.commit()
        if photo_url:
            delete_file(photo_url)
    except Exception as e:
        session.rollback()
        raise HTTPException(status_code=400, detail=f"Database error: {str(e)}")
    
    return Response(status_code=204)
