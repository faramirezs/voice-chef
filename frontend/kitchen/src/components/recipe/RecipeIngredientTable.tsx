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
  return (
    <div className="overflow-x-auto">
      <table className="w-full text-base">
        <thead>
          <tr className="border-b border-border/50 text-text-muted text-left text-xs uppercase tracking-wide">
            <th className="py-2.5 pr-3 font-medium">Ingredient</th>
            <th className="py-2.5 pr-3 font-medium">Prep</th>
            <th className="py-2.5 pr-3 font-medium text-right">Quantity</th>
            <th className="py-2.5 font-medium">Unit</th>
          </tr>
        </thead>
        <tbody>
          {ingredients.map((ing) => (
            <tr
              key={ing.id}
              className="border-b border-border/20 hover:bg-surface/40 transition-colors"
            >
              <td className="py-2.5 pr-3">{ing.ingredient_name}</td>
              <td className="py-2.5 pr-3 text-text-muted">
                {ing.preparation?.trim() || "\u2014"}
              </td>
              <td className="py-2.5 pr-3 text-right font-mono">
                {stripTrailingZeros(ing.quantity)}
              </td>
              <td className="py-2.5">{ing.unit}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

function ScalingTable({
  ingredients,
}: {
  ingredients: ScalingIngredient[];
}) {
  return (
    <div className="overflow-x-auto">
      <table className="w-full text-base">
        <thead>
          <tr className="border-b border-border/50 text-text-muted text-left text-xs uppercase tracking-wide">
            <th className="py-2.5 pr-3 font-medium">Ingredient</th>
            <th className="py-2.5 pr-3 font-medium text-right">Original</th>
            <th className="py-2.5 pr-3 font-medium text-right">Scaled</th>
            <th className="py-2.5 font-medium">Unit</th>
          </tr>
        </thead>
        <tbody>
          {ingredients.map((ing) => {
            const changed = ing.quantity !== ing.originalQuantity;
            return (
              <tr
                key={ing.id}
                className="border-b border-border/20 hover:bg-surface/40 transition-colors"
              >
                <td className="py-2.5 pr-3">{ing.name}</td>
                <td className="py-2.5 pr-3 text-right font-mono text-text-muted text-sm">
                  {formatNum(ing.originalQuantity)}
                </td>
                <td
                  className={`py-2.5 pr-3 text-right font-mono ${
                    changed ? "text-primary" : ""
                  }`}
                >
                  {formatNum(ing.quantity)}
                </td>
                <td className="py-2.5">{ing.unit}</td>
              </tr>
            );
          })}
        </tbody>
      </table>
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
