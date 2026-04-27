"""Initial backfill: fetch all recipes and ingredients from the backend,
embed them, and upsert into qdrant. Runs once at startup if collections
are empty. Polling-based incremental sync is a separate concern (next
iteration).
"""

import asyncio
import logging
from typing import Any, Awaitable, Callable

import httpx
from qdrant_client import AsyncQdrantClient
from qdrant_client.http.models import PointStruct

from .embedder import Embedder

logger = logging.getLogger("voice-chef.embedding-service")

PAGE_SIZE = 100
EMBED_BATCH = 64


def _recipe_text(recipe: dict[str, Any]) -> str:
    parts: list[str] = [
        str(recipe.get("name") or ""),
        str(recipe.get("description") or ""),
        str(recipe.get("instructions") or ""),
        str(recipe.get("notes") or ""),
    ]
    ing_names: list[str] = []
    for ing in recipe.get("ingredients") or []:
        if not isinstance(ing, dict):
            continue
        name = ing.get("name") or ing.get("ingredient_name")
        nested = ing.get("ingredient") if isinstance(ing.get("ingredient"), dict) else None
        if not name and nested:
            name = nested.get("name")
        if name:
            ing_names.append(str(name))
    if ing_names:
        parts.append(" ".join(ing_names))
    return "\n".join(p for p in parts if p)


def _ingredient_text(ing: dict[str, Any]) -> str:
    parts: list[str] = [
        str(ing.get("name") or ""),
        str(ing.get("name_english") or ""),
        str(ing.get("source") or ""),
        str(ing.get("notes") or ""),
    ]
    return "\n".join(p for p in parts if p)


def _recipe_payload(recipe: dict[str, Any]) -> dict[str, Any]:
    return {
        "id": recipe.get("id"),
        "name": recipe.get("name"),
        "status": recipe.get("status"),
        "yield_unit": recipe.get("yield_unit"),
        "preparation_time_minutes": recipe.get("preparation_time_minutes"),
        "updated_at": recipe.get("updated_at"),
    }


def _ingredient_payload(ing: dict[str, Any]) -> dict[str, Any]:
    return {
        "id": ing.get("id"),
        "name": ing.get("name"),
        "name_english": ing.get("name_english"),
        "bls_key": ing.get("bls_key"),
        "is_custom": ing.get("is_custom"),
        "updated_at": ing.get("updated_at"),
    }


async def _fetch_paginated(http: httpx.AsyncClient, url: str) -> list[dict[str, Any]]:
    items: list[dict[str, Any]] = []
    offset = 0
    while True:
        r = await http.get(
            url, params={"limit": PAGE_SIZE, "offset": offset}, timeout=30
        )
        r.raise_for_status()
        payload = r.json()
        page: list[Any]
        if isinstance(payload, dict):
            page = payload.get("items", []) or []
        elif isinstance(payload, list):
            page = payload
        else:
            page = []
        page_dicts = [p for p in page if isinstance(p, dict)]
        if not page_dicts:
            break
        items.extend(page_dicts)
        if len(page_dicts) < PAGE_SIZE:
            break
        offset += PAGE_SIZE
    return items


async def _embed_and_upsert(
    qdrant: AsyncQdrantClient,
    embedder: Embedder,
    collection: str,
    items: list[dict[str, Any]],
    text_fn: Callable[[dict[str, Any]], str],
    payload_fn: Callable[[dict[str, Any]], dict[str, Any]],
) -> int:
    upserted = 0
    total = len(items)
    for i in range(0, total, EMBED_BATCH):
        chunk = items[i : i + EMBED_BATCH]
        # Skip items missing an id; qdrant requires one per point.
        chunk = [c for c in chunk if c.get("id")]
        if not chunk:
            continue
        texts = [text_fn(c) for c in chunk]
        # Embedding is CPU-bound; offload from event loop.
        vectors = await asyncio.to_thread(embedder.embed_batch, texts)
        points = [
            PointStruct(id=c["id"], vector=vec, payload=payload_fn(c))
            for c, vec in zip(chunk, vectors)
        ]
        await qdrant.upsert(collection_name=collection, points=points)
        upserted += len(points)
        logger.info(
            "[%s] embedded+upserted %s/%s", collection, upserted, total
        )
    return upserted


async def _hydrate_recipes(
    http: httpx.AsyncClient, backend_url: str, summaries: list[dict[str, Any]]
) -> list[dict[str, Any]]:
    detailed: list[dict[str, Any]] = []
    for s in summaries:
        rid = s.get("id")
        if not rid:
            continue
        try:
            r = await http.get(f"{backend_url}/api/recipes/{rid}", timeout=30)
            r.raise_for_status()
            data = r.json()
            if isinstance(data, dict):
                detailed.append(data)
        except Exception as exc:
            logger.warning("failed to fetch recipe %s detail: %s", rid, exc)
    return detailed


async def _backfill_recipes(
    http: httpx.AsyncClient,
    qdrant: AsyncQdrantClient,
    embedder: Embedder,
    backend_url: str,
) -> int:
    summaries = await _fetch_paginated(http, f"{backend_url}/api/recipes")
    logger.info("fetched %s recipe summaries; hydrating with detail", len(summaries))
    detailed = await _hydrate_recipes(http, backend_url, summaries)
    return await _embed_and_upsert(
        qdrant, embedder, "recipes", detailed, _recipe_text, _recipe_payload
    )


async def _backfill_ingredients(
    http: httpx.AsyncClient,
    qdrant: AsyncQdrantClient,
    embedder: Embedder,
    backend_url: str,
) -> int:
    items = await _fetch_paginated(http, f"{backend_url}/api/ingredient")
    logger.info("fetched %s ingredients", len(items))
    return await _embed_and_upsert(
        qdrant, embedder, "ingredients", items, _ingredient_text, _ingredient_payload
    )


_BACKFILLERS: dict[str, Callable[[httpx.AsyncClient, AsyncQdrantClient, Embedder, str], Awaitable[int]]] = {
    "recipes": _backfill_recipes,
    "ingredients": _backfill_ingredients,
}


async def backfill_if_empty(
    qdrant: AsyncQdrantClient, embedder: Embedder, backend_url: str
) -> None:
    """Backfill any collection that currently has zero points.

    Idempotent: collections that already have data are skipped — the
    polling-based incremental sync (next iteration) keeps them fresh.
    """
    async with httpx.AsyncClient() as http:
        for name, fn in _BACKFILLERS.items():
            existing = (await qdrant.count(collection_name=name, exact=True)).count
            if existing > 0:
                logger.info(
                    "collection '%s' already has %s points; skipping backfill",
                    name,
                    existing,
                )
                continue
            logger.info("starting backfill: %s (from %s)", name, backend_url)
            count = await fn(http, qdrant, embedder, backend_url)
            logger.info("backfill complete: %s — %s points upserted", name, count)
