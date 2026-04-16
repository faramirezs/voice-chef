from fastapi import FastAPI, APIRouter
from fastapi.staticfiles import StaticFiles
from app.api.routes.auth import router as auth_router
from app.api.routes.users import router as user_router
from app.api.routes.recipe import router as recipe_router
from app.api.routes.ingredient import router as ingredient_router
from app.api.routes.recipe_photos import router as recipe_photos_router

app = FastAPI()

api_router = APIRouter(prefix="/api")

api_router.include_router(auth_router)
api_router.include_router(user_router)
api_router.include_router(recipe_router)
api_router.include_router(ingredient_router)
api_router.include_router(recipe_photos_router)
app.include_router(api_router)

app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")

# ─── Routes ──────────────────────────────────────────────────────────────────

@app.get("/")
def hello():
    return {"message": "Hello voice-chef"}
