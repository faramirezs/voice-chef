from contextlib import asynccontextmanager
from fastapi import FastAPI, Depends
from sqlmodel import Session, select
from sqlalchemy import inspect
from app.database import get_db, engine, create_db_and_tables
from app import models


@asynccontextmanager
# Lifespan function to create tables on startup
async def lifespan(app: FastAPI):
    create_db_and_tables()
    yield


app = FastAPI(lifespan=lifespan)


# ─── Routes ──────────────────────────────────────────────────────────────────

@app.get("/")
def hello():
    return {"message": "Hello voice-chef"}

# NOTE: DL - this is just a test endpoint to verify that we can fetch recipes from the database. 
# We will remove this later and implement proper endpoints for recipes.
@app.get("/recipes")
def fetch_recipes(session: Session = Depends(get_db)):
    query = select(models.Recipe)
    result = session.exec(query)
    recipes = result.all()
    return recipes

# List DB tables (GET)
# NOTE: DL: You cannot fully replace inspect() with SQLModel's own APIs, but this is a simple 
# endpoint to verify that we can connect to the database and fetch table names. 
@app.get("/tables")
def list_tables():
    inspector = inspect(engine)
    return {"tables": inspector.get_table_names()}