import { useParams, useNavigate } from 'react-router-dom';
import { useRecipe } from '@/hooks/useRecipes';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { cn } from '@/lib/utils';

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

  return (
    <div className="space-y-5 max-w-10xl">

      {/* ── Header ─────────────────────────────────────────── */}
      <div className="space-y-4">
        <Button size="sm" onClick={() => navigate('/')}>← Back</Button>
        <div className="flex items-center gap-3 flex-wrap">
          <h1 className="text-2xl font-semibold">{recipe.name}</h1>
          <span className={badgeClass}>{recipe.status}</span>
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
        <TextBlock label="" value={recipe.description} />
      </Section>
      <Section title="Instructions">
        <TextBlock label="" value={recipe.instructions} />
      </Section>
      <Section title="Notes">
        <TextBlock label="" value={recipe.notes} />
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
