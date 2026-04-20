import os
import httpx
from pydantic_ai import Agent

FASTAPI_URL = os.getenv("FASTAPI_INTERNAL_URL", "http://fastapi:80")

# Read model/provider settings from environment variables.
AGENT_MODEL = os.getenv("AGENT_MODEL")
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")

if not AGENT_MODEL:
    raise RuntimeError(
        "Missing AGENT_MODEL. Set it to a model id, "
        "for example: gemini-2.5-flash or anthropic/claude-sonnet-4-5"
    )

# Reuse a single HTTP client for all tool calls instead of opening a new
# TCP connection on every request. Much faster under load.
_http_client = httpx.AsyncClient()

# Select provider based on which API key is set.
# Google Gemini takes priority if both are present.
if GOOGLE_API_KEY:
    from pydantic_ai.models.gemini import GeminiModel
    from pydantic_ai.providers.google_gla import GoogleGLAProvider
    model = GeminiModel(
        AGENT_MODEL,
        provider=GoogleGLAProvider(api_key=GOOGLE_API_KEY),
    )
elif OPENROUTER_API_KEY:
    from pydantic_ai.models.openrouter import OpenRouterModel
    from pydantic_ai.providers.openrouter import OpenRouterProvider
    model = OpenRouterModel(
        AGENT_MODEL,
        provider=OpenRouterProvider(api_key=OPENROUTER_API_KEY),
    )
else:
    raise RuntimeError(
        "Missing API key. Set GOOGLE_API_KEY or OPENROUTER_API_KEY "
        "in your environment before starting the agent service."
    )

agent = Agent(
    model,
    system_prompt=(
        "You are Voice Chef, a culinary AI assistant for professional kitchen staff. "
        "You have access to the recipe database. Answer questions about recipes, "
        "cooking steps, ingredients, storage, plating, and kitchen operations. "
        "When a chef asks about a recipe, always look it up from the database first. "
        "Respond in a concise, action-oriented way suited for a busy kitchen environment.\n\n"
        "VOICE INPUT HANDLING:\n"
        "User messages may come from speech-to-text transcription. When a message "
        "includes [voice] metadata, the transcription may contain errors — especially "
        "for recipe names, ingredient names, and non-English words. Apply fuzzy matching: "
        "interpret 'borsh' as 'borscht', 'julien' as 'julienne', etc. "
        "When confidence is 'low' or 'medium', be more lenient with interpretation "
        "and ask for confirmation if the intent is ambiguous. "
        "When confidence is 'high', treat the input as reliable text."
    ),
)

# @agent.tool_plain registers a function as a tool the LLM can call.
# "plain" means it doesn't need access to the agent context or run state —
# it just takes arguments and returns a value.

@agent.tool_plain
async def get_recipes_list(query: str) -> list[dict]:
    """Get a list of recipes in the db, optional filter by name."""
    resp = await _http_client.get(f"{FASTAPI_URL}/recipes", timeout=10)
    resp.raise_for_status()
    recipes = resp.json()

    if not query:
        return recipes

    query_lower = query.lower()
    filtered = [
        r for r in recipes
        if isinstance(r, dict)
        and query_lower in str(r.get("name", "")).lower()
    ]

    # With a test-limited endpoint, return available results if local filtering
    # finds nothing to avoid false "no recipes" responses.
    return filtered or recipes

@agent.tool_plain
async def get_recipe_detail(recipe_id: str) -> dict:
    """Get full details of a recipe by its UUID."""
    async with httpx.AsyncClient() as client:
        resp = await client.get(f"{FASTAPI_URL}/recipes/{recipe_id}", timeout=10)
        resp.raise_for_status()
        return resp.json()
