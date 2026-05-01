import { useCallback } from "react";
import { setSharedAgentState } from "@/hooks/useAgent";
import { useAgentSlots } from "@/components/layout/AgentSlotProvider";
import { chefAgent } from "@/lib/agent";
import type { KitchenState } from "@/types/agent-state";
import type { RecipeScalingState } from "@/types/scaling";

export interface ActivateResult {
  success: boolean;
  error?: string;
}

interface RecipeIngredient {
  id: string;
  ingredient_name: string;
  quantity: string;
  unit: string;
}

interface RecipeDetailResponse {
  id: string;
  name: string;
  portions_count_resolved: string | null;
  total_raw_weight_grams: string | null;
  total_cooked_weight_grams: string | null;
  yield_mode: string;
  ingredients: RecipeIngredient[];
}

function parseNum(value: string | null | undefined): number | null {
  if (value == null) return null;
  const n = parseFloat(value);
  return Number.isNaN(n) ? null : n;
}

export function useRecipeScaling(): {
  activateScaling: (targetPortions?: number) => Promise<ActivateResult>;
  deactivateScaling: () => void;
} {
  const { selectedRecipeId } = useAgentSlots();

  const activateScaling = useCallback(
    async (targetPortions?: number): Promise<ActivateResult> => {
      if (!selectedRecipeId) {
        return { success: false, error: "No recipe selected" };
      }

      let payload: RecipeDetailResponse;
      try {
        const resp = await fetch(`/api/recipes/${selectedRecipeId}`);
        if (!resp.ok) {
          return {
            success: false,
            error: `Failed to fetch recipe (${resp.status})`,
          };
        }
        payload = (await resp.json()) as RecipeDetailResponse;
      } catch (err) {
        return {
          success: false,
          error: err instanceof Error ? err.message : "Network error",
        };
      }

      const portions = parseNum(payload.portions_count_resolved);
      const rawWeight = parseNum(payload.total_raw_weight_grams);
      const cookedWeight = parseNum(payload.total_cooked_weight_grams);
      const yieldMode = payload.yield_mode || "count";
      const currentPortions = targetPortions ?? portions ?? 0;

      const ratio =
        portions != null && portions !== 0 ? currentPortions / portions : 1;

      const ingredients = payload.ingredients.map((ing) => {
        const qty = parseNum(ing.quantity) ?? 0;
        return {
          id: ing.id,
          name: ing.ingredient_name || "",
          quantity: qty,
          unit: ing.unit || "",
          originalQuantity: qty,
        };
      });

      const scalingState: RecipeScalingState = {
        widget: "recipe.scaling",
        version: "1",
        recipeId: payload.id,
        recipeName: payload.name,
        original: {
          portions,
          totalRawWeight: rawWeight,
          totalCookedWeight: cookedWeight,
          yieldMode: yieldMode as "count" | "weight",
        },
        current: {
          portions: currentPortions,
          totalRawWeight:
            rawWeight != null ? Math.round(rawWeight * ratio * 100) / 100 : null,
          totalCookedWeight:
            cookedWeight != null
              ? Math.round(cookedWeight * ratio * 100) / 100
              : null,
        },
        ingredients,
        suggestedFields: null,
        isDirty: true,
      };

      setSharedAgentState(scalingState);

      const ks: KitchenState = {
        view: "scaling",
        selected_recipe: {
          id: payload.id,
          name: payload.name,
          portions,
          yield_mode: yieldMode,
        },
        scaling: {
          target_portions: scalingState.current.portions,
          is_dirty: scalingState.isDirty,
        },
        last_action: { type: "scale", timestamp: Date.now() },
      };
      chefAgent.setState(ks);

      return { success: true };
    },
    [selectedRecipeId]
  );

  const deactivateScaling = useCallback(() => {
    setSharedAgentState(null);

    const agentState = chefAgent.state as Record<string, unknown> | null;
    const looksLikeKitchenState =
      agentState != null && typeof agentState.view === "string";

    const ks: KitchenState = looksLikeKitchenState
      ? {
          view: "recipe_detail",
          selected_recipe: (agentState.selected_recipe as KitchenState["selected_recipe"]) ?? null,
          scaling: null,
          last_action: { type: "clear", timestamp: Date.now() },
        }
      : {
          view: "empty",
          selected_recipe: null,
          scaling: null,
          last_action: { type: "clear", timestamp: Date.now() },
        };

    chefAgent.setState(ks);
  }, []);

  return { activateScaling, deactivateScaling };
}
