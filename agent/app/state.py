"""Shared state model for bidirectional frontend-agent synchronization.

KitchenState is serialized into RunAgentInput.state by the frontend
and deserialized by the pydantic-ai AGUIAdapter into the agent's deps.

Both frontend and backend must agree on this shape.
"""

from typing import Any
from pydantic import BaseModel


class SelectedRecipe(BaseModel):
    """Minimal recipe info for agent context."""

    id: str
    name: str
    portions: float | None = None
    yield_mode: str = "count"


class ScalingContext(BaseModel):
    """Active scaling session info."""

    target_portions: float | None = None
    is_dirty: bool = False


class LastAction(BaseModel):
    """Record of the last user action for agent reasoning."""

    type: str  # "search" | "select" | "scale" | "apply" | "browse" | "clear" | "voice"
    timestamp: int  # epoch ms


class KitchenState(BaseModel):
    """Full state snapshot shared between kitchen frontend and agent.

    The frontend sets this via chefAgent.setState() before runAgent().
    The agent reads it from ctx.deps.state inside tools.
    """

    view: str = "empty"  # "empty" | "recipe_list" | "recipe_detail" | "scaling"
    selected_recipe: SelectedRecipe | None = None
    scaling: ScalingContext | None = None
    last_action: LastAction | None = None

    # Convenience helpers for tools
    def has_selected_recipe(self) -> bool:
        return self.selected_recipe is not None

    def get_recipe_id(self) -> str | None:
        return self.selected_recipe.id if self.selected_recipe else None

    def get_recipe_name(self) -> str | None:
        return self.selected_recipe.name if self.selected_recipe else None
