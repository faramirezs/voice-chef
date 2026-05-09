import { useParams, useNavigate } from 'react-router-dom';
import { useEffect, useRef, useState } from 'react';
import { useQueryClient } from '@tanstack/react-query';
import { 
  useDeleteRecipe, 
  useRecipe, 
  useUpdateRecipe, 
  useUploadRecipePicture, 
  useDeleteRecipePicture } from '@/hooks/useRecipes';
import { Button } from '@/components/ui/button';
import { InlineEditableRecipeText } from '../components/recipes/InlineEditableRecipeText';
import { Section } from '../components/Section';
import { formatDatetime } from '../components/Format-Datetime.tsx';
import { DetailRow } from '../components/Detail-row';
import { Grid } from '../components/Grid';
import { cn } from '@/lib/utils';

const STATUS_STYLES: Record<string, string> = {
  draft: 'bg-yellow-100 text-yellow-800',
  active: 'bg-green-100 text-green-800',
  archived: 'bg-gray-100 text-gray-600',
};


export function RecipeDetailPage() {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const queryClient = useQueryClient();
  const deleteRecipe = useDeleteRecipe();
  // TanStack Query is very sensitive to the enabled flag. As soon as you click 
  // the "Delete" button and the backend returns 204, the deleteMutation.isSuccess 
  // status instantly becomes true.
  const { data: recipe, isLoading, isError } = useRecipe(id!, {
    enabled: !deleteRecipe.isSuccess
  });
  const moveToActive = useUpdateRecipe();
  const uploadPhoto = useUploadRecipePicture();
  const deletePhoto = useDeleteRecipePicture();
  const fileInputRef = useRef<HTMLInputElement>(null);
  const [uploadError, setUploadError] = useState<string | null>(null);

  // Navigate away immediately after successful deletion
  useEffect(() => {
    if (deleteRecipe.isSuccess) {
      // Remove the recipe from cache immediately to prevent "not found" error
      queryClient.removeQueries({ queryKey: ['recipe', id] });
      // Navigate away
      navigate('/recipes');
    }
  }, [deleteRecipe.isSuccess, navigate, queryClient, id]);

  const handleMoveToActive = () => {
    if (!recipe) { return; }

    moveToActive.mutate({
      id: recipe.id,
      status: recipe.status === 'active' ? 'draft' : 'active',
    });
  };

  const handleDeleteRecipe = () => {
    if (!recipe) return;

    const confirmed = window.confirm(
      `Delete recipe "${recipe.name}"? This cannot be undone.`,
    );

    if (!confirmed) return;

    deleteRecipe.mutate(recipe.id);
  };

  const handlePhotoClick = () => {
    fileInputRef.current?.click();
  };

  const handleFileSelect = (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (!file) return;

    const validateImage = (f: File) => {
      const ALLOWED_TYPES = ['image/jpeg', 'image/png'];
      const MAX_SIZE_MB = 1;
      const MAX_SIZE = MAX_SIZE_MB * 1024 * 1024; // 10MB
      const MIN_DIM = 200;
      const MAX_DIM = 6000;

      return new Promise<void>((resolve, reject) => {
        if (!ALLOWED_TYPES.includes(f.type)) {
          reject('Only JPG, JPEG and PNG images are allowed');
          return;
        }

        if (f.size === 0) {
          reject('File is empty');
          return;
        }

        if (f.size > MAX_SIZE) {
          reject(`File size exceeds the limit of ${MAX_SIZE_MB}MB`);
          return;
        }

        const url = URL.createObjectURL(f);
        const img = new Image();
        img.onload = () => {
          const { width, height } = img;
          URL.revokeObjectURL(url);
          if (width < MIN_DIM || height < MIN_DIM) {
            reject(`Image dimensions too small. Minimum is ${MIN_DIM}x${MIN_DIM}px`);
            return;
          }
          if (width > MAX_DIM || height > MAX_DIM) {
            reject(`Image dimensions too large. Maximum is ${MAX_DIM}x${MAX_DIM}px`);
            return;
          }
          // simple format verification by attempting to draw to canvas (detects some corruptions)
          try {
            const canvas = document.createElement('canvas');
            canvas.width = width;
            canvas.height = height;
            const ctx = canvas.getContext('2d');
            if (!ctx) {
              // if no context, still accept (uncommon)
              resolve();
              return;
            }
            ctx.drawImage(img, 0, 0);
            // attempt to read a few pixels
            ctx.getImageData(0, 0, 1, 1);
            resolve();
          } catch (err) {
            reject('Invalid or corrupted image file');
          }
        };
        img.onerror = () => {
          URL.revokeObjectURL(url);
          reject('Invalid or corrupted image file');
        };
        img.src = url;
      });
    };

    setUploadError(null);
    if (recipe) {
      validateImage(file)
        .then(() => {
          uploadPhoto.mutate({ id: recipe.id, file });
        })
        .catch((err) => {
          setUploadError(typeof err === 'string' ? err : 'Invalid image file');
        })
        .finally(() => {
          if (fileInputRef.current) fileInputRef.current.value = '';
        });
    }
  };

  const handleDeletePhoto = () => {
    if (!recipe?.photo_url) { return; }

    const confirmed = window.confirm('Delete this recipe picture?');
    if (!confirmed) { return; }

    deletePhoto.mutate(recipe.id);
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

  // Show error only if recipe genuinely doesn't exist (not during deletion)
  if (isError && !deleteRecipe.isPending && !deleteRecipe.isSuccess) {
    return (
      <div className="space-y-4">
        <Button variant="outline" onClick={() => navigate('/recipes')}>← Back to recipes</Button>
        <div className="rounded-lg border border-destructive/50 bg-destructive/10 p-6 text-destructive">
          Recipe not found.
        </div>
      </div>
    );
  }

  // If recipe data is missing but we're not in an error state, don't render
  if (!recipe) {
    return null;
  }

  const badgeClass = cn(
    'inline-flex items-center rounded-full px-2.5 py-0.5 text-xs font-medium capitalize',
    STATUS_STYLES[recipe.status] ?? 'bg-gray-100 text-gray-600',
  );

  return (
    <div className="space-y-5 max-w-10xl">

      {/* ── Header ─────────────────────────────────────────── */}
      <div className="space-y-3">
        <Button size="sm" onClick={() => navigate('/recipes')}>← Back</Button>
        <div
          className="h-72 w-full overflow-hidden rounded-xl border cursor-pointer relative hover:opacity-80 transition-opacity bg-muted flex items-center justify-center"
          onClick={handlePhotoClick}
        >
          {uploadPhoto.isPending && (
            <div className="absolute inset-0 bg-black/50 flex items-center justify-center z-10">
              <div className="text-white text-sm">Uploading...</div>
            </div>
          )}
          {recipe.photo_url ? (
            <img
              key={recipe.photo_url}
              src={`/api/recipe_images/${recipe.id}?v=${new Date(recipe.updated_at).getTime()}`}
              alt={recipe.name}
              className="w-full h-full object-cover"
            />
          ) : (
            <div className="text-center text-muted-foreground">
              <p className="text-lg font-medium">Click here to upload a picture</p>
            </div>
          )}
        </div>
        <input
          ref={fileInputRef}
          type="file"
          accept="image/*"
          onChange={handleFileSelect}
          className="hidden"
          disabled={uploadPhoto.isPending}
        />
        {uploadError && (
          <div className="mt-2 rounded-lg border border-destructive/50 bg-destructive/10 p-3 text-sm text-destructive">
            {uploadError}
          </div>
        )}
        <div className="flex items-center gap-3 flex-wrap">
          <InlineEditableRecipeText
            recipeId={recipe.id}
            field="name"
            value={recipe.name}
            label=""
            className="w-full sm:w-auto sm:min-w-[28rem]"
            displayClassName="text-2xl font-semibold"
          />
          <span className={badgeClass}>{recipe.status}</span>
        </div>
        <div className="flex flex-wrap gap-3 justify-between">
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
            {/* <Button size="lg" onClick={() => alert('Edit recipe functionality coming soon!')}>
              Edit
            </Button>
            <Button size="lg" variant="outline" onClick={() => alert('Duplicate recipe functionality coming soon!')}>
              Duplicate
            </Button> */}
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
          <div className="flex flex-wrap gap-3">
            {recipe.photo_url && (
              <Button
                size="lg"
                variant="destructive"
                onClick={handleDeletePhoto}
                disabled={deletePhoto.isPending}
                aria-busy={deletePhoto.isPending}
              >
                {deletePhoto.isPending ? 'Deleting...' : 'Delete picture'}
              </Button>
            )}
          </div>
        </div>
      </div>

      {/* <Section title="preparation_time_minutes">
        preparation_time_minutes
      </Section> */}

      {/* ── 4 cols: preparation_time_minutes ── */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-10 items-start">

      {/* 1 column */}
      <div className="lg:col-span-3">
       <Section title="PREP TIME">
        {recipe.preparation_time_minutes}
        {(!recipe.preparation_time_minutes || recipe.preparation_time_minutes === 0) && (
          <p className="text-sm text-muted-foreground italic">No preparation time minutes added yet.</p>
          )}
       </Section>
      </div>

      {/* column 2 */}
      <div className="lg:col-span-3">
       <Section title="COOK TIME">
        {recipe.cooking_time_minutes}
        {(!recipe.cooking_time_minutes || recipe.cooking_time_minutes === 0) && (
          <p className="text-sm text-muted-foreground italic">No cooking time minutes added yet.</p>
          )}
       </Section>
      </div>
      {/* column 3 */}
      <div className="lg:col-span-3">
       <Section title="SERVINGS">
        {/* Ternary operator for conditional rendering to ensure the math 
        only happens if a valid value exists. */}
        {recipe.portions_count_resolved ? (
          // Only render the number if portion_size_grams is not null or empty
          Math.round(Number(recipe.portions_count_resolved))
        ) : (
          // Fallback message if it is null, 0, or an empty string
          <p className="text-sm text-muted-foreground italic">No portions count resolved added yet.</p>
        )}
       </Section>
      </div>
      {/* column 4 */}
      <div className="lg:col-span-3">
       <Section title="PORTION SIZE">
        {recipe.portion_size_grams ? (
          Math.round(Number(recipe.portion_size_grams))
        ) : (
          <p className="text-sm text-muted-foreground italic">
            No portion size grams resolved added yet.
          </p>
        )}
       </Section>
      </div>
    </div>

      {/* ── Long-form text ─────────────────────────────────── */}
      <Section title="Description">
        <InlineEditableRecipeText
          recipeId={recipe.id}
          field="description"
          value={recipe.description}
          label=""
          multiline
        />
      </Section>

      {/* ── Main Content: Ingredients & Instructions Column ── */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-10 items-start">

      {/* Left column */}
      {/* ── Ingredients ───────────────────────────────────────── */}
      <div className="lg:col-span-4">
       <Section title="Ingredients">
        <div className="">
          <ul className="list-disc ml-5 space-y-1 text-black">
             {recipe.ingredients?.map(({ id, ingredient_name, quantity, unit }) => (
            <li key={id} className="border-b border-dashed pb-1.5 text-sm">
              <div className="flex justify-between w-full">
                <span className="font-medium">
                  {ingredient_name}
                </span>
                <span className="text-muted-foreground ml-4 whitespace-nowrap">
                  {Math.round(Number(quantity))} {unit}
                </span>
              </div>
            </li>
          ))}
          {(!recipe.ingredients || recipe.ingredients.length === 0) && (
          <p className="text-sm text-muted-foreground italic">No ingredients added yet.</p>
         )}
         </ul>
        </div>
       </Section>
      </div>
      

      {/* Right column */}
      <div className="lg:col-span-8">
       <Section title="Instructions">
        <div className="min-h-[200px]">
          <InlineEditableRecipeText
            recipeId={recipe.id}
            field="instructions"
            value={recipe.instructions}
            label=""
            multiline
          />
        </div>
       </Section>
      </div>
    </div>

         {/* ── Identity ───────────────────────────────────────── */}
      <Section title="Identity">
        <Grid>
          <DetailRow label="ID" value={recipe.id} />
          <DetailRow label="Is component" value={recipe.is_component} />
          <DetailRow label="Created" value={formatDatetime(recipe.created_at)} />
          <DetailRow label="Updated" value={formatDatetime(recipe.updated_at)} />
        </Grid>
      </Section>
      {/* <Section title="yield_mode">
        yield_mode
      </Section> */}
      {/* <Section title="total_raw_weight_grams">
        total_raw_weight_grams
      </Section> */}
      {/* <Section title="photo_url">
        photo_url
      </Section> */}
      {/* ── Yield & Weights ────────────────────────────────── */}
      <Section title="Yield & Weights">
          <Grid>
            {/* <DetailRow label="Yield" value={recipe.yield_amount != null ? `${recipe.yield_amount}${recipe.yield_unit ? ` ${recipe.yield_unit}` : ''}` : null} /> */}
            {/* <DetailRow label="Reduction factor" value={recipe.reduction_factor} /> */}
            <DetailRow label="Total cooked weight (g)" value={recipe.total_cooked_weight_grams} />
          </Grid>
        </Section>
    </div>
  );
}