import { useCallback, useMemo, useState } from "react";
import { KCard } from "@/components/ui/KCard";
import { KButton } from "@/components/ui/KButton";
import { useAgent, useAgentState } from "@/hooks/useAgent";
import { useAgentSlots } from "@/components/layout/AgentSlotProvider";
import { isRecipeScalingState } from "@/types/scaling";
import type { RecipeScalingState, RecipeScalingIngredient } from "@/types/scaling";
import { RecipeYieldBar } from "./RecipeYieldBar";
import { RecipeIngredientTable } from "./RecipeIngredientTable";
import { RecipeSection } from "./RecipeSection";

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
    <KCard className="p-5 space-y-5 animate-pulse max-w-2xl w-full">
      <div className="flex items-center justify-between">
        <div className="h-7 w-48 rounded bg-border/30" />
        <div className="h-6 w-16 rounded-full bg-border/20" />
      </div>
      <div className="grid grid-cols-3 gap-3">
        <div className="h-16 rounded-2xl bg-border/20" />
        <div className="h-16 rounded-2xl bg-border/20" />
        <div className="h-16 rounded-2xl bg-border/20" />
      </div>
      <div className="space-y-2">
        <div className="h-4 w-full rounded bg-border/15" />
        <div className="h-4 w-3/4 rounded bg-border/15" />
        <div className="h-4 w-5/6 rounded bg-border/15" />
      </div>
    </KCard>
  );
}

// --- Main component ---

export function RecipeDetailCard(props: Record<string, unknown>) {
  const agentState = useAgentState();
  const { sendMessage } = useAgent();
  const { clear } = useAgentSlots();

  // Extract recipe data from slot props (set by render_component -> ui.render)
  const recipe = extractRecipeData(props);

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
}

function RecipeCardInner({
  recipe,
  scalingState,
  sendMessage,
  clearCanvas,
}: InnerProps) {
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
      setLocalCurrent(scalingState.current);
    }
  }, [scalingState]);

  // Error state
  if (scalingState?.error) {
    return (
      <KCard className="p-5 max-w-2xl w-full">
        <div className="bg-error/10 border border-error/30 rounded-2xl p-4">
          <p className="text-error font-semibold">Error loading recipe</p>
          <p className="text-sm mt-1 text-error/80">{scalingState.error}</p>
        </div>
      </KCard>
    );
  }

  return (
    <KCard className="p-5 space-y-5 max-w-2xl w-full">
      {/* Header */}
      <div className="flex items-start justify-between gap-3">
        <h2 className="text-2xl font-semibold text-text truncate">
          {recipe.name}
        </h2>
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
        <p className="text-base text-text-muted leading-relaxed">
          {recipe.description}
        </p>
      )}

      {/* Yield bar */}
      <RecipeYieldBar
        fields={yieldFields}
        mode={mode}
        onChange={handleYieldChange}
      />

      {/* Ingredients */}
      <RecipeIngredientTable
        ingredients={recipe.ingredients}
        scalingIngredients={
          mode === "scaling" && scaledIng.length > 0 ? scaledIng : undefined
        }
        mode={mode}
        scalingRatio={ratio}
      />

      {/* Instructions */}
      {recipe.instructions && (
        <RecipeSection
          title="Instructions"
          defaultOpen={mode === "detail"}
          forceOpen={mode === "detail"}
        >
          <p className="text-base text-text whitespace-pre-line leading-relaxed">
            {recipe.instructions}
          </p>
        </RecipeSection>
      )}

      {/* Footer actions (scaling mode only) */}
      {mode === "scaling" && dirty && (
        <div className="flex justify-end gap-3 pt-2 border-t border-border/30">
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
    </KCard>
  );
}

function parseNum(value: string | null | undefined): number | null {
  if (value == null) return null;
  const n = parseFloat(value);
  return Number.isNaN(n) ? null : n;
}
