import { useNavigate } from 'react-router-dom';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { cn } from '@/lib/utils';
import type { Recipe } from '@/types/recipe';

const STATUS_STYLES: Record<string, string> = {
  draft: 'bg-yellow-100 text-yellow-800',
  active: 'bg-green-100 text-green-800',
  archived: 'bg-gray-100 text-gray-600',
};

function ImagePlaceholder({ onView }: { onView: () => void }) {
  return (
    <div className="relative w-full h-36 bg-gradient-to-br from-orange-100 via-amber-50 to-yellow-100 flex items-center justify-center">
      <svg
        xmlns="http://www.w3.org/2000/svg"
        className="w-18 h-18 text-orange-300"
        viewBox="0 0 24 24"
        fill="none"
        stroke="currentColor"
        strokeWidth="2"
        strokeLinecap="round"
        strokeLinejoin="round"
      >
        <line x1="8" y1="2" x2="8" y2="6" />
        <line x1="6" y1="2" x2="6" y2="6" />
        <line x1="10" y1="2" x2="10" y2="6" />
        <path d="M6 6a2 2 0 0 0 2 2h0a2 2 0 0 0 2-2" />
        <line x1="8" y1="8" x2="8" y2="22" />
        <path d="M16 2l2 4-4 4 2 12" />
      </svg>

      {/* Eye icon button */}
      {/* <button
        onClick={(e) => { e.stopPropagation(); onView(); }}
        className="absolute top-1 right-1 rounded-full text-gray-200 hover:text-gray-400 transition-colors"
        aria-label="View recipe"
      >
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" className="w-4 h-4">
          <path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z" />
          <circle cx="12" cy="12" r="4" />
        </svg>
      </button> */}
    </div>
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
    <Card className="hover:shadow-md transition-shadow cursor-pointer pt-0 gap-2" onClick={() => navigate(`/recipes/${recipe.id}`)}>
      <ImagePlaceholder onView={() => navigate(`/recipes/${recipe.id}`)} />
      <CardHeader className="pb-2">
        <div className="flex items-start justify-between gap-2">
          <CardTitle className="text-base leading-snug">{recipe.name}</CardTitle>
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
