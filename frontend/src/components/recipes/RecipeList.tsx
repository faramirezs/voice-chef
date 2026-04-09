import { useState } from 'react';
import { useRecipes } from '@/hooks/useRecipes';
import { RecipeCard } from './RecipeCard';
import { Input } from '@/components/ui/input';

function RecipeSkeleton() {
  return (
    <div className="rounded-lg border bg-card p-4 space-y-3 animate-pulse">
      <div className="flex justify-between gap-2">
        <div className="h-4 bg-muted rounded w-3/4" />
        <div className="h-4 bg-muted rounded w-12" />
      </div>
      <div className="h-3 bg-muted rounded w-1/2" />
    </div>
  );
}

export function RecipeList() {
  const [statusFilter, setStatusFilter] = useState('');
  const [nameFilter, setNameFilter] = useState('');

  const { data: recipes, isLoading, isError, error } = useRecipes(
    statusFilter ? { status: statusFilter } : undefined,
  );

  const normalizedNameFilter = nameFilter.trim().toLowerCase();
  const visibleRecipes = recipes?.filter((recipe) => {
    if (!normalizedNameFilter) {
      return true;
    }

    return recipe.name.toLowerCase().includes(normalizedNameFilter);
  });

  return (
    <div className="space-y-4">
      <div className="flex items-center gap-3">
        <Input
          placeholder="Filter by name..."
          className="max-w-sm"
          value={nameFilter}
          onChange={(e) => setNameFilter(e.target.value)}
        />
        <Input
          placeholder="Filter by status (e.g. draft, active)…"
          className="max-w-sm"
          value={statusFilter}
          onChange={(e) => setStatusFilter(e.target.value)}
        />
        {!isLoading && visibleRecipes && (
          <span className="text-sm text-muted-foreground">
            {visibleRecipes.length} recipe{visibleRecipes.length !== 1 ? 's' : ''}
          </span>
        )}
      </div>

      {isError && (
        <div className="rounded-lg border border-destructive/50 bg-destructive/10 p-4 text-sm text-destructive">
          Failed to load recipes:{' '}
          {error instanceof Error ? error.message : 'Unknown error'}
        </div>
      )}

      {isLoading && (
        <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-3">
          {Array.from({ length: 6 }).map((_, i) => (
            <RecipeSkeleton key={i} />
          ))}
        </div>
      )}

      {!isLoading && !isError && visibleRecipes?.length === 0 && (
        <div className="rounded-lg border border-dashed p-8 text-center text-muted-foreground">
          No recipes found.
        </div>
      )}

      {!isLoading && visibleRecipes && visibleRecipes.length > 0 && (
        <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-6">
          {visibleRecipes.map((recipe) => (
            <RecipeCard key={recipe.id} recipe={recipe} />
          ))}
        </div>
      )}
    </div>
  );
}
