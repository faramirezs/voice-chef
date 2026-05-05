import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useCreateRecipe } from '@/hooks/useRecipes';
import { useIngredientsAutocomplete } from '@/hooks/useIngredients';
import { Combobox, type ComboboxOption } from '@/components/ui/combobox';
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

  // creating `ingredients` variable that will change, 
  // and the `setIngredients` function to update it
  const [ingredients, setIngredients] = useState<Array<{ 
    id: string; 
    ingredientId: string | null; 
    name: string; 
    quantity: string | null 
  }>>([]);
  const [searchQuery, setSearchQuery] = useState('');
  // useIngredientsAutocomplete
  const { 
    data: autocompleteResults = [], 
    isLoading: isLoadingAutocomplete 
  } = useIngredientsAutocomplete(searchQuery);
  const draftStatus = 'draft';

  const handleSave = () => {
    const trimmedName = name.trim();

    if (!trimmedName) {
      setError('Recipe name is required.');
      return;
    }
    setError(null);

    // Filter out ingredients without an ingredientId
    const validIngredients = ingredients
      .filter(ingredient => ingredient.ingredientId !== null)
      .map((ingredient, index) => ({
        ingredient_id: ingredient.ingredientId!,
        quantity: ingredient.quantity || undefined,
        unit: 'g',
        sort_order: index,
      }));

    createRecipe.mutate(
      {
        name: trimmedName,
        status: 'draft',
        ingredients: validIngredients,
      },
      {
        onSuccess: (recipe) => {
          navigate(`/recipes/${recipe.id}`);
        },
      },
    );
  };

  const addIngredientRow = () => {
    const newId = Date.now().toString();
    setIngredients([
      ...ingredients, { 
        id: newId, 
        ingredientId: null, 
        name: '', 
        quantity: null }
      ]);
  };

  const removeIngredientRow = (id: string) => {
    setIngredients(ingredients.filter(ingredient => ingredient.id !== id));
  };

  const selectIngredient = (id: string, ingredientId: string, ingredientName: string) => {
    setIngredients(ingredients.map(ingredient =>
      ingredient.id === id ? { ...ingredient, ingredientId, name: ingredientName } : ingredient
    ));
    setSearchQuery('');
  };

  // Convert autocomplete results to combobox options
  const comboboxOptions: ComboboxOption[] = autocompleteResults.map(result => ({
    value: result.id,
    label: result.name,
  }));

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
            <div className="space-y-3">
              {ingredients.map((ingredient) => (
                <div key={ingredient.id} className="space-y-1">
                  <div className="flex items-center gap-2">
                    <div className="flex-1">
                      <Combobox
                        options={comboboxOptions}
                        value={ingredient.ingredientId || ''}
                        onValueChange={(value) => {
                          const selected = autocompleteResults.find(r => r.id === value);
                          if (selected) {
                            selectIngredient(ingredient.id, selected.id, selected.name);
                          }
                        }}
                        onSearchChange={setSearchQuery}
                        placeholder={ingredient.name || 'Click here to search'}
                        searchPlaceholder="Type to search..."
                        emptyText="No ingredients found."
                        isLoading={isLoadingAutocomplete}
                      />
                    </div>
                    <Input
                      type="number"
                      value={ingredient.quantity || ''}
                      onChange={(e) => {
                        setIngredients(ingredients.map(ing =>
                          ing.id === ingredient.id ? { ...ing, quantity: e.target.value || null } : ing
                        ));
                      }}
                      placeholder="Qty"
                      className="w-24"
                    />
                    <span className="text-sm font-medium text-gray-700 w-6">g</span>
                    <Button
                      size="sm"
                      variant="ghost"
                      onClick={() => removeIngredientRow(ingredient.id)}
                      className="text-destructive hover:text-destructive hover:bg-destructive/10"
                    >
                      ✕
                    </Button>
                  </div>
                  {ingredient.ingredientId && (
                    <p className="text-xs text-muted-foreground">ID: {ingredient.ingredientId}</p>
                  )}
                </div>
              ))}
              <Button
                variant="outline"
                onClick={addIngredientRow}
                className="border-black text-lg text-green-900 font-bold px-3 py-1 h-auto"
              >
                + Add Row
              </Button>
            </div>
          </Section>
        </div>
      </div>
    </div>
  );
}
