import asyncio
import logging
import os
from contextlib import asynccontextmanager
from typing import Any, AsyncIterator

from fastapi import FastAPI, HTTPException, Request
from pydantic import BaseModel, Field
from qdrant_client import AsyncQdrantClient
from qdrant_client.http.models import Distance, VectorParams

from .embedder import Embedder
from .sync import backfill_if_empty

logger = logging.getLogger("voice-chef.embedding-service")
logging.basicConfig(level=logging.INFO)

BACKEND_URL = os.getenv("BACKEND_URL", "http://backend:80")
QDRANT_URL = os.getenv("QDRANT_URL", "http://qdrant:6333")
EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "paraphrase-multilingual-mpnet-base-v2")
POLL_SECONDS = int(os.getenv("EMBEDDING_POLL_SECONDS", "30"))

COLLECTIONS = ("recipes", "ingredients")


async def ensure_collections(client: AsyncQdrantClient, dim: int) -> None:
    existing = {c.name for c in (await client.get_collections()).collections}
    for name in COLLECTIONS:
        if name in existing:
            logger.info("collection already present: %s", name)
            continue
        await client.create_collection(
            collection_name=name,
            vectors_config=VectorParams(size=dim, distance=Distance.COSINE),
        )
        logger.info("created qdrant collection: %s (cosine, %s-dim)", name, dim)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    logger.info("embedding-service starting")
    logger.info("BACKEND_URL=%s", BACKEND_URL)
    logger.info("QDRANT_URL=%s", QDRANT_URL)
    logger.info("EMBEDDING_MODEL=%s", EMBEDDING_MODEL)
    logger.info("POLL_SECONDS=%s", POLL_SECONDS)

    embedder = Embedder(EMBEDDING_MODEL)
    qdrant = AsyncQdrantClient(url=QDRANT_URL)
    await ensure_collections(qdrant, embedder.dim)
    await backfill_if_empty(qdrant, embedder, BACKEND_URL)

    app.state.embedder = embedder
    app.state.qdrant = qdrant

    yield

    await qdrant.close()


app = FastAPI(lifespan=lifespan)


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


# --- Search ----------------------------------------------------------------
# Tenant filtering note: a `tenant_id` parameter is accepted for forward
# compatibility but is currently a no-op. Two upstream blockers (tracked in
# docs/voiceNextSteps.md "Known issues"):
#   1. Backend API does not yet expose tenant_id on /api/recipes responses,
#      so the indexer can't tag vectors with tenant in their payloads.
#   2. JWT-based auth on these endpoints requires the agent-auth fix on main.
# Once both land: parse JWT → extract tenant_id → pass through Qdrant filter.


class SearchRequest(BaseModel):
    query: str = Field(..., description="Natural-language search query")
    k: int = Field(5, ge=1, le=50, description="Number of results to return")
    tenant_id: str | None = Field(
        None,
        description="Reserved for future tenant filtering (no-op today).",
    )


class SearchHit(BaseModel):
    id: str
    score: float
    payload: dict[str, Any]


class SearchResponse(BaseModel):
    query: str
    items: list[SearchHit]


async def _search(
    request: Request, collection: str, req: SearchRequest
) -> SearchResponse:
    text = req.query.strip()
    if not text:
        raise HTTPException(status_code=400, detail="query must not be empty")

    embedder: Embedder = request.app.state.embedder
    qdrant: AsyncQdrantClient = request.app.state.qdrant

    vector = await asyncio.to_thread(embedder.embed, text)
    result = await qdrant.query_points(
        collection_name=collection,
        query=vector,
        limit=req.k,
    )
    items = [
        SearchHit(
            id=str(p.id),
            score=float(p.score) if p.score is not None else 0.0,
            payload=dict(p.payload or {}),
        )
        for p in result.points
    ]
    return SearchResponse(query=text, items=items)


@app.post("/search/recipes", response_model=SearchResponse)
async def search_recipes(req: SearchRequest, request: Request) -> SearchResponse:
    return await _search(request, "recipes", req)


@app.post("/search/ingredients", response_model=SearchResponse)
async def search_ingredients(req: SearchRequest, request: Request) -> SearchResponse:
    return await _search(request, "ingredients", req)
