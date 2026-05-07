import { useEffect, useState } from 'react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Textarea } from '@/components/ui/textarea';
import { cn } from '@/lib/utils';
import { useUpdateRecipe } from '@/hooks/useRecipes';
import type { RecipeDetail } from '@/types/recipe';

type EditableRecipeField = 'name' | 'description' | 'instructions';

export function InlineEditableRecipeText({
  recipeId,
  field,
  value,
  label,
  multiline = false,
  className,
  displayClassName,
}: {
  recipeId: string;
  field: EditableRecipeField;
  value: string | null | undefined;
  label: string;
  multiline?: boolean;
  className?: string;
  displayClassName?: string;
}) {
  const updateRecipe = useUpdateRecipe();
  const [isEditing, setIsEditing] = useState(false);
  const [draft, setDraft] = useState(value ?? '');
  const [validationError, setValidationError] = useState<string | null>(null);

  useEffect(() => {
    if (!isEditing) {
      setDraft(value ?? '');
      setValidationError(null);
    }
  }, [isEditing, value]);

  const handleSave = () => {
    const nextValue = draft.trim();

    if (field === 'name' && !nextValue) {
      setValidationError('Recipe name is required.');
      return;
    }

    setValidationError(null);

    const payload =
      field === 'name'
        ? ({ id: recipeId, name: nextValue } as Partial<RecipeDetail> & { id: string })
        : ({ id: recipeId, [field]: nextValue || null } as Partial<RecipeDetail> & { id: string });

    updateRecipe.mutate(payload, {
        onSuccess: () => {
          setValidationError(null);
          setIsEditing(false);
        },
      },
    );
  };

  return (
    <div className={cn('space-y-1', className)}>
      {label && <span className="text-xs text-muted-foreground uppercase tracking-wide">{label}</span>}
      {isEditing ? (
        <div className="space-y-2">
          {multiline ? (
            <Textarea
              value={draft}
              onChange={(event) => {
                setDraft(event.target.value);
                if (validationError) {
                  setValidationError(null);
                }
              }}
              autoFocus
            />
          ) : (
            <Input
              value={draft}
              className={cn(field === 'name' && 'h-12 text-2xl font-semibold')}
              onChange={(event) => {
                setDraft(event.target.value);
                if (validationError) {
                  setValidationError(null);
                }
              }}
              autoFocus
            />
          )}
          {validationError && (
            <p className="text-xs text-destructive">{validationError}</p>
          )}
          <div className="flex gap-2">
            <Button 
              size="sm" 
              type="button" 
              onClick={handleSave} 
              disabled={updateRecipe.isPending}>
              Save
            </Button>
            <Button
              size="sm"
              variant="outline"
              type="button"
              onClick={() => {
                setDraft(value ?? '');
                setValidationError(null);
                setIsEditing(false);
              }}
            >
              Cancel
            </Button>
          </div>
        </div>
      ) : value ? (
        <button
          type="button"
          onClick={() => setIsEditing(true)}
          className="block w-full text-left rounded-lg border border-transparent px-2 py-1 -mx-2 -my-1 hover:border-border hover:bg-muted/40 transition-colors"
        >
          {multiline ? (
            <p className={cn('text-sm leading-relaxed whitespace-pre-line', displayClassName)}>{value}</p>
          ) : (
            <p className={cn('text-sm font-medium', displayClassName)}>{value}</p>
          )}
        </button>
      ) : (
        <button
          type="button"
          onClick={() => setIsEditing(true)}
          className="w-full text-left rounded-lg border border-dashed border-border/70 px-2 py-1 text-sm text-muted-foreground/50 italic hover:bg-muted/30 transition-colors"
        >
          Click to add
        </button>
      )}
    </div>
  );
}