import { useNavigate } from 'react-router-dom';
import { Card, CardHeader, CardTitle } from '@/components/ui/card';
import { cn } from '@/lib/utils';
import type { Recipe } from '@/types/recipe';
import recipeImage from '@/assets/voice-chef-recipe.jpg';

const STATUS_STYLES: Record<string, string> = {
  draft: 'bg-yellow-100 text-yellow-800',
  active: 'bg-green-100 text-green-800',
  archived: 'bg-gray-100 text-gray-600',
};

function ImagePlaceholder() {
  return (
    <div
      className="relative flex h-36 w-full items-center justify-center overflow-hidden bg-cover bg-center bg-no-repeat"
      style={{ backgroundImage: `url(${recipeImage})` }}
      aria-hidden="true"
    />
  );
}

interface RecipeCardProps {
  recipe: Recipe;
}

export function RecipeCard({ recipe }: RecipeCardProps) {
  const navigate = useNavigate();

  // const yieldLabel =
  //   recipe.yield_amount != null
  //     ? `${recipe.yield_amount}${recipe.yield_unit ? ` ${recipe.yield_unit}` : ''}`
  //     : null;

  const badgeClass = cn(
    'inline-flex items-center rounded-full px-2 py-0.5 text-xs font-medium capitalize',
    STATUS_STYLES[recipe.status] ?? 'bg-gray-100 text-gray-600',
  );

  return (
    <Card className="h-[16.5rem] cursor-pointer gap-2 pt-0 hover:scale-[1.02] hover:animate-pulse hover:shadow-lg" onClick={() => navigate(`/recipes/${recipe.id}`)}>
      <ImagePlaceholder />
      <CardHeader className="pb-2 h-full">
        <div className="flex h-full items-start justify-between gap-2">
          <CardTitle className="flex-1 text-base leading-snug break-words">{recipe.name}</CardTitle>
          <span className={badgeClass}>{recipe.status}</span>
        </div>
      </CardHeader>
      {/* <CardContent className="text-sm text-muted-foreground space-y-1">
        {yieldLabel && (
          <p>
            <span className="font-medium text-foreground">Yield:</span> {yieldLabel}
          </p>
        )}
        {recipe.recipe_number && (
          <p className="text-xs font-mono">#{recipe.recipe_number}</p>
        )}
      </CardContent> */}
    </Card>
  );
}
