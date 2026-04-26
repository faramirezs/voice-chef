/**
 * Shared state shape for bidirectional frontend-agent synchronization.
 *
 * This must match the Python KitchenState Pydantic model in agent/app/state.py.
 * Both sides serialize/deserialize the same JSON structure.
 */

export interface SelectedRecipe {
  id: string;
  name: string;
  portions: number | null;
  yield_mode: string;
}

export interface ScalingContext {
  target_portions: number | null;
  is_dirty: boolean;
}

export interface LastAction {
  type: "search" | "select" | "scale" | "apply" | "browse" | "clear";
  timestamp: number;
}

export interface KitchenState {
  view: "empty" | "recipe_list" | "recipe_detail" | "scaling";
  selected_recipe: SelectedRecipe | null;
  scaling: ScalingContext | null;
  last_action: LastAction | null;
}

export const DEFAULT_KITCHEN_STATE: KitchenState = {
  view: "empty",
  selected_recipe: null,
  scaling: null,
  last_action: null,
};

/** Type guard for partial state updates. */
export function isKitchenState(value: unknown): value is KitchenState {
  return (
    typeof value === "object" &&
    value !== null &&
    typeof (value as Record<string, unknown>).view === "string"
  );
}
