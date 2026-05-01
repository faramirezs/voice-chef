import os
import httpx
import logging
from typing import Any
from pydantic import BaseModel
from pydantic_ai import Agent, RunContext, ToolReturn
from pydantic_ai.models.openai import OpenAIModel
from pydantic_ai.ui import StateDeps
from ag_ui.core import CustomEvent, EventType, StateSnapshotEvent, StateDeltaEvent
from .state import KitchenState
from .context import get_auth_headers, mark_notification_shown

logger = logging.getLogger("voice-chef.agent")

_BACKEND_URL = os.getenv("FASTAPI_INTERNAL_URL", "http://backend:80")
FASTAPI_URL = f"{_BACKEND_URL}/api"

_RAG_URL = os.getenv("RAG_SERVICE_URL", "http://rag:8003")
SEARCH_MIN_SCORE = float(os.getenv("SEARCH_MIN_SCORE", "0.45"))

AGENT_MODEL = os.getenv("AGENT_MODEL", "meta/llama-3.3-70b-instruct")

AGENT_PROVIDER = os.getenv("AGENT_PROVIDER", "nvidia").lower()
PROVIDER_DEFAULT_BASE_URLS = {
    "nvidia": "https://integrate.api.nvidia.com/v1",
    "openrouter": "https://openrouter.ai/api/v1",
    "openai": "https://api.openai.com/v1",
}

if AGENT_PROVIDER not in PROVIDER_DEFAULT_BASE_URLS:
    raise RuntimeError(
        "Invalid AGENT_PROVIDER. Supported values: nvidia, openrouter, openai."
    )

AGENT_BASE_URL = os.getenv("AGENT_BASE_URL") or PROVIDER_DEFAULT_BASE_URLS[AGENT_PROVIDER]

# Preferred key is AGENT_API_KEY; provider-specific keys are backward-compatible fallbacks.
AGENT_API_KEY = os.getenv("AGENT_API_KEY")
if not AGENT_API_KEY:
    provider_key_env = {
        "nvidia": "NVIDIA_API_KEY",
        "openrouter": "OPENROUTER_API_KEY",
        "openai": "OPENAI_API_KEY",
    }[AGENT_PROVIDER]
    AGENT_API_KEY = os.getenv(provider_key_env)

if not AGENT_API_KEY:
    raise RuntimeError(
        "Missing API key. Set AGENT_API_KEY or the provider-specific key "
        f"for '{AGENT_PROVIDER}' in your environment."
    )

# Set OpenAI-compatible env vars so OpenAIModel picks them up automatically.
os.environ["OPENAI_BASE_URL"] = AGENT_BASE_URL
os.environ["OPENAI_API_KEY"] = AGENT_API_KEY

model = OpenAIModel(AGENT_MODEL)

def _backend_headers() -> dict[str, str]:
    """Return headers with forwarded auth from the frontend request."""
    return get_auth_headers()


_http_client = httpx.AsyncClient()
SYSTEM_PROMPT = """\
You are Voice Chef, the display controller for a professional kitchen management system.
You operate exclusively through UI components -- never through free-form text.
Your job is to interpret chef commands and render the right component in the right slot.

RECIPE DISPLAY RULE:
To show a recipe, call get_recipe_detail(recipe_id) recipe_id: UUID format only (e.g. "bd3083b9-10ca-557b-9428-88bb6c9f6733").
NEVER pass a recipe name, slug, or any other string as recipe_id. This single tool both fetches
the recipe data AND renders the recipe card in the canvas. Do NOT call render_component
separately -- the card appears automatically. Never respond with markdown tables,
lists, or rewritten recipe text. If the user provides a recipe name, call get_recipes_list
first to find the ID (UUID format only), then call get_recipe_detail with that ID.

If get_recipe_detail returns ANY error → call show_notification(level: "error").
STOP. Do not generate text. Do not try get_recipes_list as a fallback.

Do not send any additional assistant text after a typed tool result.

UI RENDERING POLICY:
When a tool returns a typed envelope like recipes.list or recipe.scaling, do not
rewrite the tool data as markdown tables, long lists, or full recipe text. The UI
renders detailed tool output as cards. After a successful typed tool result, do not
send any additional assistant text. Return no follow-up sentence; the card is the
full response. Do not call additional tools after a successful tool result unless
the user explicitly asks for another lookup. In particular, after get_recipe_detail
succeeds, do not call get_recipes_list again in the same run.

Example: User: "show chimichurri"
→ get_recipes_list(query="chimichurri") → extract id
→ get_recipe_detail(recipe_id=<uuid>) → ui.render fires
→ NO TEXT RESPONSE. The card is the answer.

SEMANTIC SEARCH RULES:
For descriptive, fuzzy, or multilingual queries:
- search_recipes(query, k=5): semantic recipe search. Returns a recipes.list
  envelope; the card renders automatically. Stay silent after.
- search_ingredients(query, k=10): ingredient knowledge. Returns plain data
  for your reasoning — call show_notification(level: "info") with a brief
  summary based on the items. Do NOT recommend recipes from ingredient
  results; ingredients alone don't render as recipe cards.

When to use which:
- search_recipes: ANY question phrasing ("do you have", "show me",
  "what's a"), fuzzy descriptions ("something with chickpeas", "creamy
  soup", "spicy"), multilingual or transliterated queries ("vegane
  Hauptspeise", "tajine recipe", "haehnchen recipe")
- get_recipes_list: ONLY when the user gives a literal exact recipe
  name verbatim (e.g., "Chimichurri")
- get_recipe_detail: ONLY for known UUIDs
When in doubt between search_recipes and get_recipes_list, prefer search_recipes.

VERIFY SEMANTIC MATCH (after search_recipes returns a recipes.list):
Before acting on the result, judge whether the top recipe's name plausibly
relates to what the user asked for. The score threshold is permissive on
purpose; YOU make the relevance call.

- Match (related): call get_recipe_detail(<top recipe id>) ONLY, then STOP.
  That single tool both fetches and renders. Make NO other tool calls
  afterward — no show_notification, no render_component, no follow-up
  search. The recipe card is the full answer.
  Examples:
    "chickpeas"  → "Hummus Bowl"          → match (hummus IS chickpeas)
    "spicy"      → "Chili Soße"           → match
    "soup"       → "Köttbullar Rahmsauce" → match (rahmsauce is creamy)

- Mismatch: call show_notification(level: "info", message: "No recipe
  found for <query>.") and STOP. Make no further tool calls of any kind
  in this run. Do NOT call show_notification again. Do NOT call
  get_recipe_detail. Do NOT call search_recipes again with the same
  query.
  Examples:
    "borscht" → "Roasted Cauliflower"   → mismatch (unrelated dishes)
    "lasagna" → "Hummus Bowl"            → mismatch
    "cake"    → "Stir fried Five-Spices" → mismatch

When unsure, prefer mismatch. An honest "no match" is better than
confidently recommending the wrong recipe.

If a search tool returns an error envelope (no strong match found):
- DO NOT retry the same query — the search already failed for it.
- DO NOT call get_recipes_list as a fallback.
- Call show_notification(level: "info") explaining no match was found.
- Then STOP. Do not call additional tools in this run.

Do NOT invent recipes or recommend irrelevant items.

SCALING RULE:
When a chef asks to scale a recipe, edit portions, or adjust ingredient quantities:

STEP 1 — Identify the target recipe_id:
  a. If the chef names a recipe AND it differs from the currently selected recipe
     (or snapshot.recipeId is empty):
       → Call get_recipes_list(query=<name>) to find its UUID.
       → Call get_recipe_detail(recipe_id) to render the card in the canvas.
  b. If the chef says "this", "that", "it", or names the already-selected recipe:
       → Use snapshot.recipeId directly. Do NOT call get_recipes_list or get_recipe_detail.
         The card is already visible.
  c. If no recipe can be identified from either the request or state:
       → Ask the chef which recipe they want to scale.

STEP 2 — Activate the scaling editor:
  Call scale_recipe(recipe_id, target_portions).
  Compute target from the chef's words:
    "double" = original*2, "triple" = original*3,
    "halve" = original/2, "scale to 20" = 20.
  After one successful call, STOP. Confirm to the user. Do not call scale_recipe again.

STEP 3 — Apply changes:
  When the chef confirms "apply", call apply_recipe_changes with the final values.

ADDITIONAL RULES:
- NEVER pass an empty string as recipe_id to scale_recipe.
- isDirty in STATE_SNAPSHOT means the widget has unsaved UI changes.
  It does NOT mean your last scale_recipe call failed. Do not retry on isDirty alone.
- Never skip STEP 1a's get_recipe_detail when loading a new recipe —
  the card must be visible in the canvas before scaling data arrives.

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
If get_recipes_list returns 0 results → call show_notification(level='warning') and STOP.
If get_recipes_list returns ANY error → call show_notification(level='error') and STOP.
If get_recipe_detail returns ANY error → call show_notification(level='error'),
  call clear_slot('canvas'), and STOP.
Do not call any further tools after show_notification. Do not generate text. STOP means STOP.
Never fall back to free-form text responses on errors.
If a tool result contains the word STOP, obey it immediately. Do not reason about it. Just stop.

LANGUAGE:
Ingredient names in the database may be in German or other languages.
Render them exactly as stored -- do not translate ingredient names.

RESPONSE FORMAT:
After any tool call completes, output NOTHING. No explanatory text, no summaries,
no "I have done X". Silence is the correct response after a tool result.
The only exception is if the user asks a direct question that no tool can answer.
"""

agent = Agent(
    model,
    system_prompt=SYSTEM_PROMPT,
    deps_type=StateDeps[KitchenState],
)


@agent.instructions
def state_instructions(ctx: RunContext[StateDeps[KitchenState]]) -> str:
    """Inject current frontend state into the LLM's context.

    AGUIAdapter validates the request body state into ctx.deps.state before
    the agent runs. This instruction makes that state visible to the LLM so
    it can make intelligent tool calls without guessing.
    """
    state = ctx.deps.state
    selected = state.selected_recipe
    scaling = state.scaling

    lines = ["CURRENT STATE:"]
    if selected:
        lines.append(
            f'- View: "{state.view}"'
        )
        lines.append(
            f'- Selected recipe: "{selected.name}" (id: {selected.id}, portions: {selected.portions or "unknown"}, yield_mode: {selected.yield_mode})'
        )
    else:
        lines.append(f'- View: "{state.view}"')
        lines.append("- No recipe selected")

    if scaling and scaling.target_portions is not None:
        lines.append(f"- Scaling: target_portions={scaling.target_portions}, is_dirty={scaling.is_dirty}")

    if state.last_action:
        lines.append(f"- Last action: {state.last_action.type}")

    return "\n".join(lines)


@agent.tool
async def get_recipes_list(
    ctx: RunContext[StateDeps[KitchenState]],
    query: str = "",
    limit: int = 20,
    offset: int = 0,
) -> dict[str, Any]:
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
        params["search"] = query

    try:
        resp = await _http_client.get(
            f"{FASTAPI_URL}/recipes",
            params=params,
            headers=_backend_headers(),
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

    _LIST_FIELDS = {
        "id", "name", "status", "yield_mode", "yield_unit",
        "yield_amount", "portions_count_resolved", "is_component",
        "total_raw_weight_grams", "recipe_number",
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

    items = [
        {k: v for k, v in item.items() if k in _LIST_FIELDS}
        for item in items
        if isinstance(item, dict)
    ]

    envelope: dict[str, Any] = {
        "type": "recipes.list",
        "version": "1",
        "items": items,
        "meta": meta,
    }
    if query:
        envelope["query"] = query

    return envelope


@agent.tool
async def get_recipe_detail(
    ctx: RunContext[StateDeps[KitchenState]],
    recipe_id: str = "",
) -> dict[str, Any]:
    """Fetch a recipe by its UUID and render the recipe card in the canvas.
    recipe_id: UUID format only (e.g. "bd3083b9-10ca-557b-9428-88bb6c9f6733").
    NEVER pass a recipe name, slug, or any other string as recipe_id.

    If recipe_id is not provided, uses get_recipes_list(query="recipe name") or
    state.selected_recipe.id and extract id as fallback.

    Example: User: "show chimichurri"
        → get_recipes_list(query="chimichurri") → extract id
        → get_recipe_detail(recipe_id=<uuid>) → ui.render fires
        → NO TEXT RESPONSE. The card is the answer.
    This tool both fetches the full recipe data AND places the recipe card
    in the canvas slot. The assistant should not call render_component
    separately after this tool -- the card is rendered automatically.

    Use this whenever the user wants to open, inspect, or edit a single recipe.
    Do not guess fields yourself; always call this tool instead.
    """
    state = ctx.deps.state
    if not recipe_id and state.selected_recipe:
        recipe_id = state.selected_recipe.id
    if not recipe_id:
        return {
            "type": "error",
            "version": "1",
            "message": "No recipe_id provided and no recipe selected",
        }
    try:
        resp = await _http_client.get(f"{FASTAPI_URL}/recipes/{recipe_id}", headers=_backend_headers(), timeout=10)
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


@agent.tool
async def render_component(
    ctx: RunContext[StateDeps[KitchenState]],
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


@agent.tool
async def show_notification(
    ctx: RunContext[StateDeps[KitchenState]],
    message: str,
    level: str = "info",
    duration: int = 5000,
) -> ToolReturn:
    """Show a transient toast notification.

    Levels: "info", "success", "warning", "error".
    Duration is in milliseconds (default 5000).
    """
    # Deduplicate: if this exact notification was already shown in the
    # current request, return early so the LLM does not loop.
    cache_key = f"{level}:{message}"
    if mark_notification_shown(cache_key):
        return ToolReturn(
            return_value={
                "status": "already_shown",
                "instruction": "STOP. This notification was already displayed. Do not call show_notification again. Output no text.",
            },
            metadata=[],
        )

    value = {
        "type": "ui.render",
        "version": "1",
        "component": "notification",
        "slot": "notifications",
        "message": message,
        "level": level,
        "duration": duration,
    }
    return ToolReturn(
        return_value={
            "status": "ok",
            "instruction": "STOP. Notification displayed. Do not call any more tools. Output no text.",
        },
        metadata=[CustomEvent(type=EventType.CUSTOM, name="ui.render", value=value)],
    )


@agent.tool
async def show_chip(
    ctx: RunContext[StateDeps[KitchenState]],
    actions: list[dict[str, str]],
) -> ToolReturn:
    """Show action confirmation buttons in the chips bar.

    Each action has: label (button text), message (sent to agent on click).
    Optional: variant ("default" | "ghost" | "destructive").

    Example: [{"label": "Apply", "message": "confirm apply scaling", "variant": "default"}]
    """
    value = {
        "type": "ui.render",
        "version": "1",
        "component": "confirmation_chips",
        "slot": "chips",
        "actions": actions,
    }
    return ToolReturn(
        return_value={"status": "ok"},
        metadata=[CustomEvent(type=EventType.CUSTOM, name="ui.render", value=value)],
    )


@agent.tool
async def clear_slot(ctx: RunContext[StateDeps[KitchenState]], slot: str) -> ToolReturn:
    """Clear a UI slot, removing its rendered component.

    Use this to dismiss chips, notifications, or canvas content.
    Slots: "canvas", "sticky", "chips", "notifications", "overlay".
    """
    if slot not in VALID_SLOTS:
        return ToolReturn(
            return_value={"status": "error", "message": f"Unknown slot: {slot}"},
            metadata=[],
        )
    value = {"type": "ui.clear", "version": "1", "slot": slot}
    return ToolReturn(
        return_value={
            "status": "ok",
            "instruction": "STOP. Slot cleared. Do not call any more tools. Output no text.",
        },
        metadata=[CustomEvent(type=EventType.CUSTOM, name="ui.clear", value=value)],
    )

class _PatchOp(BaseModel):
    op: str
    path: str
    value: Any = None


@agent.tool
async def scale_recipe(
    ctx: RunContext[StateDeps[KitchenState]],
    recipe_id: str = "",
    target_portions: float = 0,
) -> StateSnapshotEvent:
    """Activate the scaling editor for a recipe with a target portion count.

    If recipe_id is not provided, uses state.selected_recipe.id as fallback.

    Fetches the recipe data and sends a STATE_SNAPSHOT that activates scaling mode
    on the recipe card. The frontend computes the ratio and scales ingredients locally.

    IMPORTANT: always call get_recipe_detail(recipe_id) BEFORE this tool,
    so the recipe card is already visible in the canvas.

    Args:
        recipe_id: UUID of the recipe to scale.
        target_portions: The desired number of portions. Compute this from the
            chef's words: "double" = original*2, "triple" = original*3,
            "scale to 20" = 20, "halve" = original/2.
    """
    state = ctx.deps.state
    logger.warning("[scale_recipe] state.selected_recipe: %s", state.selected_recipe)
    if not recipe_id and state.selected_recipe:
        recipe_id = state.selected_recipe.id
    if not recipe_id:
        return StateSnapshotEvent(
            type=EventType.STATE_SNAPSHOT,
            snapshot={"widget": "recipe.scaling", "version": "1", "error": "No recipe_id provided"},
        )

    try:
        resp = await _http_client.get(
            f"{FASTAPI_URL}/recipes/{recipe_id}", headers=_backend_headers(), timeout=10
        )
        resp.raise_for_status()
        payload = resp.json()
    except Exception as exc:
        return StateSnapshotEvent(
            type=EventType.STATE_SNAPSHOT,
            snapshot={
                "widget": "recipe.scaling",
                "version": "1",
                "recipeId": recipe_id,
                "error": str(exc),
            },
        )

    portions = payload.get("portions_count_resolved")
    raw_weight = payload.get("total_raw_weight_grams")
    cooked_weight = payload.get("total_cooked_weight_grams")
    yield_mode = payload.get("yield_mode", "count")

    ingredients = []
    for ing in payload.get("ingredients", []):
        qty = float(ing["quantity"]) if ing.get("quantity") is not None else 0
        ingredients.append({
            "id": ing.get("id"),
            "name": ing.get("ingredient_name", ""),
            "quantity": qty,
            "unit": ing.get("unit", ""),
            "originalQuantity": qty,
        })

    # Compute derived weights from ratio so frontend has full context.
    # Frontend will re-compute these anyway, but pre-filling helps the initial render.
    orig_portions = float(portions) if portions is not None else None
    ratio = target_portions / orig_portions if orig_portions else 1

    orig_raw = float(raw_weight) if raw_weight is not None else None
    orig_cooked = float(cooked_weight) if cooked_weight is not None else None

    snapshot = {
        "widget": "recipe.scaling",
        "version": "1",
        "recipeId": str(payload.get("id", recipe_id)),
        "recipeName": payload.get("name", ""),
        "original": {
            "portions": orig_portions,
            "totalRawWeight": orig_raw,
            "totalCookedWeight": orig_cooked,
            "yieldMode": yield_mode,
        },
        "current": {
            "portions": target_portions,
            "totalRawWeight": round(orig_raw * ratio, 2) if orig_raw else None,
            "totalCookedWeight": round(orig_cooked * ratio, 2) if orig_cooked else None,
        },
        "ingredients": ingredients,
        "suggestedFields": None,
        "isDirty": True,
    }

    return StateSnapshotEvent(
        type=EventType.STATE_SNAPSHOT,
        snapshot=snapshot,
    )


@agent.tool
async def apply_recipe_changes(
    ctx: RunContext[StateDeps[KitchenState]],
    recipe_id: str,
    portions: float | None = None,
    total_raw_weight: float | None = None,
    total_cooked_weight: float | None = None,
    ingredients: list[dict[str, Any]] | None = None,
) -> StateDeltaEvent:
    """Apply scaled recipe changes to the database.

    Persists the updated portions, weights, and ingredient quantities via
    PUT /recipes/:id, then returns a STATE_DELTA confirming the clean state.
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
            f"{FASTAPI_URL}/recipes/{recipe_id}",
            json=updates,
            headers=_backend_headers(),
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


@agent.tool
async def suggest_recipe_improvements(ctx: RunContext[StateDeps[KitchenState]], recipe_id: str) -> StateDeltaEvent:
    """Analyze a recipe and suggest improvements for missing or weak fields.

    Returns a STATE_DELTA patch with suggestedFields containing proposed values
    for description, instructions, or other empty/incomplete fields.
    """
    try:
        resp = await _http_client.get(
            f"{FASTAPI_URL}/recipes/{recipe_id}", headers=_backend_headers(), timeout=10
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


# --- Semantic search via the rag service -----------------------------------


@agent.tool
async def search_recipes(
    ctx: RunContext[StateDeps[KitchenState]],
    query: str,
    k: int = 5,
) -> dict[str, Any]:
    """Semantic recipe search via the rag service.

    Use for descriptive, fuzzy, or multilingual recipe queries that do not
    match an existing recipe name (e.g., "something with chickpeas",
    "creamy soup", "vegane Hauptspeise"). For exact-name lookups, prefer
    get_recipes_list. For UUID lookups, use get_recipe_detail.

    Returns a recipes.list envelope (renders as a card) or an error
    envelope when no strong match is found.

    Args:
        query: Natural-language search query.
        k: Number of results to return (1-10).
    """
    k = max(1, min(k, 10))
    try:
        resp = await _http_client.post(
            f"{_RAG_URL}/search/recipes",
            json={"query": query, "k": k},
            timeout=15,
        )
        resp.raise_for_status()
        payload = resp.json()
    except Exception as exc:
        return {
            "type": "error",
            "version": "1",
            "source": "search_recipes",
            "message": f"search service unavailable: {exc}",
            "instruction": "STOP. Call show_notification(level: 'error') once with the message above and make no further tool calls.",
        }

    raw_items = payload.get("items", []) or []
    confident = [
        it for it in raw_items if (it.get("score") or 0) >= SEARCH_MIN_SCORE
    ]
    if not confident:
        return {
            "type": "error",
            "version": "1",
            "source": "search_recipes",
            "message": f"No strong match for '{query}'.",
            "instruction": "STOP. Call show_notification(level: 'info') once with the message above and make no further tool calls.",
        }

    list_items: list[dict[str, Any]] = []
    for it in confident:
        p = it.get("payload") or {}
        list_items.append(
            {
                "id": p.get("id"),
                "name": p.get("name"),
                "status": p.get("status"),
                "yield_unit": p.get("yield_unit"),
                "preparation_time_minutes": p.get("preparation_time_minutes"),
            }
        )

    return {
        "type": "recipes.list",
        "version": "1",
        "items": list_items,
        "meta": {"limit": k, "offset": 0, "total": len(list_items)},
        "query": query,
        "search": "semantic",
    }


@agent.tool
async def search_ingredients(
    ctx: RunContext[StateDeps[KitchenState]],
    query: str,
    k: int = 10,
) -> dict[str, Any]:
    """Semantic ingredient search via the rag service.

    Use for ingredient knowledge questions ("what vegan proteins do you
    have?", "alternatives to feta", "is paprika spicy?"). The result is
    plain data for your reasoning — render the response by calling
    show_notification with a brief summary. Do not invent ingredients
    not in the result.

    Args:
        query: Natural-language ingredient query.
        k: Number of results to return (1-20).
    """
    k = max(1, min(k, 20))
    try:
        resp = await _http_client.post(
            f"{_RAG_URL}/search/ingredients",
            json={"query": query, "k": k},
            timeout=15,
        )
        resp.raise_for_status()
        payload = resp.json()
    except Exception as exc:
        return {
            "type": "error",
            "version": "1",
            "source": "search_ingredients",
            "message": f"search service unavailable: {exc}",
            "instruction": "STOP. Call show_notification(level: 'error') once with the message above and make no further tool calls.",
        }

    raw_items = payload.get("items", []) or []
    confident = [
        it for it in raw_items if (it.get("score") or 0) >= SEARCH_MIN_SCORE
    ]
    if not confident:
        return {
            "type": "error",
            "version": "1",
            "source": "search_ingredients",
            "message": f"No strong ingredient match for '{query}'.",
            "instruction": "STOP. Call show_notification(level: 'info') once with the message above and make no further tool calls.",
        }

    list_items: list[dict[str, Any]] = []
    for it in confident:
        p = it.get("payload") or {}
        list_items.append(
            {
                "id": p.get("id"),
                "name": p.get("name"),
                "name_english": p.get("name_english"),
                "bls_key": p.get("bls_key"),
            }
        )

    return {
        "type": "ingredients.search.result",
        "version": "1",
        "query": query,
        "items": list_items,
    }
