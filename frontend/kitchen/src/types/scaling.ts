export interface RecipeScalingIngredient {
  id: string;
  name: string;
  quantity: number;
  unit: string;
  originalQuantity: number;
}

export interface RecipeScalingOriginal {
  portions: number | null;
  totalRawWeight: number | null;
  totalCookedWeight: number | null;
  yieldMode: "count" | "weight";
}

export interface RecipeScalingCurrent {
  portions: number | null;
  totalRawWeight: number | null;
  totalCookedWeight: number | null;
}

export interface RecipeScalingState {
  widget: "recipe.scaling";
  version: "1";
  recipeId: string;
  recipeName: string;
  original: RecipeScalingOriginal;
  current: RecipeScalingCurrent;
  ingredients: RecipeScalingIngredient[];
  suggestedFields: Record<string, string> | null;
  isDirty: boolean;
  error?: string;
}

export function isRecipeScalingState(
  value: unknown
): value is RecipeScalingState {
  return (
    typeof value === "object" &&
    value !== null &&
    (value as Record<string, unknown>).widget === "recipe.scaling"
  );
}
