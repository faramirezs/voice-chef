import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useCreateRecipe } from '@/hooks/useRecipes';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Section } from '@/components/Section';
import { cn } from '@/lib/utils';

const STATUS_STYLES: Record<string, string> = {
  draft: 'bg-yellow-100 text-yellow-800',
  active: 'bg-green-100 text-green-800',

};


export function CreateRecipePage() {
  const navigate = useNavigate();
  const createRecipe = useCreateRecipe();

  const [name, setName] = useState('');
  const [error, setError] = useState<string | null>(null);
  const draftStatus = 'draft';

  const handleSave = () => {
    const trimmedName = name.trim();

    if (!trimmedName) {
      setError('Recipe name is required.');
      return;
    }
    setError(null);
    createRecipe.mutate({name: trimmedName, status: 'draft',},
      {
        onSuccess: (recipe) => {
          navigate(`/recipes/${recipe.id}`);
        },
      },
    );
  };

  const badgeClass = cn(
    'inline-flex items-center rounded-full px-2.5 py-0.5 text-xs font-medium capitalize',
    STATUS_STYLES[draftStatus] ?? 'bg-gray-100 text-gray-600',
  );

  return (
    <div className="space-y-5 max-w-10xl">
      {/* Header Section */}
      <div className="flex items-center justify-between">
        <h1 className="text-3xl font-bold">Create New Recipe</h1>
        <div className="flex items-center gap-2">
          <Button
            size="lg"
            variant="outline"
            onClick={() => navigate('/recipes/')}
            className="text-gray-600"
          >
            Cancel
          </Button>
          <Button
            size="lg"
            type="button"
            onClick={handleSave}
            disabled={createRecipe.isPending}
            aria-busy={createRecipe.isPending}
          >
            {createRecipe.isPending ? 'Saving...' : 'Save'}
          </Button>
        </div>
      </div>

      {/* Content Section - Two Columns */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-10 items-start">
        {/* Left column - Basic Info */}
        <div className="lg:col-span-4">
          <Section title="Basic Info">
            <div className="space-y-4">
              <div className="space-y-1">
                <Input
                  id="recipe-name"
                  value={name}
                  onChange={(event) => {
                    setName(event.target.value);
                    if (error) {
                      setError(null);
                    }
                  }}
                  placeholder="Untitled recipe"
                  className="h-12 text-lg font-semibold"
                  autoFocus
                />
                {error && <p className="text-xs text-destructive">{error}</p>}
              </div>
              <div className="flex items-center">
                <span className={badgeClass}>{draftStatus}</span>
              </div>
            </div>
          </Section>
        </div>

        {/* Right column - Ingredients */}
        <div className="lg:col-span-8">
          <Section title="Ingredients">
            <p className="text-sm text-muted-foreground italic">Ingredients input coming soon.</p>
          </Section>
        </div>
      </div>
    </div>
  );
}
