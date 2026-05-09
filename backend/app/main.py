import os
from contextlib import asynccontextmanager
from fastapi import FastAPI, APIRouter
from fastapi.exceptions import RequestValidationError
from app.api.routes.auth import router as auth_router
from app.api.routes.users import router as user_router
from app.api.routes.recipe import router as recipe_router
from app.api.routes.ingredient import router as ingredient_router
from app.api.routes.file_service_images import router as images_router
from app.api.routes.file_service_pdfs import router as pdfs_router
from app.api.routes.api_keys import router as api_keys_router
from app.api.routes.public import router as public_router
from app.core.limiter import limiter
from app.core.config import settings
from slowapi.middleware import SlowAPIMiddleware
from slowapi.errors import RateLimitExceeded


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Start-up phase:
    os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
    os.makedirs(settings.API_KEYS_DIR, exist_ok=True)

    yield # Runtime phase: FastAPI is fully running and serving requests
    
    # Shutdown Phase:
    # Cleanup code can be added here if needed


app = FastAPI(
    lifespan=lifespan,
    # docs_url="/docs",
    # openapi_url="/openapi.json",
)

app.state.limiter = limiter
app.add_middleware(SlowAPIMiddleware)

@app.exception_handler(RateLimitExceeded)
async def rate_limit_handler(request, exc):
    return {
        "detail": str(exc.detail),
        "status_code": 429,
    }

api_router = APIRouter(prefix="/api")
api_router.include_router(auth_router)
api_router.include_router(user_router)
api_router.include_router(recipe_router)
api_router.include_router(ingredient_router)
api_router.include_router(images_router)
api_router.include_router(pdfs_router)
api_router.include_router(api_keys_router)

app.include_router(api_router)

@app.get("/")
def hello():
    return {"message": "Hello voice-chef"}



public_app = FastAPI(
    title="Voice Chef Public API",
    docs_url="/docs",
    openapi_url="/openapi.json",
    redoc_url=None,
)

public_app.state.limiter = limiter
public_app.add_middleware(SlowAPIMiddleware)

app.mount("/api/public", public_app)
public_app.include_router(public_router)
