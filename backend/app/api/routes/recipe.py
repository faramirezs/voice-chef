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

router = APIRouter(prefix="/recipe", tags=["Recipes"])


# # NOTE: MK - FOLLOWING END POINTS NOT FULLY TESTED YET  
########################################
@router.post("/create", response_model=RecipeSummaryResponse)
def create_recipe(recipe_in: RecipeWrite, session: Session = Depends(get_session)):
    recipe = Recipe(**recipe_in.model_dump(exclude={"ingredients"}))

    session.add(recipe)
    session.flush()

    # for ing in recipe_in.ingredients:
    #     link = RecipeIngredient(
    #         recipe_id=recipe.id,
    #         ingredient_id=ing.ingredient_id,
    #         quantity=ing.quantity,
    #         unit=ing.unit,
    #         preparation=ing.preparation,
    #         sort_order=ing.sort_order,
    #     )
    #     session.add(link)

    session.commit()
    session.refresh(recipe)

    return to_recipe_detail(recipe)


@router.get("/read_all", response_model=PaginatedResponse[Recipe])
def retrieve_recipes(
    session: Session = Depends(get_session),
    pagination: PaginationParams = Depends(pagination_params)):

    query = select(Recipe)
    recipes = paginate(query, session, pagination)
    return recipes


@router.get("/read/{recipe_id}", response_model=RecipeSummaryResponse)
def get_recipe(recipe_id: str, session: Session = Depends(get_session)):
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
@router.put("/update/{recipe_id}", response_model=RecipeSummaryResponse)
def update_recipe(recipe_id: str, recipe_update: RecipeUpdate, session: Session = Depends(get_session)):
    query = select(Recipe).where(Recipe.id == recipe_id)
    recipe = session.exec(query).first()

    if not recipe:
        raise HTTPException(status_code=404, detail="Recipe not found")

    for key, value in recipe_update.dict(exclude_unset=True).items():
        setattr(recipe, key, value)

    session.add(recipe)
    session.commit()
    session.refresh(recipe)

    return recipe

@router.delete("/delete/{recipe_id}", response_model=RecipeSummaryResponse)
def delete_recipe(recipe_id: str, session: Session = Depends(get_session)):
    recipe = session.get(Recipe, recipe_id)

    if not recipe:
        raise HTTPException(status_code=404, detail="Recipe not found")

    session.refresh(recipe)

    result = to_recipe_detail(recipe)
    # result = recipe.name

    session.delete(recipe)
    session.commit()

    return result


# # NOTE: MK - Retrieve one recipe by id
# @app.get("/recipes/{recipe_id}", response_model=RecipeDetailResponse)
# def retrieve_recipe(recipe_id: str, session: Session = Depends(get_session)):
#     query = select(Recipe).where(Recipe.id == recipe_id)
#     recipe = session.exec(query).first()

#     if not recipe:
#         raise HTTPException(status_code=404, detail="Recipe not found")

#     return recipe

# # NOTE: MK - Create a recipe 
# @app.post("/recipes", response_model=RecipeIngredientResponse)
# def create_recipe(recipe: RecipeWrite, session: Session = Depends(get_session)):
#     new_recipe = Recipe(**recipe.dict())
    
#     session.add(new_recipe)
#     session.commit()
#     session.refresh(new_recipe)

#     return new_recipe

# ########
# @app.get("/recipes/{recipe_id}", response_model=RecipeDetailResponse)
# def get_recipe(recipe_id: str, session: Session = Depends(get_session)):
#     recipe = session.get(Recipe, recipe_id)

#     if not recipe:
#         raise HTTPException(404, "Recipe not found")

#     return (recipe)
# ##########



# NOTE: MK - Delete recipe
# @app.delete("/recipes/{recipe_id}", response_model=RecipeDetailResponse)
# def delete_recipe(recipe_id: str, session: Session = Depends(get_session)):
#     query = select(Recipe).where(Recipe.id == recipe_id)
#     recipe = session.exec(query).first()

#     if not recipe:
#         raise HTTPException(status_code=404, detail="Recipe not found for tenant")

#     session.delete(recipe)
#     session.commit()

#     return recipe


