import { cn } from "@/lib/utils";

interface DetailIngredient {
  id: string;
  ingredient_name: string;
  quantity: string;
  unit: string;
  preparation: string | null;
}

interface ScalingIngredient {
  id: string;
  name: string;
  quantity: number;
  unit: string;
  originalQuantity: number;
}

interface RecipeIngredientTableProps {
  ingredients: DetailIngredient[];
  scalingIngredients?: ScalingIngredient[];
  mode: "detail" | "scaling";
  scalingRatio?: number;
}

export function RecipeIngredientTable({
  ingredients,
  scalingIngredients,
  mode,
}: RecipeIngredientTableProps) {
  if (mode === "scaling" && scalingIngredients && scalingIngredients.length > 0) {
    return <ScalingTable ingredients={scalingIngredients} />;
  }

  if (ingredients.length === 0) {
    return (
      <div className="py-4 text-center text-text-muted italic text-sm">
        No ingredients listed
      </div>
    );
  }

  return <DetailTable ingredients={ingredients} />;
}

function DetailTable({ ingredients }: { ingredients: DetailIngredient[] }) {
  const multiCol = ingredients.length > 15;
  return (
    <div className={cn("text-sm", multiCol && "columns-2 gap-4")}>
      {ingredients.map((ing) => (
        <div key={ing.id} className="py-1 break-inside-avoid">
          <span className="font-mono">{stripTrailingZeros(ing.quantity)}</span>{" "}
          <span>{ing.unit}</span>{" "}
          <span className="font-medium">{ing.ingredient_name}</span>
          {ing.preparation?.trim() && (
            <span className="text-text-muted"> ({ing.preparation.trim()})</span>
          )}
        </div>
      ))}
    </div>
  );
}

function ScalingTable({
  ingredients,
}: {
  ingredients: ScalingIngredient[];
}) {
  return (
    <div className="text-sm space-y-0.5">
      {ingredients.map((ing) => {
        const changed = ing.quantity !== ing.originalQuantity;
        return (
          <div
            key={ing.id}
            className="flex items-center justify-between gap-3 py-1"
          >
            <span className="font-medium">{ing.name}</span>
            <span className="font-mono text-right shrink-0">
              <span className="text-text-muted">
                {formatNum(ing.originalQuantity)}
              </span>
              {" → "}
              <span className={changed ? "text-primary" : ""}>
                {formatNum(ing.quantity)}
              </span>{" "}
              <span className="text-text-muted">{ing.unit}</span>
            </span>
          </div>
        );
      })}
    </div>
  );
}

function stripTrailingZeros(value: string): string {
  const num = parseFloat(value);
  if (Number.isNaN(num)) return value;
  const str = num.toFixed(4);
  return str.replace(/\.?0+$/, "");
}

function formatNum(value: number): string {
  const str = value.toFixed(2);
  return str.replace(/\.?0+$/, "");
}
