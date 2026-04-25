import os
import httpx
from typing import Any
from pydantic import BaseModel
from pydantic_ai import Agent
from pydantic_ai.models.openrouter import OpenRouterModel
from pydantic_ai.providers.openrouter import OpenRouterProvider
from ag_ui.core import EventType, StateSnapshotEvent, StateDeltaEvent

FASTAPI_URL = os.getenv("FASTAPI_INTERNAL_URL", "http://backend:80")

AGENT_MODEL = os.getenv("AGENT_MODEL")
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")

if not AGENT_MODEL:
    raise RuntimeError(
        "Missing AGENT_MODEL. Set it to an OpenRouter model id, "
        "for example: anthropic/claude-sonnet-4-5"
    )

if not OPENROUTER_API_KEY:
    raise RuntimeError(
        "Missing OPENROUTER_API_KEY. Set it in your environment before "
        "starting the agent service."
    )

_http_client = httpx.AsyncClient()

model = OpenRouterModel(
    AGENT_MODEL,
    provider=OpenRouterProvider(api_key=OPENROUTER_API_KEY),
)

agent = Agent(
    model,
    system_prompt="""\
You are Voice Chef, the display controller for a professional kitchen management system.
You operate exclusively through UI components -- never through free-form text.
Your job is to interpret chef commands and render the right component in the right slot.

RECIPE DISPLAY RULE:
To show a recipe, call get_recipe_detail(recipe_id). This single tool both fetches
the recipe data AND renders the recipe card in the canvas. Do NOT call render_component
separately -- the card appears automatically. Never respond with markdown tables,
lists, or rewritten recipe text. If the user provides a recipe name, call get_recipes_list
first to find the ID, then call get_recipe_detail with that ID.

UI RENDERING POLICY:
When a tool returns a typed envelope like recipes.list or recipe.scaling, do not
rewrite the tool data as markdown tables, long lists, or full recipe text. The UI
renders detailed tool output as cards. After a successful typed tool result, do not
send any additional assistant text. Return no follow-up sentence; the card is the
full response. Do not call additional tools after a successful tool result unless
the user explicitly asks for another lookup. In particular, after get_recipe_detail
succeeds, do not call get_recipes_list again in the same run.

SCALING RULE:
When a chef asks to scale a recipe, edit portions, or adjust ingredient quantities:
1. Call get_recipe_detail(recipe_id) to show the recipe card in the canvas.
2. Call get_recipe_for_scaling(recipe_id) to enable the scaling editor.
Never skip step 1 -- the card must be visible before scaling data arrives.

COMPONENT GUIDE:
* 'placeholder' (any slot): test card. Args: message.
* 'recipe_detail' (canvas slot): unified recipe card with detail + scaling. Args: recipe_id.
* 'confirmation_chips' (chips slot): action buttons. Args: actions.
* 'notification' (notifications slot): toast. Args: message, level, duration.

SLOT GUIDE:
'canvas' = primary content area (center)
'sticky' = pinned top bar
'chips' = bottom bar for transient actions
'notifications' = top-right toasts
'overlay' = full-screen modal

After placing a component, STATE_SNAPSHOT from other tools will populate its state.
Do not duplicate data in render_component args.

TRANSIENT UI TOOLS:
* show_notification(message, level='info', duration=5000): show auto-dismiss toast.
  Levels: info, success, warning, error.
* show_chip(actions=[{label, message, variant?}]): show action buttons in chips bar.
  Each action sends its message back to you when clicked.
* clear_slot(slot): remove content from a slot.

Use show_notification for status updates (saved, errors, completion confirmations).
Use show_chip when you need explicit user confirmation before an action.

ERROR & EMPTY STATE HANDLING:
If get_recipes_list returns 0 results, call show_notification with level='warning'
and suggest the user try a different search term or browse all recipes.
If get_recipe_detail returns a 404 or other error, call show_notification with
level='error' and clear_slot('canvas') to remove any stale content.
Never fall back to free-form text responses on errors.

LANGUAGE:
Ingredient names in the database may be in German or other languages.
Render them exactly as stored -- do not translate ingredient names.
""",
)


@agent.tool_plain
async def get_recipes_list(query: str = "", limit: int = 20, offset: int = 0) -> dict[str, Any]:
    """Get recipes with pagination, optional filter by name.

    Returns a typed UI envelope for card rendering. The assistant should not
    restate returned fields as markdown tables or long recipe dumps.

    Args:
        query: Optional substring filter for recipe name (case-insensitive, server-side).
        limit: Page size. Clamped to [1, 100].
        offset: Starting row index. Clamped to >= 0.
    """
    limit = max(1, min(limit, 100))
    offset = max(0, offset)

    params: dict[str, Any] = {"limit": limit, "offset": offset}
    if query:
        params["query"] = query

    try:
        resp = await _http_client.get(
            f"{FASTAPI_URL}/api/recipes",
            params=params,
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

    items: list[Any] = []
    meta: dict[str, Any] = {"limit": limit, "offset": offset, "total": 0}

    if isinstance(payload, dict):
        items = payload.get("items", [])
        meta = payload.get("meta", meta)
    elif isinstance(payload, list):
        items = payload
        meta = {"limit": limit, "offset": offset, "total": len(payload)}

    if not isinstance(items, list):
        items = []
    if not isinstance(meta, dict):
        meta = {"limit": limit, "offset": offset, "total": len(items)}

    envelope: dict[str, Any] = {
        "type": "recipes.list",
        "version": "1",
        "items": items,
        "meta": meta,
    }
    if query:
        envelope["query"] = query

    return envelope


@agent.tool_plain
async def get_recipe_detail(recipe_id: str) -> dict[str, Any]:
    """Fetch a recipe by its UUID and render the recipe card in the canvas.

    This tool both fetches the full recipe data AND places the recipe card
    in the canvas slot. The assistant should not call render_component
    separately after this tool -- the card is rendered automatically.

    Use this whenever the user wants to open, inspect, or edit a single recipe.
    Do not guess fields yourself; always call this tool instead.
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
        "type": "ui.render",
        "version": "1",
        "component": "recipe_detail",
        "slot": "canvas",
        "recipe": payload,
    }


VALID_COMPONENTS = ("placeholder", "recipe_detail", "confirmation_chips", "notification")
VALID_SLOTS = ("canvas", "sticky", "chips", "notifications", "overlay")


@agent.tool_plain
async def render_component(
    component: str,
    slot: str = "canvas",
    message: str = "Slot active",
    recipe_id: str = "",
    actions: list[dict[str, str]] | None = None,
    level: str = "info",
    duration: int = 5000,
) -> dict[str, Any]:
    """Render a UI component in a layout slot.

    Call this before sending STATE_SNAPSHOT data. The slot will show a
    skeleton until state arrives.

    Components:
    - "placeholder" (any slot): test card. Pass 'message' for display text.
    - "recipe_detail" (canvas slot): unified recipe card. Pass 'recipe_id'.
    - "confirmation_chips" (chips slot): action buttons. Pass 'actions'.
    - "notification" (notifications slot): toast message. Pass 'message', 'level'.

    Slots: "canvas" = primary content area, "sticky" = pinned top bar,
    "chips" = bottom bar, "notifications" = top-right toasts,
    "overlay" = full-screen modal.
    """
    if component not in VALID_COMPONENTS:
        return {"type": "error", "version": "1", "message": f"Unknown component: {component}"}
    if slot not in VALID_SLOTS:
        return {"type": "error", "version": "1", "message": f"Unknown slot: {slot}"}

    if component == "recipe_detail" and not recipe_id:
        return {"type": "error", "version": "1", "message": "recipe_id required for recipe_detail"}
    if component == "confirmation_chips" and not actions:
        return {"type": "error", "version": "1", "message": "actions required for confirmation_chips"}

    payload: dict[str, Any] = {"component": component, "slot": slot}
    if component == "placeholder":
        payload["message"] = message
    elif component == "recipe_detail":
        payload["recipe_id"] = recipe_id
    elif component == "confirmation_chips":
        payload["actions"] = actions
    elif component == "notification":
        payload["message"] = message
        payload["level"] = level
        payload["duration"] = duration

    return {"type": "ui.render", "version": "1", **payload}


@agent.tool_plain
async def show_notification(
    message: str,
    level: str = "info",
    duration: int = 5000,
) -> dict[str, Any]:
    """Show a transient toast notification.

    Levels: "info", "success", "warning", "error".
    Duration is in milliseconds (default 5000).
    """
    return await render_component(
        component="notification",
        slot="notifications",
        message=message,
        level=level,
        duration=duration,
    )


@agent.tool_plain
async def show_chip(
    actions: list[dict[str, str]],
) -> dict[str, Any]:
    """Show action confirmation buttons in the chips bar.

    Each action has: label (button text), message (sent to agent on click).
    Optional: variant ("default" | "ghost" | "destructive").

    Example: [{"label": "Apply", "message": "confirm apply scaling", "variant": "default"}]
    """
    return await render_component(
        component="confirmation_chips",
        slot="chips",
        actions=actions,
    )


@agent.tool_plain
async def clear_slot(slot: str) -> dict[str, Any]:
    """Clear a UI slot, removing its rendered component.

    Use this to dismiss chips, notifications, or canvas content.
    Slots: "canvas", "sticky", "chips", "notifications", "overlay".
    """
    if slot not in VALID_SLOTS:
        return {"type": "error", "version": "1", "message": f"Unknown slot: {slot}"}
    return {"type": "ui.clear", "version": "1", "slot": slot}


class _PatchOp(BaseModel):
    op: str
    path: str
    value: Any = None


@agent.tool_plain
async def get_recipe_for_scaling(recipe_id: str) -> StateSnapshotEvent:
    """Fetch a recipe with its ingredients for the scaling widget.

    Use this when the chef wants to scale a recipe, edit portions,
    or adjust ingredient quantities.

    IMPORTANT: always call get_recipe_detail(recipe_id) BEFORE calling this
    tool, to place the recipe card in the UI.
    """
    try:
        resp = await _http_client.get(
            f"{FASTAPI_URL}/api/recipes/{recipe_id}", timeout=10
        )
        resp.raise_for_status()
        payload = resp.json()
    except Exception as exc:
        return StateSnapshotEvent(
            type=EventType.STATE_SNAPSHOT,
            snapshot={
                "widget": "recipe.scaling",
                "version": "1",
                "error": str(exc),
            },
        )

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

    suggestions: dict[str, str] = {}
    if not payload.get("description") or len(str(payload.get("description", "")).strip()) < 20:
        suggestions["description"] = (
            "(AI suggestion pending -- describe this recipe in 1-2 appealing sentences)"
        )
    if not payload.get("instructions") or len(str(payload.get("instructions", "")).strip()) < 20:
        suggestions["instructions"] = (
            "(AI suggestion pending -- add step-by-step cooking instructions)"
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
