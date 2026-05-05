import os
from contextlib import asynccontextmanager
from fastapi import FastAPI, APIRouter
from fastapi.staticfiles import StaticFiles
from app.api.routes.auth import router as auth_router
from app.api.routes.users import router as user_router
from app.api.routes.recipe import router as recipe_router
from app.api.routes.ingredient import router as ingredient_router
from app.api.routes.file_service_images import router as images_router
from app.api.routes.file_service_pdfs import router as pdfs_router
from app.core.config import settings


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Start-up phase:
    os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
    
    yield # Runtime phase: FastAPI is fully running and serving requests
    
    # Shutdown Phase:
    # Cleanup code can be added here if needed


app = FastAPI(lifespan=lifespan)


api_router = APIRouter(prefix="/api")
api_router.include_router(auth_router)
api_router.include_router(user_router)
api_router.include_router(recipe_router)
api_router.include_router(ingredient_router)
api_router.include_router(images_router)
api_router.include_router(pdfs_router)

app.include_router(api_router)

@app.get("/")
def hello():
    return {"message": "Hello voice-chef"}
