import { RecipeList } from '@/components/recipes/RecipeList';
import { Button } from '@/components/ui/button';
import { useNavigate } from 'react-router-dom';
import { useCreateRecipe, useAllRecipes } from '@/hooks/useRecipes';

export function RecipesPage() {
  const navigate = useNavigate();
  const createRecipe = useCreateRecipe();
  const { data: allRecipes } = useAllRecipes(1000);

  const getNextUntitledRecipeName = (): string => {
    if (!allRecipes) return 'Untitled recipe';

    let maxNumber = 0;
    
    allRecipes.forEach((recipe) => {
      if (recipe.name === 'Untitled recipe') {
        // Treat "Untitled recipe" without a number as #1
        maxNumber = Math.max(maxNumber, 1);
      } else {
        const match = recipe.name.match(/^Untitled recipe \((\d+)\)$/);
        if (match) {
          const num = parseInt(match[1], 10);
          maxNumber = Math.max(maxNumber, num);
        }
      }
    });

    if (maxNumber === 0) {
      return 'Untitled recipe';
    }

    return `Untitled recipe (${maxNumber + 1})`;
  };

  const handleCreateRecipe = () => {
    const recipeName = getNextUntitledRecipeName();
    
    createRecipe.mutate(
      {
        name: recipeName,
        status: 'draft',
      },
      {
        onSuccess: (recipe) => {
          navigate(`/recipes/${recipe.id}`, { state: { isNewRecipe: true } });
        },
      },
    );
  };

  return (
    <div className="space-y-6">
      <div className="flex items-start justify-between gap-4">
        <div className="space-y-1">
          <h1 className="text-2xl font-semibold">Recipes</h1>
          <p className="text-muted-foreground">Browse and manage your recipe collection.</p>
        </div>
        <Button
          onClick={handleCreateRecipe}
          disabled={createRecipe.isPending}
          aria-busy={createRecipe.isPending}
        >
          {createRecipe.isPending ? 'Creating...' : 'Create new recipe'}
        </Button>
      </div>
      <RecipeList />
    </div>
  );
}
