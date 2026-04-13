from uuid import UUID
from fastapi import FastAPI, Depends, HTTPException
from sqlmodel import Session, select
from sqlalchemy import inspect
from app.database import get_session, engine
from app import models
from app.api.routes.auth import router as auth_router
from app.api.routes.users import router as user_router


app = FastAPI()

app.include_router(auth_router, prefix="/api")
app.include_router(user_router, prefix="/api")

# ─── Routes ──────────────────────────────────────────────────────────────────

@app.get("/")
def hello():
    return {"message": "Hello voice-chef"}

# NOTE: DL - this is just a test endpoint to verify that we can fetch recipes from the database. 
# We will remove this later and implement proper endpoints for recipes.
@app.get("/recipes")
def fetch_recipes(session: Session = Depends(get_session)):
    query = select(models.Recipe)
    result = session.exec(query)
    recipes = result.all()
    return recipes

@app.get("/recipes/{recipe_id}")
def get_recipe(recipe_id: UUID, session: Session = Depends(get_session)):
    recipe = session.get(models.Recipe, recipe_id)
    if not recipe:
        raise HTTPException(status_code=404, detail="Recipe not found")
    return recipe

# List DB tables (GET)
# NOTE: DL: You cannot fully replace inspect() with SQLModel's own APIs, but this is a simple 
# endpoint to verify that we can connect to the database and fetch table names. 
@app.get("/tables")
def list_tables():
    inspector = inspect(engine)
    return {"tables": inspector.get_table_names()}
