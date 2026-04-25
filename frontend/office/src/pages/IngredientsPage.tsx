import { IngredientsList } from '@/components/ingredients/IngredientList';

export function IngredientsPage() {
  return (
    <div className="space-y-6">
      <div className="space-y-1">
        <h1 className="text-2xl font-semibold">Ingredients</h1>
        <p className="text-muted-foreground">Manage your ingredients and inventory.</p>
      </div>
      <IngredientsList />
    </div>
  );
}
