import { RecipeList } from '@/components/recipes/RecipeList';
import { Button } from '@/components/ui/button';

export function RecipesPage() {
  return (
    <div className="space-y-6">
      <div className="flex items-start justify-between gap-4">
        <div className="space-y-1">
          <h1 className="text-2xl font-semibold">Recipes</h1>
          <p className="text-muted-foreground">Browse and manage your recipe collection.</p>
        </div>
        <Button onClick={() => alert('Create new recipe functionality coming soon!')}>
          Create new recipe
        </Button>
      </div>
      <RecipeList />
    </div>
  );
}
