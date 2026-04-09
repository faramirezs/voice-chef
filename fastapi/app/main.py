from fastapi import Query, FastAPI, Depends, HTTPException
from sqlmodel import Session, select
from sqlalchemy import inspect
from app.core.database import get_db, engine
from app.models.recipe import Recipe
from app.models.ingredient import Ingredient
from app.schemas.recipe import RecipeRead, RecipeUpdate, RecipeCreate
from app.schemas.ingredient import IngredientWrite
from app.models.users import Users


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


# NOTE: MK - Retrieve one recipe by id
@app.get("/recipes/{recipe_id}", response_model=RecipeRead)
def retrieve_recipe(recipe_id: str, session: Session = Depends(get_db)):
    query = select(Recipe).where(Recipe.id == recipe_id)
    recipe = session.exec(query).first()

    if not recipe:
        raise HTTPException(status_code=404, detail="Recipe not found")

    return recipe

# NOTE: MK - Create a recipe 
@app.post("/recipes", response_model=RecipeRead)
def create_recipe(recipe: RecipeCreate, session: Session = Depends(get_db)):
    new_recipe = Recipe(**recipe.dict())
    
    session.add(new_recipe)
    session.commit()
    session.refresh(new_recipe)

    return new_recipe

# NOTE: MK - Update recipe fields with partial merge semantics
@app.put("/recipes/{recipe_id}", response_model=RecipeRead)
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

# # NOTE: MK - Delete recipe
# @app.delete("/recipes/{recipe_id}", response_model=schemas.RecipeRead)
# def delete_recipe(recipe_id: str, session: Session = Depends(get_db)):
#     query = select(Recipe).where(Recipe.id == recipe_id)
#     recipe = session.exec(query).first()

#     if not recipe:
#         raise HTTPException(status_code=404, detail="Recipe not found for tenant")

#     session.delete(recipe)
#     session.commit()

#     return recipe


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

