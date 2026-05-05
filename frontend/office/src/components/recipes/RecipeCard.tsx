import { useNavigate } from 'react-router-dom';
import { cn } from '@/lib/utils';
import type { RecipeSummary } from '@/types/recipe';

const RECIPE_CARD_TITLE_MAX_LENGTH = 64;

function formatRecipeCardTitle(title: string) {
  if (title.length <= RECIPE_CARD_TITLE_MAX_LENGTH) {
    return title;
  }

  return `${title.slice(0, RECIPE_CARD_TITLE_MAX_LENGTH - 1).trimEnd()}…`;
}

const STATUS_STYLES: Record<string, string> = {
  draft: 'bg-yellow-100 text-yellow-800',
  active: 'bg-green-100 text-green-800',
  archived: 'bg-gray-100 text-gray-600',
};


interface RecipeCardProps {
  recipe: RecipeSummary;
}

export function RecipeCard({ recipe }: RecipeCardProps) {
  const navigate = useNavigate();
  const displayTitle = formatRecipeCardTitle(recipe.name);

  // const yieldLabel =
  //   recipe.yield_amount != null
  //     ? `${recipe.yield_amount}${recipe.yield_unit ? ` ${recipe.yield_unit}` : ''}`
  //     : null;

  const badgeClass = cn(
    'inline-flex items-center rounded-full px-2 py-0.5 text-xs font-medium capitalize',
    STATUS_STYLES[recipe.status] ?? 'bg-gray-100 text-gray-600',
  );

  return (
    <div
      onClick={() => navigate(`/recipes/${recipe.id}`)}
      className="rounded-lg border bg-card overflow-hidden cursor-pointer hover:shadow transition"
    >
      {/* IMAGE */}
      {recipe.photo_url ? (
        <img
          key={recipe.photo_url}
          src={`/api/recipe_images/${recipe.id}?v=${new Date(recipe.updated_at).getTime()}`}
          alt={displayTitle}
          className="w-full h-32 object-cover"
        />
      ) : (
        <div className="w-full h-32 bg-muted flex items-center justify-center text-xs text-muted-foreground">
          No Image
        </div>
      )}

      {/* CONTENT */}
      <div className="p-3 space-y-2">
        <div className="flex items-center justify-between gap-2">
          <h3 className="font-medium text-sm leading-tight line-clamp-2">
            {displayTitle}
          </h3>

          <span className={badgeClass}>
            {recipe.status}
          </span>
        </div>
      </div>
    </div>
  );
}
