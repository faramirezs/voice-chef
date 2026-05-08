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
from .sync import force_reindex, sync_collections
from .sync_state import state as sync_state

logger = logging.getLogger("voice-chef.rag")
logging.basicConfig(level=logging.INFO)

BACKEND_URL = os.getenv("BACKEND_URL", "http://backend:80")
QDRANT_URL = os.getenv("QDRANT_URL", "http://qdrant:6333")
EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "paraphrase-multilingual-mpnet-base-v2")
POLL_SECONDS = int(os.getenv("EMBEDDING_POLL_SECONDS", "30"))
INTERNAL_SECRET = os.getenv("INTERNAL_SECRET", "")

COLLECTIONS = ("recipes", "ingredients")


async def _has_compatible_schema(
    client: AsyncQdrantClient, name: str, expected_dim: int
) -> bool:
    """A collection is hybrid-compatible if it has named 'dense' + 'sparse'
    vectors AND the dense vector dimension matches the current embedding
    model. Mismatch on dim means the model has changed (different embedding
    space), in which case existing vectors are invalid and the collection
    must be rebuilt."""
    info = await client.get_collection(collection_name=name)
    vectors = info.config.params.vectors
    sparse = info.config.params.sparse_vectors or {}
    has_dense = isinstance(vectors, dict) and "dense" in vectors
    has_sparse = isinstance(sparse, dict) and "sparse" in sparse
    if not (has_dense and has_sparse):
        return False
    dense_params = vectors.get("dense") if isinstance(vectors, dict) else None
    actual_dim = getattr(dense_params, "size", None)
    if actual_dim != expected_dim:
        logger.warning(
            "collection '%s' has dim=%s but embedding model expects dim=%s — "
            "treating as incompatible, will rebuild",
            name,
            actual_dim,
            expected_dim,
        )
        return False
    return True


async def _create_collection(client: AsyncQdrantClient, name: str, dim: int) -> None:
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


async def ensure_collections(client: AsyncQdrantClient, dim: int) -> None:
    """Make sure each collection exists with the right schema. Drops +
    recreates anything that's incompatible (legacy single-vector schema OR
    different embedding dim — the latter catches embedding-model swaps)."""
    existing = {c.name for c in (await client.get_collections()).collections}
    for name in COLLECTIONS:
        if name in existing:
            if await _has_compatible_schema(client, name, dim):
                logger.info("collection '%s' has compatible schema; keeping", name)
                continue
            logger.warning(
                "collection '%s' incompatible; dropping for re-creation", name,
            )
            await client.delete_collection(collection_name=name)
        await _create_collection(client, name, dim)


async def _drop_and_recreate(
    client: AsyncQdrantClient, dim: int, names: list[str]
) -> None:
    """Drop the named collections (if present) and recreate them with the
    current schema. Used by sync.py during count-mismatch rebuilds and by
    the /reindex endpoint."""
    for name in names:
        try:
            await client.delete_collection(collection_name=name)
        except Exception as exc:
            logger.info("delete_collection(%s) — already absent: %s", name, exc)
        await _create_collection(client, name, dim)


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

    app.state.embedder = embedder
    app.state.sparse_embedder = sparse_embedder
    app.state.qdrant = qdrant
    app.state.dim = embedder.dim

    # Bind a closure that captures the qdrant client + dim so sync.py can
    # request a drop+recreate without knowing the schema details.
    async def drop_recreate(names: list[str]) -> None:
        await _drop_and_recreate(qdrant, embedder.dim, names)

    app.state.drop_recreate = drop_recreate

    # Run sync in the background so the service starts serving immediately.
    # While the sync runs, /search returns whatever is currently in qdrant
    # (empty on first boot, stale otherwise). Search responses include an
    # `indexing` flag so callers can surface that state to users.
    sync_task = asyncio.create_task(
        sync_collections(
            qdrant,
            embedder,
            sparse_embedder,
            BACKEND_URL,
            sync_state,
            drop_recreate,
        ),
        name="rag-startup-sync",
    )
    app.state.sync_task = sync_task

    yield

    if not sync_task.done():
        sync_task.cancel()
        try:
            await sync_task
        except (asyncio.CancelledError, Exception):
            pass
    await qdrant.close()


app = FastAPI(lifespan=lifespan)


@app.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok", "service": "rag"}


@app.get("/status")
async def status() -> dict[str, Any]:
    """Full sync/reindex progress snapshot. Light-tier consumers only need
    `indexing`; the rest (items_done, items_total, eta_seconds, phase) is
    here for a future Medium-tier UI banner that polls this endpoint."""
    return sync_state.snapshot()


def _require_internal_secret(request: Request) -> None:
    """Gate write/admin endpoints behind the same shared secret the agent
    uses to call backend. Without this, anyone reachable on the network
    could trigger a multi-minute reindex."""
    if not INTERNAL_SECRET:
        # No secret configured — allow (matches existing fail-open behaviour
        # in backend.deps._is_internal_request when INTERNAL_SECRET is empty).
        return
    if request.headers.get("X-Internal-Secret") != INTERNAL_SECRET:
        raise HTTPException(status_code=401, detail="internal secret required")


@app.post("/reindex")
async def reindex(request: Request) -> dict[str, Any]:
    """Drop both collections and re-embed from scratch. Returns
    immediately; the work runs in the background. Poll /status for
    progress. Concurrent calls are serialized via the sync lock — a
    second /reindex while the first is running blocks until the first
    finishes, then runs the second.

    Auth: requires X-Internal-Secret header matching the INTERNAL_SECRET
    env var. Used to keep the endpoint inaccessible to public clients
    even if eventually exposed through the nginx-proxy.
    """
    _require_internal_secret(request)
    # Run in background — this can take several minutes for a full corpus.
    asyncio.create_task(
        force_reindex(
            request.app.state.qdrant,
            request.app.state.embedder,
            request.app.state.sparse_embedder,
            BACKEND_URL,
            sync_state,
            request.app.state.drop_recreate,
        ),
        name="rag-force-reindex",
    )
    return {"status": "accepted", "snapshot": sync_state.snapshot()}


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
    # True while the index is rebuilding. Light-tier UX hint: callers (the
    # agent) read this and surface a "results may be incomplete" notice to
    # the user. Medium-tier consumers can call /status for the full
    # progress snapshot.
    indexing: bool = False


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
    return SearchResponse(query=text, items=items, indexing=sync_state.running)


@app.post("/search/recipes", response_model=SearchResponse)
async def search_recipes(req: SearchRequest, request: Request) -> SearchResponse:
    return await _search(request, "recipes", req)


@app.post("/search/ingredients", response_model=SearchResponse)
async def search_ingredients(req: SearchRequest, request: Request) -> SearchResponse:
    return await _search(request, "ingredients", req)
