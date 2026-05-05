from fastapi import FastAPI

from app.api.routes.public import router as public_router

public_app = FastAPI(
    title="Voice Chef Public API",
    docs_url="/docs",
    openapi_url="/openapi.json",
    redoc_url=None,
)

public_app.include_router(public_router)
