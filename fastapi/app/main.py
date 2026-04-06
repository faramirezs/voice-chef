from fastapi import Query, FastAPI, Depends, HTTPException
from sqlmodel import Session, select
from sqlalchemy import inspect
from app.database import get_db, engine
from app import models
from app import schemas

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
    query = select(models.Recipe)
    recipes = result = session.exec(query).all()
    return recipes


# NOTE: MK - Retrieve one recipe by id
@app.get("/recipes/{recipe_id}", response_model=schemas.RecipeRead)
def retrieve_recipe(recipe_id: str, session: Session = Depends(get_db)):
    query = select(models.Recipe).where(models.Recipe.id == recipe_id)
    recipe = session.exec(query).first()

    if not recipe:
        raise HTTPException(status_code=404, detail="Recipe not found")

    return recipe

# # NOTE: MK - Create a recipe 
# @app.post("/recipes", response_model=schemas.RecipeRead)
# def create_recipe(recipe: schemas.RecipeCreate, session: Session = Depends(get_db)):
#     new_recipe = models.Recipe(**recipe.dict())
    
#     session.add(new_recipe)
#     session.commit()
#     session.refresh(new_recipe)

#     return new_recipe

# NOTE: MK - Update recipe fields with partial merge semantics
@app.put("/recipes/{recipe_id}", response_model=schemas.RecipeRead)
def update_recipe(recipe_id: str, recipe_update: schemas.RecipeUpdate, session: Session = Depends(get_db)):
    query = select(models.Recipe).where(models.Recipe.id == recipe_id)
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
#     query = select(models.Recipe).where(models.Recipe.id == recipe_id)
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
    limit: int = Query(50, ge=1, le=200)):
    
    query = select(models.Ingredients)
    ingredients = session.exec(query).all()
    return ingredients


@app.post("/ingredients")
def create_ingredient(ingredient: schemas.IngredientCreate, session: Session = Depends(get_db)):
    new_ingredient = models.Ingredients(**ingredient.dict())
    
    session.add(new_ingredient)
    session.commit()
    session.refresh(new_ingredient)

    return new_ingredient

