import asyncio
import logging
import os
from contextlib import asynccontextmanager
from typing import Any, AsyncIterator

from fastapi import FastAPI, HTTPException, Request
from pydantic import BaseModel, Field
from qdrant_client import AsyncQdrantClient
from qdrant_client.http.models import (
    Distance,
    Fusion,
    FusionQuery,
    Modifier,
    Prefetch,
    SparseVectorParams,
    VectorParams,
)

from .embedder import Embedder
from .sparse_embedder import SparseEmbedder
from .sync import backfill_if_empty

logger = logging.getLogger("voice-chef.rag")
logging.basicConfig(level=logging.INFO)

BACKEND_URL = os.getenv("BACKEND_URL", "http://backend:80")
QDRANT_URL = os.getenv("QDRANT_URL", "http://qdrant:6333")
EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "paraphrase-multilingual-mpnet-base-v2")
POLL_SECONDS = int(os.getenv("EMBEDDING_POLL_SECONDS", "30"))

COLLECTIONS = ("recipes", "ingredients")


async def _has_hybrid_schema(client: AsyncQdrantClient, name: str) -> bool:
    """A collection is hybrid-ready if it has named 'dense' + 'sparse' vectors."""
    info = await client.get_collection(collection_name=name)
    vectors = info.config.params.vectors
    sparse = info.config.params.sparse_vectors or {}
    has_dense = isinstance(vectors, dict) and "dense" in vectors
    has_sparse = isinstance(sparse, dict) and "sparse" in sparse
    return has_dense and has_sparse


async def ensure_collections(client: AsyncQdrantClient, dim: int) -> None:
    existing = {c.name for c in (await client.get_collections()).collections}
    for name in COLLECTIONS:
        if name in existing:
            if await _has_hybrid_schema(client, name):
                logger.info("collection '%s' has hybrid schema; keeping", name)
                continue
            logger.warning(
                "collection '%s' has legacy schema; dropping for re-creation "
                "(backfill will re-embed)",
                name,
            )
            await client.delete_collection(collection_name=name)
        await client.create_collection(
            collection_name=name,
            vectors_config={
                "dense": VectorParams(size=dim, distance=Distance.COSINE),
            },
            sparse_vectors_config={
                "sparse": SparseVectorParams(modifier=Modifier.IDF),
            },
        )
        logger.info(
            "created qdrant collection: %s (dense %s-dim cosine + sparse BM25 IDF)",
            name,
            dim,
        )


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    logger.info("rag service starting")
    logger.info("BACKEND_URL=%s", BACKEND_URL)
    logger.info("QDRANT_URL=%s", QDRANT_URL)
    logger.info("EMBEDDING_MODEL=%s", EMBEDDING_MODEL)
    logger.info("POLL_SECONDS=%s", POLL_SECONDS)

    embedder = Embedder(EMBEDDING_MODEL)
    sparse_embedder = SparseEmbedder()
    qdrant = AsyncQdrantClient(url=QDRANT_URL)
    await ensure_collections(qdrant, embedder.dim)
    await backfill_if_empty(qdrant, embedder, sparse_embedder, BACKEND_URL)

    app.state.embedder = embedder
    app.state.sparse_embedder = sparse_embedder
    app.state.qdrant = qdrant

    yield

    await qdrant.close()


app = FastAPI(lifespan=lifespan)


@app.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok", "service": "rag"}


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
    sparse_embedder: SparseEmbedder = request.app.state.sparse_embedder
    qdrant: AsyncQdrantClient = request.app.state.qdrant

    dense_vec = await asyncio.to_thread(embedder.embed, text)
    sparse_vec = await asyncio.to_thread(sparse_embedder.embed, text)

    # Hybrid retrieval: dense (semantic) + sparse BM25 (keyword), fused via RRF.
    prefetch_limit = max(req.k * 5, 25)
    result = await qdrant.query_points(
        collection_name=collection,
        prefetch=[
            Prefetch(query=dense_vec, using="dense", limit=prefetch_limit),
            Prefetch(query=sparse_vec, using="sparse", limit=prefetch_limit),
        ],
        query=FusionQuery(fusion=Fusion.RRF),
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
