from fastapi import FastAPI, Depends, HTTPException
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

# NOTE: DL - this is just a test endpoint to verify that we can fetch recipes from the database. 
# We will remove this later and implement proper endpoints for recipes.
@app.get("/recipes")
def fetch_recipes(session: Session = Depends(get_db)):
    query = select(models.Recipes)
    recipes = result = session.exec(query).all()
    return recipes

@app.get("/recipes/{recipe_id}")
def fetch_recipe(recipe_id: str, session: Session = Depends(get_db)):
    query = select(models.Recipes).where(models.Recipes.id == recipe_id)
    recipe = session.exec(query).first()

    if not recipe:
        raise HTTPException(status_code=404, detail="Recipe not found")

    return recipe

@app.post("/recipes")
def create_recipe(recipe: schemas.RecipeCreate, session: Session = Depends(get_db)):
    new_recipe = models.Recipes(**recipe.dict())
    
    session.add(new_recipe)
    session.commit()
    session.refresh(new_recipe)

    return new_recipe
