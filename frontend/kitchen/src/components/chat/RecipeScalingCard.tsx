import { useCallback, useMemo, useState } from "react";
import { KCard } from "@/components/ui/KCard";
import { KButton } from "@/components/ui/KButton";
import type {
  RecipeScalingState,
  RecipeScalingIngredient,
} from "@/types/scaling";

interface RecipeScalingCardProps {
  state: RecipeScalingState;
  onApply: (state: RecipeScalingState) => void;
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

export function RecipeScalingCard({
  state,
  onApply,
}: RecipeScalingCardProps) {
  const { original, current, ingredients, recipeName, suggestedFields, isDirty } =
    state;

  const [localCurrent, setLocalCurrent] = useState(current);
  const [applying, setApplying] = useState(false);

  const ratio = computeRatio(original, localCurrent);
  const displayedIngredients = useMemo(
    () => scaledIngredients(ingredients, ratio),
    [ingredients, ratio]
  );

  const dirty =
    isDirty ||
    localCurrent.portions !== current.portions ||
    localCurrent.totalRawWeight !== current.totalRawWeight ||
    localCurrent.totalCookedWeight !== current.totalCookedWeight;

  const handleFieldChange = useCallback(
    (field: TargetField, raw: string) => {
      const value = raw === "" ? null : parseFloat(raw);
      if (raw !== "" && Number.isNaN(value)) return;
      setLocalCurrent((prev) => ({ ...prev, [field]: value }));
    },
    []
  );

  const handleApply = useCallback(() => {
    if (applying) return;
    setApplying(true);
    const finalIngredients = scaledIngredients(ingredients, ratio);
    onApply({
      ...state,
      current: localCurrent,
      ingredients: finalIngredients,
      isDirty: false,
    });
    setApplying(false);
  }, [applying, ingredients, ratio, localCurrent, state, onApply]);

  const targetField = getTargetField(original.yieldMode);

  if (state.error) {
    return (
      <KCard className="p-4">
        <div className="bg-error/10 border border-error/30 rounded-2xl p-4 text-error">
          <p className="font-semibold">Error loading recipe</p>
          <p className="text-sm mt-1">{state.error}</p>
        </div>
      </KCard>
    );
  }

  return (
    <KCard className="p-4 space-y-4">
      {/* Header */}
      <div className="flex items-center justify-between flex-wrap gap-2">
        <h3 className="text-lg font-semibold">{recipeName || "Recipe"}</h3>
        {dirty && (
          <span className="text-xs text-warning bg-warning/15 px-2 py-0.5 rounded-full">
            Unsaved changes
          </span>
        )}
      </div>

      {/* Editable yield fields */}
      <div className="grid grid-cols-3 gap-3">
        <FieldInput
          label="Portions"
          value={localCurrent.portions}
          isTarget={targetField === "portions"}
          onChange={(v) => handleFieldChange("portions", v)}
        />
        <FieldInput
          label="Raw weight (g)"
          value={localCurrent.totalRawWeight}
          isTarget={targetField === "totalRawWeight"}
          onChange={(v) => handleFieldChange("totalRawWeight", v)}
        />
        <FieldInput
          label="Cooked weight (g)"
          value={localCurrent.totalCookedWeight}
          isTarget={targetField === "totalCookedWeight"}
          onChange={(v) => handleFieldChange("totalCookedWeight", v)}
        />
      </div>

      {/* Ingredient table */}
      {displayedIngredients.length > 0 && (
        <div className="overflow-x-auto">
          <table className="w-full text-sm">
            <thead>
              <tr className="border-b border-border/50 text-text-muted text-left">
                <th className="py-2 pr-3 font-medium">Ingredient</th>
                <th className="py-2 pr-3 font-medium text-right">Quantity</th>
                <th className="py-2 font-medium">Unit</th>
              </tr>
            </thead>
            <tbody>
              {displayedIngredients.map((ing) => (
                <tr key={ing.id} className="border-b border-border/20">
                  <td className="py-2 pr-3">{ing.name}</td>
                  <td className="py-2 pr-3 text-right font-mono">
                    {ing.quantity}
                  </td>
                  <td className="py-2">{ing.unit}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}

      {/* Suggested fields (from auto-improve) */}
      {suggestedFields && (
        <div className="bg-primary/8 border border-primary/20 rounded-xl p-3 space-y-2">
          <p className="text-sm font-medium text-primary">
            Suggested improvements
          </p>
          {Object.entries(suggestedFields).map(([key, value]) => (
            <div key={key} className="flex items-start gap-2 text-sm">
              <span className="text-text-muted shrink-0">+{key}:</span>
              <span className="text-text">{value}</span>
            </div>
          ))}
        </div>
      )}

      {/* Apply button */}
      {dirty && (
        <div className="flex justify-end pt-1">
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

function FieldInput({
  label,
  value,
  isTarget,
  onChange,
}: {
  label: string;
  value: number | null;
  isTarget: boolean;
  onChange: (raw: string) => void;
}) {
  return (
    <div className="space-y-1">
      <label className="text-xs text-text-muted flex items-center gap-1">
        {label}
        {isTarget && (
          <span className="text-[10px] text-primary bg-primary/15 px-1 rounded">
            drive
          </span>
        )}
      </label>
      <input
        type="number"
        step="any"
        value={value ?? ""}
        onChange={(e) => onChange(e.target.value)}
        className="w-full h-10 px-3 text-sm rounded-xl bg-surface/90 border border-border text-text
          focus:outline-none focus:ring-2 focus:ring-primary/50 focus:border-primary/60"
      />
    </div>
  );
}
