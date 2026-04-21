import { useEffect, useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { useDeleteRecipe, useRecipe, useUpdateRecipe } from '@/hooks/useRecipes';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Textarea } from '@/components/ui/textarea';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { cn } from '@/lib/utils';
import recipeImage from '@/assets/voice-chef-recipe.jpg';
import type { Recipe } from '@/types/recipe';

const STATUS_STYLES: Record<string, string> = {
  draft: 'bg-yellow-100 text-yellow-800',
  active: 'bg-green-100 text-green-800',
  archived: 'bg-gray-100 text-gray-600',
};

function DetailRow({ label, value }: { label: string; value: string | number | boolean | null | undefined }) {
  const isEmpty = value == null || value === '';
  const display = isEmpty
    ? null
    : typeof value === 'boolean'
    ? value ? 'Yes' : 'No'
    : String(value);
  return (
    <div className="flex flex-col gap-0.5">
      <span className="text-xs text-muted-foreground uppercase tracking-wide">{label}</span>
      {isEmpty
        ? <span className="text-sm text-muted-foreground/50 italic">empty</span>
        : <span className="text-sm font-medium">{display}</span>
      }
    </div>
  );
}

function Section({ title, children }: { title: string; children: React.ReactNode }) {
  return (
    <Card>
      <CardHeader className="pb-2">
        <CardTitle className="text-sm uppercase tracking-wide text-muted-foreground font-medium">
          {title}
        </CardTitle>
      </CardHeader>
      <CardContent>{children}</CardContent>
    </Card>
  );
}

function Grid({ children }: { children: React.ReactNode }) {
  return <div className="grid grid-cols-2 sm:grid-cols-3 gap-x-6 gap-y-4">{children}</div>;
}

type EditableRecipeField = 'name' | 'description' | 'instructions';

function InlineEditableText({
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
        ? ({ id: recipeId, name: nextValue } as Partial<Recipe> & { id: string })
        : ({ id: recipeId, [field]: nextValue || null } as Partial<Recipe> & { id: string });

    updateRecipe.mutate(
      payload,
      {
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
            <Button size="sm" type="button" onClick={handleSave} disabled={updateRecipe.isPending}>
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

function TextBlock({ label, value }: { label: string; value: string | null | undefined }) {
  return (
    <div className="space-y-1">
      {label && <span className="text-xs text-muted-foreground uppercase tracking-wide">{label}</span>}
      {value
        ? <p className="text-sm leading-relaxed whitespace-pre-line">{value}</p>
        : <p className="text-sm text-muted-foreground/50 italic">empty</p>
      }
    </div>
  );
}

function formatDate(value: string | null | undefined) {
  if (!value) return null;
  return new Date(value).toLocaleDateString(undefined, { year: 'numeric', month: 'short', day: 'numeric' });
}

function formatDatetime(value: string | null | undefined) {
  if (!value) return null;
  return new Date(value).toLocaleString(undefined, { year: 'numeric', month: 'short', day: 'numeric', hour: '2-digit', minute: '2-digit' });
}


export function RecipeDetailPage() {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const { data: recipe, isLoading, isError } = useRecipe(id!);
  const moveToActive = useUpdateRecipe();
  const deleteRecipe = useDeleteRecipe();

  const handleMoveToActive = () => {
    if (!recipe) {
      return;
    }

    moveToActive.mutate({
      id: recipe.id,
      status: recipe.status === 'active' ? 'draft' : 'active',
    });
  };

  const handleDeleteRecipe = () => {
    if (!recipe) {
      return;
    }

    const confirmed = window.confirm(
      `Delete recipe "${recipe.name}"? This cannot be undone.`,
    );

    if (!confirmed) {
      return;
    }

    deleteRecipe.mutate(recipe.id, {
      onSuccess: () => {
        navigate('/recipes');
      },
    });
  };

  if (isLoading) {
    return (
      <div className="space-y-4 animate-pulse max-w-3xl">
        <div className="h-6 bg-muted rounded w-1/3" />
        <div className="h-4 bg-muted rounded w-1/4" />
        <div className="h-32 bg-muted rounded-lg" />
        <div className="h-32 bg-muted rounded-lg" />
      </div>
    );
  }

  if (isError || !recipe) {
    return (
      <div className="space-y-4">
        <Button variant="outline" onClick={() => navigate(-1)}>← Back to recipes</Button>
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

  return (
    <div className="space-y-5 max-w-10xl">

      {/* ── Header ─────────────────────────────────────────── */}
      <div className="space-y-4">
        <Button size="sm" onClick={() => navigate(-1)}>← Back</Button>
        <div
          className="h-72 w-full overflow-hidden rounded-xl border bg-cover bg-center bg-no-repeat"
          style={{ backgroundImage: `url(${recipeImage})` }}
          aria-hidden="true"
        />
        <div className="flex items-center gap-3 flex-wrap">
          <InlineEditableText
            recipeId={recipe.id}
            field="name"
            value={recipe.name}
            label=""
            className="w-full sm:w-auto sm:min-w-[28rem]"
            displayClassName="text-2xl font-semibold"
          />
          <span className={badgeClass}>{recipe.status}</span>
        </div>
        <div className="flex flex-wrap gap-3">
          <Button
            size="lg"
            type="button"
            className="min-w-40"
            onClick={handleMoveToActive}
            disabled={moveToActive.isPending}
            aria-busy={moveToActive.isPending}
          >
            Change status
          </Button>
          <Button size="lg" onClick={() => alert('Edit recipe functionality coming soon!')}>
            Edit recipe
          </Button>
          <Button size="lg" variant="outline" onClick={() => alert('Duplicate recipe functionality coming soon!')}>
            Duplicate recipe
          </Button>
          <Button
            size="lg"
            variant="destructive"
            onClick={handleDeleteRecipe}
            disabled={deleteRecipe.isPending}
            aria-busy={deleteRecipe.isPending}
          >
            Delete recipe
          </Button>
        </div>
        {recipe.description_short && (
          <p className="text-muted-foreground">{recipe.description_short}</p>
        )}
      </div>

      {/* ── Identity ───────────────────────────────────────── */}
      <Section title="Identity">
        <Grid>
          <DetailRow label="ID" value={recipe.id} />
          <DetailRow label="Recipe number" value={recipe.recipe_number} />
          <DetailRow label="Batch number" value={recipe.batch_number} />
          <DetailRow label="Is component" value={recipe.is_component} />
          <DetailRow label="Created" value={formatDatetime(recipe.created_at)} />
          <DetailRow label="Updated" value={formatDatetime(recipe.updated_at)} />
        </Grid>
      </Section>

              {/* ── Long-form text ─────────────────────────────────── */}
      <Section title="Description">
        <InlineEditableText
          recipeId={recipe.id}
          field="description"
          value={recipe.description}
          label=""
          multiline
        />
      </Section>
      <Section title="Notes">
        <TextBlock label="" value={recipe.notes} />
      </Section>
      <Section title="Instructions">
        <InlineEditableText
          recipeId={recipe.id}
          field="instructions"
          value={recipe.instructions}
          label=""
          multiline
        />
      </Section>
      <Section title="Notes on Instructions">
        <TextBlock label="" value={recipe.notes_instructions} />
      </Section>

      {/* ── Yield & Weights ────────────────────────────────── */}
      <Section title="Yield & Weights">
          <Grid>
            <DetailRow label="Yield" value={recipe.yield_amount != null ? `${recipe.yield_amount}${recipe.yield_unit ? ` ${recipe.yield_unit}` : ''}` : null} />
            <DetailRow label="Reduction factor" value={recipe.reduction_factor} />
            <DetailRow label="Eigene Menge" value={recipe.eigene_menge} />
            <DetailRow label="Net weight (g)" value={recipe.net_weight} />
            <DetailRow label="Fill weight (g)" value={recipe.fill_weight} />
            <DetailRow label="Fill quantity" value={recipe.fill_quantity} />
            <DetailRow label="Drained weight (g)" value={recipe.drained_weight} />
            <DetailRow label="Total weight (g)" value={recipe.total_weight} />
            <DetailRow label="Portion weight (g)" value={recipe.portion_weight} />
            <DetailRow label="Portion by weight" value={recipe.portion_by_weight} />
            <DetailRow label="Unit of measure" value={recipe.unit_measure} />
            <DetailRow label="Serving unit" value={recipe.unit_serving} />
          </Grid>
        </Section>

      {/* ── Production & Dates ─────────────────────────────── */}
      <Section title="Production & Dates">
          <Grid>
            <DetailRow label="Production date" value={formatDate(recipe.production_date)} />
            <DetailRow label="Use-by date" value={formatDate(recipe.use_by_date)} />
            <DetailRow label="Expiry date" value={formatDate(recipe.expiry_date)} />
            <DetailRow label="Storage temperature" value={recipe.storage_temperature} />
            <DetailRow label="Labor effort" value={recipe.labor_effort} />
            <DetailRow label="Mise en place display" value={recipe.mise_en_place_display} />
          </Grid>
        </Section>

      {/* ── Serving ────────────────────────────────────────── */}
      <Section title="Serving">
          <div className="space-y-3">
            <TextBlock label="Serving recommendation" value={recipe.serving_recommendation} />
            <TextBlock label="Side dishes" value={recipe.side_dishes} />
          </div>
        </Section>

      {/* ── Packaging ──────────────────────────────────────── */}
      <Section title="Packaging">
          <Grid>
            <DetailRow label="Packaging" value={recipe.packaging} />
            <DetailRow label="Packaging material" value={recipe.packaging_material} />
          </Grid>
        </Section>

      {/* ── Origin ─────────────────────────────────────────── */}
      <Section title="Origin">
          <Grid>
            <DetailRow label="Fish origin" value={recipe.origin_fish} />
            <DetailRow label="Location" value={recipe.origin_location} />
          </Grid>
        </Section>

      {/* ── Equipment ──────────────────────────────────────── */}
      <Section title="Equipment">
          <div className="space-y-3">
            <TextBlock label="Devices" value={recipe.devices} />
            <TextBlock label="Utensils" value={recipe.utensils} />
          </div>
        </Section>

      {/* ── Nutrition ──────────────────────────────────────── */}
      <Section title="Nutrition & Margins">
          <Grid>
            <DetailRow label="Nutri-score category" value={recipe.nutri_score_category} />
            <DetailRow label="Nutri-score veg/fruits (%)" value={recipe.nutri_score_veg_fruits} />
            <DetailRow label="Preference nutri value" value={recipe.preference_nutri_value} />
            <DetailRow label="Margin" value={recipe.margin} />
          </Grid>
        </Section>

      {/* ── Allergens & Ingredients ────────────────────────── */}
      <Section title="Allergens & Ingredients">
          <div className="space-y-3">
            <TextBlock label="Allergen source" value={recipe.allergene_source} />
            <TextBlock label="Custom ingredient list" value={recipe.ingredient_list_custom} />
          </div>
        </Section>

      {/* ── Storage ────────────────────────────────────────── */}
      <Section title="Storage">
        <TextBlock label="" value={recipe.storage_text} />
      </Section>



    </div>
  );
}
