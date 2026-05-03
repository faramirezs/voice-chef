from fastapi import APIRouter, Depends, HTTPException, Response
from sqlmodel import Session, select
from sqlalchemy.orm import selectinload
from sqlalchemy import or_
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from uuid import UUID
from typing import Annotated

from app.core.database import get_session, engine
from app.core.pagination import (
    pagination_params, PaginationParams, paginate
)
from app.core.deps import get_current_user
from app.utils.recipe_utils import (
    to_recipe_detail, to_recipe_summary, ensure_unique_recipe_name,
    validate_recipe_business_rules
)
from app.models.recipe import Recipe
from app.models.ingredient import Ingredient
from app.models.recipe_ingredients import RecipeIngredient
from app.models.users import Users
from app.schemas.pagination import PaginatedResponse
from app.schemas.ingredient import IngredientWrite
from app.schemas.recipe import (
    RecipeWrite, RecipeSummaryResponse, RecipeUpdate, 
    RecipeDetailResponse, RecipeFilters, RecipeSort
)


# -----------------------------------------------------------------------------
# Constants and Global Instances
# -----------------------------------------------------------------------------

router = APIRouter(prefix="/recipes", tags=["Recipes"])



# ─── Routes ──────────────────────────────────────────────────────────────────

@router.get("", response_model=PaginatedResponse[RecipeSummaryResponse])
def retrieve_recipes(
    current_user: Annotated[Users, Depends(get_current_user)],
    session: Session = Depends(get_session),
    pagination: PaginationParams = Depends(pagination_params),
    filters: RecipeFilters = Depends()
):
    """
    List recipes for authenticated tenant
    """
    tenant_id = current_user.tenant_id

    query = select(Recipe).where(Recipe.tenant_id == tenant_id)
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

    paginated = paginate(query, session, pagination)
    
    # Convert recipes using helper function
    paginated["items"] = [to_recipe_summary(r) for r in paginated["items"]]
    
    return paginated


@router.get("/{id}", response_model=RecipeDetailResponse)
def retrieve_recipe(
    current_user: Annotated[Users, Depends(get_current_user)],
    id: UUID, 
    session: Session = Depends(get_session),
):
    statement = (
        select(Recipe)
        .where(Recipe.id == id, Recipe.tenant_id == current_user.tenant_id)
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


# This function creates the many-to-many relationship between a recipe 
# and its ingredients
@router.post("", response_model=RecipeDetailResponse, status_code=201)
def create_recipe(
    recipe: RecipeWrite,
    current_user: Annotated[Users, Depends(get_current_user)],
    session: Session = Depends(get_session),
):
    tenant_id = current_user.tenant_id
    ensure_unique_recipe_name(session, recipe.name, tenant_id)
    
    # Validate business rules (Error 400 from api-spec)
    validate_recipe_business_rules(recipe)
    
    payload = recipe.model_dump(exclude={"ingredients"})
    payload["tenant_id"] = tenant_id
    new_recipe = Recipe(**payload)
    ingredients_data = recipe.ingredients or []

    try:
        # Create and save recipe first
        session.add(new_recipe)
        session.flush()
        
        # Create ingredient links for each ingredient
        # Loop through each ingredient
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
        session.refresh(new_recipe)
        
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
        
    except IntegrityError as e:
        session.rollback()
        raise HTTPException(
            status_code=409, 
            detail="Recipe name already exists or constraint violation"
        )
    except HTTPException:
        raise  # Re-raise HTTPException (ingredient not found, 404)
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

    return to_recipe_detail(new_recipe)


@router.patch("/{id}", response_model=RecipeSummaryResponse)
def update_recipe(
    current_user: Annotated[Users, Depends(get_current_user)],
    id: UUID, 
    recipe_update: RecipeUpdate, 
    session: Session = Depends(get_session)
):
    """
    Update recipe fields with partial merge semantics
    """
    query = select(Recipe).where(
        Recipe.id == id, 
        Recipe.tenant_id == current_user.tenant_id)
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
    
    # Validate business rules after applying updates
    # validate_recipe_business_rules(recipe)
    
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
def delete_recipe(
    current_user: Annotated[Users, Depends(get_current_user)],
    id: UUID, 
    session: Session = Depends(get_session)
):
    statement = select(Recipe).where(
        Recipe.id == id,
        Recipe.tenant_id == current_user.tenant_id
    )
    recipe = session.exec(statement).first()
    if not recipe:
        raise HTTPException(status_code=404, detail="Recipe not found")

    try:
        session.delete(recipe)
        session.commit()
    except Exception as e:
        session.rollback()
        raise HTTPException(status_code=400, detail=f"Database error: {str(e)}")
    
    return Response(status_code=204)
