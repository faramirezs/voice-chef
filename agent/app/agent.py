import os
import httpx
from typing import Any
from pydantic import BaseModel
from pydantic_ai import Agent
from pydantic_ai.models.openrouter import OpenRouterModel
from pydantic_ai.providers.openrouter import OpenRouterProvider
from ag_ui.core import EventType, StateSnapshotEvent, StateDeltaEvent

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
        "Respond in a concise, action-oriented way suited for a busy kitchen environment. "
        "You are a display controller, not a chat assistant. Never send free-form text responses. "
        "Always use render_component to show content. If you have nothing visual to show, "
        "respond with an empty TEXT_MESSAGE -- the UI has no text rendering target. "
        "UI rendering policy: when a tool returns a typed envelope like recipes.list, "
        "recipe.detail, or recipe.scaling, do not rewrite the tool data as markdown "
        "tables, long lists, or full recipe text. The UI renders detailed tool output "
        "as cards. After a successful typed tool result, do not send any additional "
        "assistant text. Return no follow-up sentence; the card is the full response. "
        "Do not call additional tools after a successful tool result unless the user "
        "explicitly asks for another lookup. In particular, after get_recipe_detail "
        "succeeds, do not call get_recipes_list again in the same run. "
        "When a chef asks to scale a recipe, edit portions, or adjust ingredient "
        "quantities, use get_recipe_for_scaling instead of get_recipe_detail. "
        "MANDATORY SCALING SEQUENCE: when scaling a recipe, you MUST call "
        "render_component(component='recipe_scaling', recipe_id=..., slot='sticky') "
        "BEFORE calling get_recipe_for_scaling. This places the scaling widget in "
        "the UI so the user sees it immediately. Never skip render_component. "
        "UI Component Rendering: render_component places a component in a layout slot. "
        "Available components: "
        "* 'placeholder' (any slot): test card. Args: message. "
        "* 'recipe_scaling' (sticky slot): scaling widget. Args: recipe_id. "
        "Slot guide: 'canvas' = primary content area (center), 'sticky' = pinned top bar, "
        "'chips' = bottom bar for transient actions, 'notifications' = top-right toasts, "
        "'overlay' = full-screen modal. "
        "After placing a component, STATE_SNAPSHOT from other tools will "
        "populate its state. Do not duplicate data in render_component args. "
    ),
)

# @agent.tool_plain registers a function as a tool the LLM can call.
# "plain" means it doesn't need access to the agent context or run state —
# it just takes arguments and returns a value.

@agent.tool_plain
async def get_recipes_list(query: str = "", limit: int = 20, offset: int = 0) -> dict[str, Any]:
    """Get recipes with pagination, optional filter by name.

    Returns a typed UI envelope for card rendering. The assistant should not
    restate returned fields as markdown tables or long recipe dumps.

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
    """Get full details of a recipe by its UUID.

    Use this whenever the user wants to open, inspect, or edit a single recipe.
    Do not guess fields yourself; always call this tool instead.
    Returns a typed UI envelope for card rendering. The assistant should not
    add any follow-up text after a successful typed tool result.
    """
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



# --- JSON Patch helper for STATE_DELTA events ---


class _PatchOp(BaseModel):
    op: str
    path: str
    value: Any = None


# --- render_component: flat-parameter tool ---

VALID_COMPONENTS = ("placeholder", "recipe_scaling")
VALID_SLOTS = ("canvas", "sticky", "chips", "notifications", "overlay")


@agent.tool_plain
async def render_component(
    component: str,
    slot: str = "canvas",
    message: str = "Slot active",
    recipe_id: str = "",
) -> dict[str, Any]:
    """Render a UI component in a layout slot.

    Call this before sending STATE_SNAPSHOT data. The slot will show a
    skeleton until state arrives.

    Components:
    - "placeholder" (any slot): test card. Pass 'message' for display text.
    - "recipe_scaling" (default slot: sticky): scaling widget. Pass 'recipe_id'.

    Slots: "canvas" = primary content area, "sticky" = pinned top bar,
    "chips" = bottom bar, "notifications" = top-right toasts,
    "overlay" = full-screen modal.
    """
    if component not in VALID_COMPONENTS:
        return {"type": "error", "version": "1", "message": f"Unknown component: {component}"}
    if slot not in VALID_SLOTS:
        return {"type": "error", "version": "1", "message": f"Unknown slot: {slot}"}

    # Validate component-specific requirements.
    if component == "recipe_scaling" and not recipe_id:
        return {"type": "error", "version": "1", "message": "recipe_id required for recipe_scaling"}

    payload: dict[str, Any] = {"component": component, "slot": slot}
    if component == "placeholder":
        payload["message"] = message
    elif component == "recipe_scaling":
        payload["recipe_id"] = recipe_id

    return {"type": "ui.render", "version": "1", **payload}

# --- Recipe scaling tools ---

@agent.tool_plain
async def get_recipe_for_scaling(recipe_id: str) -> StateSnapshotEvent:
    """Fetch a recipe with its ingredients for the scaling widget.

    Use this when the chef wants to scale a recipe, edit portions,
    or adjust ingredient quantities.

    IMPORTANT: always call render_component(component='recipe_scaling',
    recipe_id=recipe_id) BEFORE calling this tool, to place the scaling
    widget in the UI.
    """
    try:
        resp = await _http_client.get(
            f"{FASTAPI_URL}/api/recipes/{recipe_id}", timeout=10
        )
        resp.raise_for_status()
        payload = resp.json()
    except Exception as exc:
        # Return a minimal error snapshot so the UI can render it.
        return StateSnapshotEvent(
            type=EventType.STATE_SNAPSHOT,
            snapshot={
                "widget": "recipe.scaling",
                "version": "1",
                "error": str(exc),
            },
        )

    # Transform backend response into the widget state shape.
    portions = payload.get("portions_count_resolved")
    raw_weight = payload.get("total_raw_weight_grams")
    cooked_weight = payload.get("total_cooked_weight_grams")
    yield_mode = payload.get("yield_mode", "count")

    ingredients = []
    for ing in payload.get("ingredients", []):
        ingredients.append({
            "id": ing.get("id"),
            "name": ing.get("ingredient_name", ""),
            "quantity": float(ing["quantity"]) if ing.get("quantity") is not None else 0,
            "unit": ing.get("unit", ""),
            "originalQuantity": float(ing["quantity"]) if ing.get("quantity") is not None else 0,
        })

    snapshot = {
        "widget": "recipe.scaling",
        "version": "1",
        "recipeId": str(payload.get("id", recipe_id)),
        "recipeName": payload.get("name", ""),
        "original": {
            "portions": float(portions) if portions is not None else None,
            "totalRawWeight": float(raw_weight) if raw_weight is not None else None,
            "totalCookedWeight": float(cooked_weight) if cooked_weight is not None else None,
            "yieldMode": yield_mode,
        },
        "current": {
            "portions": float(portions) if portions is not None else None,
            "totalRawWeight": float(raw_weight) if raw_weight is not None else None,
            "totalCookedWeight": float(cooked_weight) if cooked_weight is not None else None,
        },
        "ingredients": ingredients,
        "suggestedFields": None,
        "isDirty": False,
    }

    return StateSnapshotEvent(
        type=EventType.STATE_SNAPSHOT,
        snapshot=snapshot,
    )


@agent.tool_plain
async def apply_recipe_changes(
    recipe_id: str,
    portions: float | None = None,
    total_raw_weight: float | None = None,
    total_cooked_weight: float | None = None,
    ingredients: list[dict[str, Any]] | None = None,
) -> StateDeltaEvent:
    """Apply scaled recipe changes to the database.

    Persists the updated portions, weights, and ingredient quantities via
    PUT /api/recipes/:id, then returns a STATE_DELTA confirming the clean state.
    """
    updates: dict[str, Any] = {}
    if portions is not None:
        updates["portions_count_resolved"] = portions
    if total_raw_weight is not None:
        updates["total_raw_weight_grams"] = total_raw_weight
    if total_cooked_weight is not None:
        updates["total_cooked_weight_grams"] = total_cooked_weight

    try:
        resp = await _http_client.put(
            f"{FASTAPI_URL}/api/recipes/{recipe_id}",
            json=updates,
            timeout=10,
        )
        resp.raise_for_status()
    except Exception as exc:
        return StateDeltaEvent(
            type=EventType.STATE_DELTA,
            delta=[
                _PatchOp(
                    op="replace",
                    path="/error",
                    value=f"Failed to save: {exc}",
                ).model_dump()
            ],
        )

    # Build delta that resets isDirty and updates original values.
    delta_ops: list[dict[str, Any]] = [
        _PatchOp(op="replace", path="/isDirty", value=False).model_dump()
    ]
    if portions is not None:
        delta_ops.append(
            _PatchOp(op="replace", path="/original/portions", value=portions).model_dump()
        )
    if total_raw_weight is not None:
        delta_ops.append(
            _PatchOp(op="replace", path="/original/totalRawWeight", value=total_raw_weight).model_dump()
        )
    if total_cooked_weight is not None:
        delta_ops.append(
            _PatchOp(op="replace", path="/original/totalCookedWeight", value=total_cooked_weight).model_dump()
        )
    if ingredients:
        for i, ing in enumerate(ingredients):
            delta_ops.append(
                _PatchOp(
                    op="replace",
                    path=f"/ingredients/{i}/originalQuantity",
                    value=ing.get("quantity"),
                ).model_dump()
            )

    return StateDeltaEvent(
        type=EventType.STATE_DELTA,
        delta=delta_ops,
    )


@agent.tool_plain
async def suggest_recipe_improvements(recipe_id: str) -> StateDeltaEvent:
    """Analyze a recipe and suggest improvements for missing or weak fields.

    Returns a STATE_DELTA patch with suggestedFields containing proposed values
    for description, instructions, or other empty/incomplete fields.
    """
    try:
        resp = await _http_client.get(
            f"{FASTAPI_URL}/api/recipes/{recipe_id}", timeout=10
        )
        resp.raise_for_status()
        payload = resp.json()
    except Exception as exc:
        return StateDeltaEvent(
            type=EventType.STATE_DELTA,
            delta=[
                _PatchOp(
                    op="replace",
                    path="/error",
                    value=f"Failed to fetch recipe: {exc}",
                ).model_dump()
            ],
        )

    # Identify missing/empty fields that could be improved.
    suggestions: dict[str, str] = {}
    if not payload.get("description") or len(str(payload.get("description", "")).strip()) < 20:
        suggestions["description"] = (
            "(AI suggestion pending — describe this recipe in 1-2 appealing sentences)"
        )
    if not payload.get("instructions") or len(str(payload.get("instructions", "")).strip()) < 20:
        suggestions["instructions"] = (
            "(AI suggestion pending — add step-by-step cooking instructions)"
        )

    return StateDeltaEvent(
        type=EventType.STATE_DELTA,
        delta=[
            _PatchOp(
                op="replace",
                path="/suggestedFields",
                value=suggestions if suggestions else None,
            ).model_dump()
        ],
    )