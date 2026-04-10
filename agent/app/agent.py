import os
import httpx
from pydantic_ai import Agent
from pydantic_ai.models.openrouter import OpenRouterModel
from pydantic_ai.providers.openrouter import OpenRouterProvider

FASTAPI_URL = os.getenv("FASTAPI_INTERNAL_URL", "http://fastapi:80")

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
async def search_recipes(query: str) -> list[dict]:
    """Search recipes by name in the database."""
    async with httpx.AsyncClient() as client:
        resp = await client.get(f"{FASTAPI_URL}/recipes", timeout=10)
        resp.raise_for_status()
        recipes = resp.json()
        return [r for r in recipes if query.lower() in r["name"].lower()]

@agent.tool_plain
async def get_recipe_detail(recipe_id: str) -> dict:
    """Get full details of a recipe by its UUID."""
    async with httpx.AsyncClient() as client:
        resp = await client.get(f"{FASTAPI_URL}/recipes/{recipe_id}", timeout=10)
        resp.raise_for_status()
        return resp.json()
