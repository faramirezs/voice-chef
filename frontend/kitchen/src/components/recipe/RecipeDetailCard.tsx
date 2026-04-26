import { useCallback, useEffect, useMemo, useState } from "react";
import { KButton } from "@/components/ui/KButton";
import { useAgent, useAgentState } from "@/hooks/useAgent";
import { useAgentSlots } from "@/components/layout/AgentSlotProvider";
import { cn } from "@/lib/utils";

import { isRecipeScalingState } from "@/types/scaling";
import type { RecipeScalingState, RecipeScalingIngredient } from "@/types/scaling";
import { RecipeYieldBar } from "./RecipeYieldBar";
import { RecipeIngredientTable } from "./RecipeIngredientTable";
import { chefAgent } from "@/lib/agent";
import { type KitchenState } from "@/types/agent-state";

// --- Data shapes ---

interface RecipeIngredient {
  id: string;
  ingredient_name: string;
  quantity: string;
  unit: string;
  quantity_grams: string | null;
  preparation: string | null;
  sort_order: number;
}

interface RecipeData {
  id: string;
  name: string;
  description: string | null;
  instructions: string | null;
  status: string;
  yield_mode: string;
  portion_size_grams: string | null;
  total_raw_weight_grams: string | null;
  total_cooked_weight_grams: string | null;
  portions_count_resolved: string | null;
  ingredients: RecipeIngredient[];
}

type TargetField = "portions" | "totalRawWeight" | "totalCookedWeight";

function getTargetField(yieldMode: string): TargetField {
  return yieldMode === "weight" ? "totalRawWeight" : "portions";
}

function computeRatio(
  original: RecipeScalingState["original"],
  current: RecipeScalingState["current"]
): number {
  const field = getTargetField(original.yieldMode);
  const origVal = original[field];
  const curVal = current[field];
  if (origVal == null || curVal == null || origVal === 0) return 1;
  return curVal / origVal;
}

function scaledIngredients(
  ingredients: RecipeScalingIngredient[],
  ratio: number
): RecipeScalingIngredient[] {
  return ingredients.map((ing) => ({
    ...ing,
    quantity: Math.round(ing.originalQuantity * ratio * 100) / 100,
  }));
}

// --- Status badge ---

const STATUS_STYLES: Record<string, string> = {
  draft: "bg-warning/15 text-warning border-warning/30",
  active: "bg-success/15 text-success border-success/30",
  archived: "bg-border/30 text-text-muted border-border/50",
};

// --- Skeleton ---

function RecipeCardSkeleton() {
  return (
    <div className="w-full h-full flex flex-col px-4 pt-2 animate-pulse gap-3">
      <div className="flex items-center justify-between gap-3 flex-shrink-0">
        <div className="h-8 w-48 rounded bg-border/30" />
        <div className="h-6 w-16 rounded-full bg-border/20" />
      </div>
      <div className="grid grid-cols-3 gap-3 flex-shrink-0">
        <div className="h-14 rounded-xl bg-border/20" />
        <div className="h-14 rounded-xl bg-border/20" />
        <div className="h-14 rounded-xl bg-border/20" />
      </div>
      <div className="flex-1 grid grid-cols-2 gap-4 min-h-0">
        <div className="h-full rounded-xl bg-border/15" />
        <div className="h-full rounded-xl bg-border/15" />
      </div>
    </div>
  );
}

// --- Main component ---

export function RecipeDetailCard(props: Record<string, unknown>) {
  const agentState = useAgentState();
  const { sendMessage } = useAgent();
  const { clear } = useAgentSlots();

  // Extract recipe data from slot props (set by render_component -> ui.render)
  const recipe = extractRecipeData(props);
  const fromList = Boolean(props.from_list);

  // Detect scaling mode: scaling state must match this recipe's ID
  const scalingState = isRecipeScalingState(agentState) ? agentState : null;
  const isScaling =
    scalingState != null && scalingState.recipeId === recipe?.id;

  if (!recipe) {
    return <RecipeCardSkeleton />;
  }

  return (
    <RecipeCardInner
      recipe={recipe}
      scalingState={isScaling ? scalingState : null}
      sendMessage={sendMessage}
      clearCanvas={() => clear("canvas")}
      fromList={fromList}
    />
  );
}


function extractRecipeData(
  props: Record<string, unknown>
): RecipeData | null {
  // The recipe data comes from the render_component payload.
  // When the agent calls get_recipe_detail first, the response is a
  // recipe.detail envelope that doesn't get merged into render props.
  // Instead, recipe data must be passed directly via render_component.
  // For now we look for a top-level recipe/item object in props.
  const source =
    (props.recipe as Record<string, unknown> | undefined) ??
    (props.item as Record<string, unknown> | undefined);

  if (!source || typeof source !== "object") return null;
  if (typeof source.name !== "string") return null;

  return source as unknown as RecipeData;
}

// --- Inner card ---

interface InnerProps {
  recipe: RecipeData;
  scalingState: RecipeScalingState | null;
  sendMessage: (text: string) => void;
  clearCanvas: () => void;
  fromList: boolean;
}

function RecipeCardInner({
  recipe,
  scalingState,
  sendMessage,
  clearCanvas,
  fromList,
}: InnerProps) {
  const { dispatch } = useAgentSlots();
  const mode = scalingState ? "scaling" : "detail";


  // Scaling state
  const [localCurrent, setLocalCurrent] = useState(
    scalingState?.current ?? {
      portions: parseNum(recipe.portions_count_resolved),
      totalRawWeight: parseNum(recipe.total_raw_weight_grams),
      totalCookedWeight: parseNum(recipe.total_cooked_weight_grams),
    }
  );
  const [applying, setApplying] = useState(false);

  // Re-sync local state when scaling STATE_SNAPSHOT arrives after mount.
  // Sync agent state whenever recipe or scaling state changes.
  useEffect(() => {
    const ks: KitchenState = {
      view: scalingState ? "scaling" : "recipe_detail",
      selected_recipe: {
        id: recipe.id,
        name: recipe.name,
        portions: parseNum(recipe.portions_count_resolved),
        yield_mode: recipe.yield_mode,
      },
      scaling: scalingState
        ? {
            target_portions: scalingState.current.portions,
            is_dirty: scalingState.isDirty,
          }
        : null,
      last_action: { type: "select", timestamp: Date.now() },
    };
    chefAgent.setState(ks);
  }, [recipe.id, recipe.name, scalingState, recipe.yield_mode, recipe.portions_count_resolved]);

  useEffect(() => {
    if (scalingState?.current) {
      setLocalCurrent(scalingState.current);
    }
  }, [scalingState?.current]);

  const yieldMode = scalingState?.original.yieldMode ?? recipe.yield_mode;
  const targetField = getTargetField(yieldMode);

  // Compute ratio for ingredient scaling
  const original = scalingState?.original ?? {
    portions: parseNum(recipe.portions_count_resolved),
    totalRawWeight: parseNum(recipe.total_raw_weight_grams),
    totalCookedWeight: parseNum(recipe.total_cooked_weight_grams),
    yieldMode: recipe.yield_mode as "count" | "weight",
  };

  const ratio = computeRatio(original, localCurrent);

  // Scale ingredients if in scaling mode
  const scaledIng = useMemo(() => {
    if (!scalingState?.ingredients.length) return [];
    return scaledIngredients(scalingState.ingredients, ratio);
  }, [scalingState?.ingredients, ratio]);

  const dirty =
    (scalingState?.isDirty ?? false) ||
    (scalingState &&
      (localCurrent.portions !== scalingState.current.portions ||
        localCurrent.totalRawWeight !== scalingState.current.totalRawWeight ||
        localCurrent.totalCookedWeight !== scalingState.current.totalCookedWeight));

  // Yield fields
  const yieldFields = [
    {
      label: "Portions",
      value: localCurrent.portions,
      isTarget: targetField === "portions",
    },
    {
      label: "Raw weight (g)",
      value: localCurrent.totalRawWeight,
      isTarget: targetField === "totalRawWeight",
    },
    {
      label: "Cooked weight (g)",
      value: localCurrent.totalCookedWeight,
      isTarget: targetField === "totalCookedWeight",
    },
  ];

  const handleYieldChange = useCallback(
    (_index: number, raw: string) => {
      // Map index back to field name
      const fields: TargetField[] = [
        "portions",
        "totalRawWeight",
        "totalCookedWeight",
      ];
      const field = fields[_index];
      if (!field) return;
      const value = raw === "" ? null : parseFloat(raw);
      if (raw !== "" && Number.isNaN(value)) return;
      setLocalCurrent((prev) => ({ ...prev, [field]: value }));
    },
    []
  );

  const handleApply = useCallback(() => {
    if (applying || !scalingState) return;
    setApplying(true);
    const finalIngredients = scaledIngredients(
      scalingState.ingredients,
      ratio
    );
    const parts: string[] = [
      `Apply scaling for recipe ${scalingState.recipeId}:`,
      `portions=${localCurrent.portions ?? ""}`,
      `total_raw_weight=${localCurrent.totalRawWeight ?? ""}`,
      `total_cooked_weight=${localCurrent.totalCookedWeight ?? ""}`,
    ];
    if (finalIngredients.length > 0) {
      parts.push(
        "ingredients=" +
          finalIngredients
            .map((i) => `${i.name}:${i.quantity}${i.unit}`)
            .join(",")
      );
    }
    sendMessage(parts.join(" "));
    setApplying(false);
  }, [applying, scalingState, ratio, localCurrent, sendMessage]);

  const handleReset = useCallback(() => {
    if (scalingState) {
      const { yieldMode: _, ...rest } = scalingState.original;
      setLocalCurrent(rest);
    }
  }, [scalingState]);

  const handleQuickScale = useCallback(
    (multiplier: number) => {
      const base = original.portions ?? 0;
      if (base <= 0) return;
      setLocalCurrent((prev) => ({
        ...prev,
        portions: Math.round(base * multiplier * 100) / 100,
      }));
    },
    [original.portions]
  );

  // Error state
  if (scalingState?.error) {
    return (
      <div className="w-full h-full flex flex-col px-4 pt-2">
        <div className="bg-error/10 border border-error/30 rounded-2xl p-4">
          <p className="text-error font-semibold">Error loading recipe</p>
          <p className="text-sm mt-1 text-error/80">{scalingState.error}</p>
        </div>
      </div>
    );
  }

  const mainGridClass = cn(
    "flex-1 min-h-0 grid gap-4",
    recipe.ingredients.length > 15 ? "grid-cols-[2fr_1fr]" : "grid-cols-2"
  );

  return (
    <div className="w-full h-full flex flex-col px-4 pt-2 gap-3">
      {/* Header */}
      <div className="flex items-center justify-between gap-3 flex-shrink-0">
        <div className="flex items-center gap-2 min-w-0">
          {fromList && (
            <KButton
              type="button"
              variant="ghost"
              onClick={() => {
                chefAgent.setState({
                  view: "recipe_list",
                  selected_recipe: null,
                  scaling: null,
                  last_action: { type: "browse", timestamp: Date.now() },
                });
                dispatch("canvas", "recipe_list", {});
              }}

              className="h-9 px-3 text-base shrink-0"
            >
              ← Back
            </KButton>
          )}
          <h2 className="text-2xl font-semibold text-text truncate">
            {recipe.name}
          </h2>
        </div>
        <div className="flex items-center gap-2 shrink-0">
          {mode === "scaling" && dirty && (
            <span className="text-xs text-warning bg-warning/15 border border-warning/30 px-2 py-0.5 rounded-full">
              Unsaved
            </span>
          )}
          <span
            className={`text-xs px-2 py-0.5 rounded-full border ${
              STATUS_STYLES[recipe.status] ?? STATUS_STYLES.archived
            }`}
          >
            {recipe.status}
          </span>
          <button
            type="button"
            onClick={clearCanvas}
            className="h-8 w-8 rounded-full bg-surface/80 border border-border/50 text-text-muted text-sm flex items-center justify-center hover:bg-error/20 hover:text-error transition-colors"
            aria-label="Close recipe"
          >
            &times;
          </button>
        </div>
      </div>

      {/* Description */}
      {recipe.description && (
        <p className="text-sm text-text-muted leading-relaxed flex-shrink-0">
          {recipe.description}
        </p>
      )}

      {/* Yield bar */}
      <div className="flex-shrink-0">
        <RecipeYieldBar
          fields={yieldFields}
          mode={mode}
          onChange={handleYieldChange}
        />
      </div>

      {/* Quick-scale buttons (scaling mode only) */}
      {mode === "scaling" && (
        <div className="flex items-center gap-2 flex-shrink-0">
          <span className="text-xs text-text-muted uppercase tracking-wide">Quick scale</span>
          {[2, 3, 5].map((mult) => {
            const base = original.portions ?? 0;
            const target = Math.round(base * mult * 100) / 100;
            const active = localCurrent.portions === target;
            return (
              <KButton
                key={mult}
                type="button"
                variant={active ? "default" : "ghost"}
                onClick={() => handleQuickScale(mult)}
                className="h-8 px-3 text-sm"
              >
                &times;{mult}
              </KButton>
            );
          })}
          {original.portions != null && original.portions > 2 && (
            <KButton
              type="button"
              variant={localCurrent.portions === Math.round((original.portions / 2) * 100) / 100 ? "default" : "ghost"}
              onClick={() => handleQuickScale(0.5)}
              className="h-8 px-3 text-sm"
            >
              &frac12;
            </KButton>
          )}
        </div>
      )}

      {/* Main content: ingredients + instructions */}
      <div className={mainGridClass}>
        {/* Ingredients */}
        <div className="flex flex-col min-h-0">
          <h3 className="text-xs text-text-muted uppercase tracking-wide mb-2">Ingredients</h3>
          <div className="flex-1 overflow-y-auto">
            <RecipeIngredientTable
              ingredients={recipe.ingredients}
              scalingIngredients={
                mode === "scaling" && scaledIng.length > 0 ? scaledIng : undefined
              }
              mode={mode}
              scalingRatio={ratio}
            />
          </div>
        </div>

        {/* Instructions */}
        {recipe.instructions && (
          <div className="flex flex-col min-h-0">
            <h3 className="text-xs text-text-muted uppercase tracking-wide mb-2">Instructions</h3>
            <div className="flex-1 overflow-y-auto">
              <p className="text-base text-text whitespace-pre-line leading-relaxed">
                {recipe.instructions}
              </p>
            </div>
          </div>
        )}
      </div>

      {/* Footer actions (scaling mode only) */}
      {mode === "scaling" && dirty && (
        <div className="flex justify-end gap-3 pt-2 border-t border-border/30 flex-shrink-0">
          <KButton
            type="button"
            variant="ghost"
            onClick={handleReset}
            className="h-11 px-6"
          >
            Reset
          </KButton>
          <KButton
            type="button"
            disabled={applying}
            onClick={handleApply}
            className="h-11 px-6"
          >
            {applying ? "Applying..." : "Apply to database"}
          </KButton>
        </div>
      )}
    </div>
  );
}

function parseNum(value: string | null | undefined): number | null {
  if (value == null) return null;
  const n = parseFloat(value);
  return Number.isNaN(n) ? null : n;
}
