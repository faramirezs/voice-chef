import logging
import os
from contextlib import asynccontextmanager
from typing import AsyncIterator

from fastapi import FastAPI
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
