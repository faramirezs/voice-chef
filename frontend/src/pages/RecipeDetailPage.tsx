import { useParams, useNavigate } from 'react-router-dom';
import { useRecipe } from '@/hooks/useRecipes';
import { Button } from '@/components/ui/button';
import { Card, CardContent } from '@/components/ui/card';
import { cn } from '@/lib/utils';

const STATUS_STYLES: Record<string, string> = {
  draft: 'bg-yellow-100 text-yellow-800',
  active: 'bg-green-100 text-green-800',
  archived: 'bg-gray-100 text-gray-600',
};

function DetailRow({ label, value }: { label: string; value: string | number | null | undefined }) {
  if (value == null || value === '') return null;
  return (
    <div className="flex flex-col gap-0.5">
      <span className="text-xs text-muted-foreground uppercase tracking-wide">{label}</span>
      <span className="text-sm">{value}</span>
    </div>
  );
}

export function RecipeDetailPage() {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const { data: recipe, isLoading, isError } = useRecipe(id!);

  if (isLoading) {
    return (
      <div className="space-y-4 animate-pulse">
        <div className="h-6 bg-muted rounded w-1/3" />
        <div className="h-4 bg-muted rounded w-1/4" />
        <div className="h-48 bg-muted rounded-lg" />
      </div>
    );
  }

  if (isError || !recipe) {
    return (
      <div className="space-y-4">
        <Button variant="outline" onClick={() => navigate('/')}>← Back to recipes</Button>
        <div className="rounded-lg border border-destructive/50 bg-destructive/10 p-6 text-destructive">
          Recipe not found.
        </div>
      </div>
    );
  }

  const badgeClass = cn(
    'inline-flex items-center rounded-full px-2.5 py-0.5 text-xs font-medium capitalize',
    STATUS_STYLES[recipe.status] ?? 'bg-gray-100 text-gray-600',
  );

  const yieldLabel =
    recipe.yield_amount != null
      ? `${recipe.yield_amount}${recipe.yield_unit ? ` ${recipe.yield_unit}` : ''}`
      : null;

  return (
    <div className="space-y-6 max-w-2xl">
      {/* Header */}
      <div className="space-y-3">
        <Button variant="outline" size="sm" onClick={() => navigate('/')}>
          ← Back
        </Button>
        <div className="flex items-center gap-3">
          <h1 className="text-2xl font-semibold">{recipe.name}</h1>
          <span className={badgeClass}>{recipe.status}</span>
        </div>
        {recipe.description_short && (
          <p className="text-muted-foreground">{recipe.description_short}</p>
        )}
      </div>

      {/* Key stats */}
      <Card>
        <CardContent className="pt-6 grid grid-cols-2 sm:grid-cols-3 gap-6">
          <DetailRow label="Yield" value={yieldLabel} />
          <DetailRow label="Recipe number" value={recipe.recipe_number} />
          <DetailRow label="Batch number" value={recipe.batch_number} />
          <DetailRow label="Portion weight" value={recipe.portion_weight != null ? `${recipe.portion_weight} g` : null} />
          <DetailRow label="Labor effort" value={recipe.labor_effort} />
          <DetailRow label="Storage temp" value={recipe.storage_temperature} />
        </CardContent>
      </Card>

      {/* Description / Instructions */}
      {recipe.description && (
        <div className="space-y-1">
          <h2 className="text-sm font-medium uppercase tracking-wide text-muted-foreground">Description</h2>
          <p className="text-sm leading-relaxed">{recipe.description}</p>
        </div>
      )}

      {recipe.instructions && (
        <div className="space-y-1">
          <h2 className="text-sm font-medium uppercase tracking-wide text-muted-foreground">Instructions</h2>
          <p className="text-sm leading-relaxed whitespace-pre-line">{recipe.instructions}</p>
        </div>
      )}

      {recipe.notes && (
        <div className="space-y-1">
          <h2 className="text-sm font-medium uppercase tracking-wide text-muted-foreground">Notes</h2>
          <p className="text-sm leading-relaxed whitespace-pre-line">{recipe.notes}</p>
        </div>
      )}
    </div>
  );
}
