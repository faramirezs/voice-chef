from fastapi import Query, FastAPI, Depends, HTTPException
from sqlmodel import Session, select
from sqlalchemy import inspect
from app.core.database import get_db, engine
from app.models.recipe import Recipe
from app.models.ingredient import Ingredient
from app.schemas.recipe import RecipeWrite, RecipeDetailResponse, RecipeSummaryResponse, RecipeUpdate
from app.schemas.recipe import RecipeIngredientWrite, RecipeIngredientUpdate, RecipeIngredientResponse
# from app.mappers.recipe_mapper import to_recipe_detail
from app.schemas.ingredient import IngredientWrite
from app.models.users import Users, Tenants
from app.models.recipe_ingredients import RecipeIngredient
from app.mappers.recipe_mapper import to_recipe_detail
from sqlalchemy.orm import selectinload

app = FastAPI()

# ─── Routes ──────────────────────────────────────────────────────────────────

@app.get("/")
def hello():
    return {"message": "Hello voice-chef"}

# List DB tables (GET)
# NOTE: DL: You cannot fully replace inspect() with SQLModel's own APIs, but this is a simple 
# endpoint to verify that we can connect to the database and fetch table names. 
@app.get("/tables")
def list_tables():
    inspector = inspect(engine)
    return {"tables": inspector.get_table_names()}

# ----------------
# Recipe endpoints
# ----------------
# NOTE: DL - this is just a test endpoint to verify that we can fetch recipes from the database. 
# We will remove this later and implement proper endpoints for recipes.
@app.get("/recipes")
def retrieve_recipes(session: Session = Depends(get_db)):
    query = select(Recipe)
    recipes = session.exec(query).all()
    return recipes


# # NOTE: MK - FOLLOWING END POINTS NOT TESTED YET  
########################################
@app.post("/recipes", response_model=RecipeSummaryResponse)
def create_recipe(recipe_in: RecipeWrite, session: Session = Depends(get_db)):
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


@app.get("/recipes/{recipe_id}", response_model=RecipeSummaryResponse)
def get_recipe(recipe_id: str, session: Session = Depends(get_db)):
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
@app.put("/recipes/{recipe_id}", response_model=RecipeSummaryResponse)
def update_recipe(recipe_id: str, recipe_update: RecipeUpdate, session: Session = Depends(get_db)):
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

@app.delete("/recipes/{recipe_id}", response_model=RecipeSummaryResponse)
def delete_recipe(recipe_id: str, session: Session = Depends(get_db)):
    recipe = session.get(Recipe, recipe_id)

    if not recipe:
        raise HTTPException(status_code=404, detail="Recipe not found")

    session.refresh(recipe)

    result = to_recipe_detail(recipe)
    # result = recipe.name

    session.delete(recipe)
    session.commit()

    return result
########################################################


# # NOTE: MK - Retrieve one recipe by id
# @app.get("/recipes/{recipe_id}", response_model=RecipeDetailResponse)
# def retrieve_recipe(recipe_id: str, session: Session = Depends(get_db)):
#     query = select(Recipe).where(Recipe.id == recipe_id)
#     recipe = session.exec(query).first()

#     if not recipe:
#         raise HTTPException(status_code=404, detail="Recipe not found")

#     return recipe

# # NOTE: MK - Create a recipe 
# @app.post("/recipes", response_model=RecipeIngredientResponse)
# def create_recipe(recipe: RecipeWrite, session: Session = Depends(get_db)):
#     new_recipe = Recipe(**recipe.dict())
    
#     session.add(new_recipe)
#     session.commit()
#     session.refresh(new_recipe)

#     return new_recipe

# ########
# @app.get("/recipes/{recipe_id}", response_model=RecipeDetailResponse)
# def get_recipe(recipe_id: str, session: Session = Depends(get_db)):
#     recipe = session.get(Recipe, recipe_id)

#     if not recipe:
#         raise HTTPException(404, "Recipe not found")

#     return (recipe)
# ##########



# NOTE: MK - Delete recipe
# @app.delete("/recipes/{recipe_id}", response_model=RecipeDetailResponse)
# def delete_recipe(recipe_id: str, session: Session = Depends(get_db)):
#     query = select(Recipe).where(Recipe.id == recipe_id)
#     recipe = session.exec(query).first()

#     if not recipe:
#         raise HTTPException(status_code=404, detail="Recipe not found for tenant")

#     session.delete(recipe)
#     session.commit()

#     return recipe

######

# # --------------------
# # Ingredient endpoints
# # --------------------


# NOTE: MK - Retrieve Ingredients
@app.get("/ingredients")
def retrieve_ingredients(
    session: Session = Depends(get_db),    
    offset: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100)):

    query = select(Ingredient).offset(offset).limit(limit)
    ingredients = session.exec(query).all()
    return ingredients


@app.post("/ingredients")
def create_ingredient(ingredient: IngredientWrite, session: Session = Depends(get_db)):
    new_ingredient = Ingredient(**ingredient.dict())
    
    session.add(new_ingredient)
    session.commit()
    session.refresh(new_ingredient)

    return new_ingredient

