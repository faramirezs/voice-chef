import { useMemo, useState } from 'react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
} from '@/components/ui/dialog';
import { Label } from '@/components/ui/label';
import { useAllRecipes } from '@/hooks/useRecipes';

const WEEKDAY_LABELS = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'];

function getWeekStart(baseDate: Date) {
  const weekStart = new Date(baseDate);
  const dayIndex = (weekStart.getDay() + 6) % 7; // Monday = 0
  weekStart.setDate(weekStart.getDate() - dayIndex);
  weekStart.setHours(0, 0, 0, 0);
  return weekStart;
}

function getWeekDays(baseDate: Date) {
  const weekStart = getWeekStart(baseDate);

  return Array.from({ length: 7 }, (_, i) => {
    const date = new Date(weekStart);
    date.setDate(weekStart.getDate() + i);
    return date;
  });
}

function formatDateKey(date: Date) {
  const year = date.getFullYear();
  const month = String(date.getMonth() + 1).padStart(2, '0');
  const day = String(date.getDate()).padStart(2, '0');
  return `${year}-${month}-${day}`;
}

function formatReadableDate(date: Date) {
  return date.toLocaleDateString(undefined, {
    weekday: 'short',
    month: 'short',
    day: 'numeric',
    year: 'numeric',
  });
}

type PlannedRecipe = {
  id: string;
  name: string;
  status: string;
  quantityWeight: number;
};

export function MenuPlannerPage() {
  const [visibleWeekDate, setVisibleWeekDate] = useState(() => new Date());

  const today = new Date();
  const weekDays = useMemo(() => getWeekDays(visibleWeekDate), [visibleWeekDate]);
  const [selectedDateKey, setSelectedDateKey] = useState<string | null>(null);
  const [isRecipeModalOpen, setIsRecipeModalOpen] = useState(false);
  const [recipeSearch, setRecipeSearch] = useState('');
  const [selectedRecipeId, setSelectedRecipeId] = useState<string>('');
  const [quantityWeight, setQuantityWeight] = useState<string>('');
  const [plannedRecipesByDate, setPlannedRecipesByDate] = useState<Record<string, PlannedRecipe[]>>({});

  const {
    data: allRecipes = [],
    isLoading: isLoadingRecipes,
    isError: isRecipeListError,
  } = useAllRecipes();

  const weekLabel = useMemo(() => {
    const start = weekDays[0];
    const end = weekDays[6];

    const sameMonth = start.getMonth() === end.getMonth() && start.getFullYear() === end.getFullYear();

    if (sameMonth) {
      return `${start.toLocaleDateString(undefined, { month: 'long' })} ${start.getDate()}-${end.getDate()}, ${start.getFullYear()}`;
    }

    return `${start.toLocaleDateString(undefined, { month: 'short', day: 'numeric' })} - ${end.toLocaleDateString(undefined, { month: 'short', day: 'numeric', year: 'numeric' })}`;
  }, [weekDays]);

  const selectedDate = useMemo(() => {
    if (!selectedDateKey) {
      return null;
    }

    const [year, month, day] = selectedDateKey.split('-').map(Number);
    return new Date(year, month - 1, day);
  }, [selectedDateKey]);

  const filteredRecipes = useMemo(() => {
    const normalizedSearch = recipeSearch.trim().toLowerCase();

    if (!normalizedSearch) {
      return allRecipes;
    }

    return allRecipes.filter((recipe) =>
      recipe.name.toLowerCase().includes(normalizedSearch),
    );
  }, [allRecipes, recipeSearch]);

  const goToPreviousWeek = () => {
    setVisibleWeekDate((current) => {
      const next = new Date(current);
      next.setDate(next.getDate() - 7);
      return next;
    });
  };

  const goToNextWeek = () => {
    setVisibleWeekDate((current) => {
      const next = new Date(current);
      next.setDate(next.getDate() + 7);
      return next;
    });
  };

  const handleAddRecipeClick = (date: Date) => {
    setSelectedDateKey(formatDateKey(date));
    setRecipeSearch('');
    setSelectedRecipeId('');
    setQuantityWeight('');
    setIsRecipeModalOpen(true);
  };

  const handleDiscard = () => {
    setSelectedRecipeId('');
    setQuantityWeight('');
    setRecipeSearch('');
    setIsRecipeModalOpen(false);
  };

  const handleAdd = () => {
    if (!selectedDateKey || !selectedRecipeId) {
      return;
    }

    const parsedQuantity = Number(quantityWeight);

    if (!Number.isFinite(parsedQuantity) || parsedQuantity <= 0) {
      return;
    }

    const selectedRecipe = allRecipes.find((recipe) => recipe.id === selectedRecipeId);

    if (!selectedRecipe) {
      return;
    }

    setPlannedRecipesByDate((current) => ({
      ...current,
      [selectedDateKey]: [
        ...(current[selectedDateKey] ?? []),
        {
          id: selectedRecipe.id,
          name: selectedRecipe.name,
          status: selectedRecipe.status,
          quantityWeight: parsedQuantity,
        },
      ],
    }));
    handleDiscard();
  };

  return (
    <div className="space-y-6">
      <div className="space-y-1">
        <h1 className="text-2xl font-semibold">Menu planner</h1>
        <p className="text-muted-foreground">Plan your meals and production schedule.</p>
      </div>

      <div className="rounded-xl border bg-card p-4 md:p-6">
        <div className="mb-4 flex items-center justify-between gap-2">
          <Button variant="outline" onClick={goToPreviousWeek}>
            Prev
          </Button>
          <h2 className="text-lg font-semibold">{weekLabel}</h2>
          <Button variant="outline" onClick={goToNextWeek}>
            Next
          </Button>
        </div>

        <div className="grid h-[calc(100vh-18rem)] min-h-[28rem] grid-cols-7 grid-rows-[auto_1fr] gap-x-2 gap-y-1 text-center text-sm">
          {WEEKDAY_LABELS.map((label) => (
            <div key={label} className="py-1 font-medium text-muted-foreground">
              {label}
            </div>
          ))}

          {weekDays.map((date) => {
            const isToday =
              date.getDate() === today.getDate() &&
              date.getMonth() === today.getMonth() &&
              date.getFullYear() === today.getFullYear();
            const dateKey = formatDateKey(date);
            const plannedRecipes = plannedRecipesByDate[dateKey] ?? [];

            return (
              <div
                key={date.toISOString()}
                className={`flex h-full flex-col rounded-md border bg-background p-2 text-left text-sm ${isToday ? 'ring-2 ring-primary' : ''}`}
              >
                <div className="flex items-start justify-between gap-2">
                  <Button
                    type="button"
                    size="icon-sm"
                    variant="outline"
                    onClick={() => handleAddRecipeClick(date)}
                    aria-label={`Add recipe for ${formatReadableDate(date)}`}
                  >
                    +
                  </Button>
                  <div className="text-right">
                    <span className="block text-xs text-muted-foreground">{date.toLocaleDateString(undefined, { month: 'short' })}</span>
                    <span className="font-medium">{date.getDate()}</span>
                  </div>
                </div>
                {plannedRecipes.length > 0 && (
                  <div className="mt-1 w-full space-y-1 overflow-y-auto">
                    {plannedRecipes.map((plannedRecipe, index) => (
                      <div key={`${plannedRecipe.id}-${index}`} className="rounded bg-primary/10 px-2 py-1 text-xs">
                        <p className="line-clamp-2 font-medium text-foreground">{plannedRecipe.name}</p>
                        <p className="text-muted-foreground">{plannedRecipe.quantityWeight} g</p>
                      </div>
                    ))}
                  </div>
                )}
              </div>
            );
          })}
        </div>
      </div>

      <Dialog
        open={isRecipeModalOpen}
        onOpenChange={(open) => {
          if (!open) {
            handleDiscard();
            return;
          }

          setIsRecipeModalOpen(true);
        }}
      >
        <DialogContent className="max-w-2xl">
          <DialogHeader>
            <DialogTitle>Select recipe</DialogTitle>
            <DialogDescription>
              {selectedDate ? `Assign a recipe to ${formatReadableDate(selectedDate)}.` : 'Assign a recipe to this date.'}
            </DialogDescription>
          </DialogHeader>

          <div className="space-y-2">
            <Label htmlFor="recipe-search">Recipe</Label>
            <Input
              id="recipe-search"
              placeholder="Search recipes by name..."
              value={recipeSearch}
              onChange={(event) => setRecipeSearch(event.target.value)}
            />
          </div>

          <div className="max-h-56 space-y-2 overflow-y-auto pr-1">
            {isLoadingRecipes && (
              <p className="text-sm text-muted-foreground">Loading recipes...</p>
            )}

            {isRecipeListError && (
              <p className="text-sm text-destructive">Failed to load recipes.</p>
            )}

            {!isLoadingRecipes && !isRecipeListError && filteredRecipes.length === 0 && (
              <p className="text-sm text-muted-foreground">No recipes found.</p>
            )}

            {filteredRecipes.map((recipe) => (
              <button
                key={recipe.id}
                type="button"
                onClick={() => setSelectedRecipeId(recipe.id)}
                className={`flex w-full items-center justify-between rounded-lg border px-3 py-2 text-left hover:bg-muted/40 ${selectedRecipeId === recipe.id ? 'border-primary bg-primary/10' : ''}`}
              >
                <span className="font-medium">{recipe.name}</span>
                <span className="text-xs capitalize text-muted-foreground">{recipe.status}</span>
              </button>
            ))}
          </div>

          <div className="space-y-2">
            <Label htmlFor="quantity-weight">Quantity (weight)</Label>
            <Input
              id="quantity-weight"
              type="number"
              min="0"
              step="0.01"
              placeholder="e.g. 250"
              value={quantityWeight}
              onChange={(event) => setQuantityWeight(event.target.value)}
            />
          </div>

          <div className="flex justify-end gap-2">
            <Button type="button" variant="outline" onClick={handleDiscard}>
              Discard
            </Button>
            <Button
              type="button"
              onClick={handleAdd}
              disabled={!selectedRecipeId || !quantityWeight || Number(quantityWeight) <= 0}
            >
              Add
            </Button>
          </div>
        </DialogContent>
      </Dialog>
    </div>
  );
}
