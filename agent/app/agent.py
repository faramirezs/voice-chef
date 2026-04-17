import os
import httpx
from typing import Any
from pydantic_ai import Agent
from pydantic_ai.models.openrouter import OpenRouterModel
from pydantic_ai.providers.openrouter import OpenRouterProvider

FASTAPI_URL = os.getenv("FASTAPI_INTERNAL_URL", "http://backend:80")

# Read model/provider settings from environment variables.
AGENT_MODEL = os.getenv("AGENT_MODEL")
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")

# Fail fast with a clear message if the model name is missing.
# This avoids starting a container with an ambiguous model config.
if not AGENT_MODEL:
    raise RuntimeError(
        "Missing AGENT_MODEL. Set it to an OpenRouter model id, "
        "for example: anthropic/claude-sonnet-4-5"
    )

# Fail fast if the OpenRouter API key is missing.
# This produces a direct startup error instead of a later runtime failure.
if not OPENROUTER_API_KEY:
    raise RuntimeError(
        "Missing OPENROUTER_API_KEY. Set it in your environment before "
        "starting the agent service."
    )


# Reuse a single HTTP client for all tool calls instead of opening a new
# TCP connection on every request. Much faster under load.
_http_client = httpx.AsyncClient()


model = OpenRouterModel(
    AGENT_MODEL,
    provider=OpenRouterProvider(api_key=OPENROUTER_API_KEY),
)

agent = Agent(
    model,
    system_prompt=(
        "You are Voice Chef, a culinary AI assistant for professional kitchen staff. "
        "You have access to the recipe database. Answer questions about recipes, "
        "cooking steps, ingredients, storage, plating, and kitchen operations. "
        "When a chef asks about a recipe, always look it up from the database first. "
        "Respond in a concise, action-oriented way suited for a busy kitchen environment."
    ),
)

# @agent.tool_plain registers a function as a tool the LLM can call.
# "plain" means it doesn't need access to the agent context or run state —
# it just takes arguments and returns a value.

@agent.tool_plain
async def get_recipes_list(query: str = "", limit: int = 20, offset: int = 0) -> dict[str, Any]:
    """Get recipes with pagination, optional filter by name.

    Args:
        query: Optional substring filter for recipe name.
        limit: Page size. Clamped to [1, 100].
        offset: Starting row index. Clamped to >= 0.
    """
    # Keep tool inputs aligned with backend contract.
    limit = max(1, min(limit, 100))
    offset = max(0, offset)

    try:
        resp = await _http_client.get(
            f"{FASTAPI_URL}/api/recipes",
            params={"limit": limit, "offset": offset},
            timeout=10,
        )
        resp.raise_for_status()
        payload = resp.json()
    except Exception as exc:
        return {
            "type": "error",
            "version": "1",
            "source": "get_recipes_list",
            "message": str(exc),
        }

    # Backend returns a paginated envelope: {items: [...], meta: {...}}.
    if isinstance(payload, dict):
        items = payload.get("items", [])
        meta = payload.get("meta", {})
    elif isinstance(payload, list):
        # Backward-safe fallback in case backend returns a raw list.
        items = payload
        meta = {"limit": limit, "offset": offset, "total": len(payload)}
    else:
        items = []
        meta = {"limit": limit, "offset": offset, "total": 0}

    if not isinstance(items, list):
        items = []
    if not isinstance(meta, dict):
        meta = {"limit": limit, "offset": offset, "total": len(items)}

    if not query:
        return {
            "type": "recipes.list",
            "version": "1",
            "items": items,
            "meta": meta,
        }

    query_lower = query.lower()
    filtered = [
        r for r in items
        if isinstance(r, dict)
        and query_lower in str(r.get("name", "")).lower()
    ]

    result_items = filtered or items
    result_meta = {
        "limit": len(result_items),
        "offset": 0,
        "total": len(result_items),
    }

    return {
        "type": "recipes.list",
        "version": "1",
        "items": result_items,
        "meta": result_meta,
        "query": query,
    }

@agent.tool_plain
async def get_recipe_detail(recipe_id: str) -> dict[str, Any]:
    """Get full details of a recipe by its UUID."""
    try:
        resp = await _http_client.get(f"{FASTAPI_URL}/api/recipes/{recipe_id}", timeout=10)
        resp.raise_for_status()
        payload = resp.json()
    except Exception as exc:
        return {
            "type": "error",
            "version": "1",
            "source": "get_recipe_detail",
            "message": str(exc),
        }

    return {
        "type": "recipe.detail",
        "version": "1",
        "item": payload,
    }
