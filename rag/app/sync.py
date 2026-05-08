"""Backfill + sync: fetch recipes and ingredients from the backend, embed
them, and upsert into qdrant.

Two entry points:
- `sync_collections(...)` — called at startup. Per collection, compares the
  qdrant point count against the backend's total. Empty → full backfill.
  Match → skip. Mismatch → drop + recreate + full backfill (catches recipes
  added or deleted between container restarts).
- `force_reindex(...)` — called from POST /reindex. Drops everything and
  re-embeds from scratch regardless of state. Use after editing recipe
  content (which doesn't change the count, so sync_collections wouldn't
  detect it) or after switching the embedding model.

Polling-based incremental sync (catching mid-uptime edits without a manual
trigger) is a separate concern — see docs/voiceNextSteps.md Topic 3.
"""

import asyncio
import logging
import os
from typing import Any, Awaitable, Callable

import httpx
from qdrant_client import AsyncQdrantClient
from qdrant_client.http.models import PointStruct

from .embedder import Embedder
from .sparse_embedder import SparseEmbedder

logger = logging.getLogger("voice-chef.rag")

PAGE_SIZE = 100
EMBED_BATCH = 64

# Shared internal-service header. Backend's `_is_internal_request` recognises
# this and returns a synthetic admin user, bypassing user-level auth — needed
# because the rag service has no JWT to forward and is calling backend on its
# own behalf during indexing. Same pattern the agent uses; see
# backend/app/core/deps.py and agent/app/agent.py.
INTERNAL_SECRET = os.getenv("INTERNAL_SECRET", "")

# Backend list endpoints used for count-comparison. Order matters for log
# readability only.
_COUNT_ENDPOINTS: dict[str, str] = {
    "recipes": "/api/recipes",
    "ingredients": "/api/ingredients",
}

# Serialize concurrent sync/reindex calls. Without this, a startup sync and
# an admin-triggered /reindex could race and double-embed everything.
_sync_lock = asyncio.Lock()


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
    sparse_embedder: SparseEmbedder,
    collection: str,
    items: list[dict[str, Any]],
    text_fn: Callable[[dict[str, Any]], str],
    payload_fn: Callable[[dict[str, Any]], dict[str, Any]],
    progress_cb: Callable[[int], None] | None = None,
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
        dense_vecs = await asyncio.to_thread(embedder.embed_batch, texts)
        sparse_vecs = await asyncio.to_thread(sparse_embedder.embed_batch, texts)
        points = [
            PointStruct(
                id=c["id"],
                vector={"dense": dense, "sparse": sparse},
                payload=payload_fn(c),
            )
            for c, dense, sparse in zip(chunk, dense_vecs, sparse_vecs)
        ]
        await qdrant.upsert(collection_name=collection, points=points)
        upserted += len(points)
        if progress_cb is not None:
            progress_cb(upserted)
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
    sparse_embedder: SparseEmbedder,
    backend_url: str,
    progress_cb: Callable[[int], None] | None = None,
) -> int:
    summaries = await _fetch_paginated(http, f"{backend_url}/api/recipes")
    logger.info("fetched %s recipe summaries; hydrating with detail", len(summaries))
    detailed = await _hydrate_recipes(http, backend_url, summaries)
    return await _embed_and_upsert(
        qdrant, embedder, sparse_embedder, "recipes", detailed,
        _recipe_text, _recipe_payload, progress_cb=progress_cb,
    )


async def _backfill_ingredients(
    http: httpx.AsyncClient,
    qdrant: AsyncQdrantClient,
    embedder: Embedder,
    sparse_embedder: SparseEmbedder,
    backend_url: str,
    progress_cb: Callable[[int], None] | None = None,
) -> int:
    items = await _fetch_paginated(http, f"{backend_url}/api/ingredients")
    logger.info("fetched %s ingredients", len(items))
    return await _embed_and_upsert(
        qdrant, embedder, sparse_embedder, "ingredients", items,
        _ingredient_text, _ingredient_payload, progress_cb=progress_cb,
    )


_BACKFILLERS: dict[
    str,
    Callable[
        [
            httpx.AsyncClient,
            AsyncQdrantClient,
            Embedder,
            SparseEmbedder,
            str,
            Callable[[int], None] | None,
        ],
        Awaitable[int],
    ],
] = {
    "recipes": _backfill_recipes,
    "ingredients": _backfill_ingredients,
}


async def _get_backend_total(
    http: httpx.AsyncClient, backend_url: str, endpoint: str
) -> int | None:
    """Ask the backend how many entities exist for a given list endpoint.
    Returns None if the response shape doesn't carry a meta.total — caller
    must treat that as "unknown" and fall back to skip-if-non-empty."""
    try:
        r = await http.get(
            f"{backend_url}{endpoint}",
            params={"limit": 1, "offset": 0},
            timeout=30,
        )
        r.raise_for_status()
        data = r.json()
        if isinstance(data, dict):
            meta = data.get("meta") or {}
            total = meta.get("total")
            if isinstance(total, int):
                return total
        return None
    except Exception as exc:
        logger.warning("couldn't fetch backend total for %s: %s", endpoint, exc)
        return None


async def _run_backfill(
    http: httpx.AsyncClient,
    qdrant: AsyncQdrantClient,
    embedder: Embedder,
    sparse_embedder: SparseEmbedder,
    backend_url: str,
    name: str,
    expected_total: int | None,
    state: "_StateLike",
) -> int:
    """Run a single backfill function with progress accounting against the
    shared sync state. The state's items_done is incremented as batches
    upsert; items_total is set up-front when known so the UI can compute
    an ETA."""
    fn = _BACKFILLERS[name]
    if expected_total is not None:
        state.set_total(expected_total)
    state.phase = f"backfilling {name}"
    logger.info("starting backfill: %s (from %s)", name, backend_url)
    base_done = state.items_done

    def _cb(done_in_collection: int) -> None:
        state.progress(base_done + done_in_collection)

    count = await fn(http, qdrant, embedder, sparse_embedder, backend_url, _cb)
    logger.info("backfill complete: %s — %s points upserted", name, count)
    return count


# Type stub to keep us decoupled from sync_state.SyncState (avoids a
# cyclic import while still letting type-checkers help). Anything with
# the methods we call qualifies.
class _StateLike:
    items_done: int = 0
    phase: str | None = None
    def set_total(self, total: int) -> None: ...
    def progress(self, done: int) -> None: ...
    def start(self, phase: str | None = None) -> None: ...
    def finish(self, error: str | None = None) -> None: ...


async def sync_collections(
    qdrant: AsyncQdrantClient,
    embedder: Embedder,
    sparse_embedder: SparseEmbedder,
    backend_url: str,
    state: _StateLike,
    drop_and_recreate: Callable[[list[str]], Awaitable[None]],
) -> None:
    """Bring qdrant collections in line with the backend.

    For each collection:
    - empty in qdrant → full backfill
    - count matches backend → skip
    - count differs from backend → drop, recreate, full backfill

    `drop_and_recreate` is supplied by main.py and knows the embedding
    dimension; we keep it injected so sync.py stays free of qdrant
    schema details.
    """
    async with _sync_lock:
        state.start(phase="checking collections")
        try:
            headers = (
                {"X-Internal-Secret": INTERNAL_SECRET} if INTERNAL_SECRET else {}
            )
            async with httpx.AsyncClient(headers=headers) as http:
                # Pass 1: figure out which collections need rebuilding
                rebuild: list[tuple[str, int | None]] = []
                aggregate_total = 0
                for name in _BACKFILLERS:
                    existing = (
                        await qdrant.count(collection_name=name, exact=True)
                    ).count
                    endpoint = _COUNT_ENDPOINTS[name]
                    expected = await _get_backend_total(
                        http, backend_url, endpoint
                    )
                    if existing == 0:
                        logger.info(
                            "[%s] empty — full backfill needed (expected ≈%s)",
                            name,
                            expected if expected is not None else "?",
                        )
                        rebuild.append((name, expected))
                        if expected:
                            aggregate_total += expected
                        continue
                    if expected is None:
                        logger.info(
                            "[%s] %s points; backend total unknown — skipping",
                            name,
                            existing,
                        )
                        continue
                    if existing == expected:
                        logger.info(
                            "[%s] %s points match backend; skipping",
                            name,
                            existing,
                        )
                        continue
                    logger.warning(
                        "[%s] count mismatch: qdrant=%s backend=%s — full rebuild",
                        name,
                        existing,
                        expected,
                    )
                    rebuild.append((name, expected))
                    aggregate_total += expected

                if not rebuild:
                    logger.info("all collections in sync; nothing to do")
                    state.finish()
                    return

                # Drop + recreate the collections that need rebuilding.
                await drop_and_recreate([n for n, _ in rebuild])

                # Pass 2: backfill in order. items_done accumulates across
                # collections so the snapshot ETA is global, not per-coll.
                state.set_total(aggregate_total)
                for name, expected in rebuild:
                    await _run_backfill(
                        http,
                        qdrant,
                        embedder,
                        sparse_embedder,
                        backend_url,
                        name,
                        expected,
                        state,
                    )
            state.finish()
        except Exception as exc:
            logger.exception("sync_collections failed: %s", exc)
            state.finish(error=str(exc))


async def force_reindex(
    qdrant: AsyncQdrantClient,
    embedder: Embedder,
    sparse_embedder: SparseEmbedder,
    backend_url: str,
    state: _StateLike,
    drop_and_recreate: Callable[[list[str]], Awaitable[None]],
) -> None:
    """Drop both collections and re-embed from scratch.

    Use after editing recipe content (which doesn't change the count, so
    sync_collections wouldn't notice) or after switching the embedding
    model. Concurrent calls are serialized via the sync lock.
    """
    async with _sync_lock:
        state.start(phase="full reindex")
        try:
            headers = (
                {"X-Internal-Secret": INTERNAL_SECRET} if INTERNAL_SECRET else {}
            )
            async with httpx.AsyncClient(headers=headers) as http:
                # Sum expected totals so the ETA is global.
                aggregate_total = 0
                expected_per: dict[str, int | None] = {}
                for name in _BACKFILLERS:
                    expected = await _get_backend_total(
                        http, backend_url, _COUNT_ENDPOINTS[name]
                    )
                    expected_per[name] = expected
                    if expected:
                        aggregate_total += expected
                state.set_total(aggregate_total)

                await drop_and_recreate(list(_BACKFILLERS.keys()))

                for name in _BACKFILLERS:
                    await _run_backfill(
                        http,
                        qdrant,
                        embedder,
                        sparse_embedder,
                        backend_url,
                        name,
                        expected_per[name],
                        state,
                    )
            state.finish()
        except Exception as exc:
            logger.exception("force_reindex failed: %s", exc)
            state.finish(error=str(exc))
