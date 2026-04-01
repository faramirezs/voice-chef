from fastapi import FastAPI, Depends
from sqlmodel import Session, select, SQLModel
from app.database import get_session, engine
from app import models


app = FastAPI()


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

# This endpoint lists all tables that have a defined SQLModel class
@app.get("/defined-models")
def list_defined_models():
    # SQLModel.metadata holds all the table information from your defined models
    defined_tables = list(SQLModel.metadata.tables.keys())
    return {"defined_models": defined_tables}
