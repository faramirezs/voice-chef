import { RecipeList } from '@/components/recipes/RecipeList';

export function RecipesPage() {
  return (
    <div className="space-y-6">
      <div className="space-y-1">
        <h1 className="text-2xl font-semibold">Recipes</h1>
        <p className="text-muted-foreground">Browse and manage your recipe collection.</p>
      </div>
      <RecipeList />
    </div>
  );
}
