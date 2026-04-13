from fastapi import FastAPI
from sqlalchemy import inspect
from app.core.database import engine

from app.schemas.pagination import PaginatedResponse
from app.api.routes.auth import router as auth_router
from app.api.routes.users import router as user_router
from app.api.routes.recipe import router as recipe_router
from app.api.routes.ingredient import router as ingredient_router

app = FastAPI()

app.include_router(auth_router, prefix="/api")
app.include_router(user_router, prefix="/api")
app.include_router(recipe_router, prefix="/api")
app.include_router(ingredient_router, prefix="/api")


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
