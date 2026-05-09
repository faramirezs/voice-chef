import { useState } from 'react';
import { useIngredients } from '@/hooks/useIngredients';
import { Input } from '@/components/ui/input';
import { Button } from '@/components/ui/button';
import { Card, CardHeader, CardTitle } from '@/components/ui/card';
// import { cn } from '@/lib/utils';

const PAGE_SIZE = 100;

function IngredientSkeleton() {
  return (
    <div className="rounded-lg border bg-card p-4 space-y-3 animate-pulse">
      <div className="flex justify-between gap-2">
        <div className="h-4 bg-muted rounded w-3/4" />
        <div className="h-4 bg-muted rounded w-16" />
      </div>
      <div className="h-3 bg-muted rounded w-1/2" />
    </div>
  );
}

export function IngredientsList() {
  // const [sourceFilter, setSourceFilter] = useState('');
  const [nameFilter, setNameFilter] = useState('');
  const [page, setPage] = useState(0);
  const [viewMode, setViewMode] = useState<'grid' | 'list'>('grid');

  const offset = page * PAGE_SIZE;
  const normalizedNameFilter = nameFilter.trim();
  // const normalizedSourceFilter = sourceFilter.trim();

  const { data: ingredientPage, isLoading, isError, error } = useIngredients({
    ...(normalizedNameFilter ? { search: normalizedNameFilter } : {}),
    // ...(normalizedSourceFilter ? { source: normalizedSourceFilter } : {}),
    offset,
    limit: PAGE_SIZE,
  });

  const visibleIngredients = ingredientPage?.items ?? [];
  const isInitialLoading = isLoading && !ingredientPage;

  return (
    <div className="space-y-4">
      <div className="flex items-center gap-3">
        <Input
          placeholder="Filter by name..."
          className="max-w-sm"
          value={nameFilter}
          onChange={(e) => {
            setNameFilter(e.target.value);
            setPage(0);
          }}
        />
        {/* <Input
          placeholder="Filter by source (e.g. standard, custom)..."
          className="max-w-sm"
          value={sourceFilter}
          onChange={(e) => {
            setSourceFilter(e.target.value);
            setPage(0);
          }}
        /> */}

        {!isInitialLoading && ingredientPage && (
          <span className="text-sm text-muted-foreground">
            {ingredientPage.meta.total} ingredient{ingredientPage.meta.total !== 1 ? 's' : ''}
          </span>
        )}

        <div className="ml-auto flex gap-2">
          <Button
            variant="outline"
            type="button"
            onClick={() => setViewMode((mode) => (mode === 'grid' ? 'list' : 'grid'))}
          >
            {viewMode === 'grid' ? 'List view' : 'Grid view'}
          </Button>
          {/* <Button variant="outline" type="button">
            Import
          </Button>
          <Button variant="outline" type="button">
            Export
          </Button> */}
        </div>
      </div>

      {isError && (
        <div className="rounded-lg border border-destructive/50 bg-destructive/10 p-4 text-sm text-destructive">
          Failed to load ingredients: {error instanceof Error ? error.message : 'Unknown error'}
        </div>
      )}

      {isInitialLoading && (
        <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-3">
          {Array.from({ length: 6 }).map((_, i) => (
            <IngredientSkeleton key={i} />
          ))}
        </div>
      )}

      {!isInitialLoading && !isError && visibleIngredients.length === 0 && (
        <div className="rounded-lg border border-dashed p-8 text-center text-muted-foreground">
          No ingredients found.
        </div>
      )}

      {!isInitialLoading && visibleIngredients.length > 0 && (
        <>
          {viewMode === 'grid' ? (
            <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-6">
              {visibleIngredients.map((ingredient) => (
                <Card key={ingredient.id} className="h-[10rem] gap-2">
                  <CardHeader className="pb-2 h-full">
                    <div className="flex h-full items-start justify-between gap-2">
                      <CardTitle className="flex-1 text-base leading-snug break-words">
                        {ingredient.name}
                      </CardTitle>
                      {/* <span
                        className={cn(
                          'inline-flex items-center rounded-full px-2 py-0.5 text-xs font-medium capitalize',
                          ingredient.is_custom ? 'bg-orange-100 text-orange-800' : 'bg-blue-100 text-blue-800',
                        )}
                      >
                        {ingredient.is_custom ? 'custom' : ingredient.source ?? 'standard'}
                      </span> */}
                    </div>
                    {/* {ingredient.default_unit && (
                      <p className="text-sm text-muted-foreground">Default unit: {ingredient.default_unit}</p>
                    )} */}
                  </CardHeader>
                </Card>
              ))}
            </div>
          ) : (
            <div className="space-y-2">
              {visibleIngredients.map((ingredient) => (
                <div
                  key={ingredient.id}
                  className="flex w-full items-center justify-between rounded-lg border bg-card px-4 py-3"
                >
                  <span className="font-medium">{ingredient.name}</span>
                  {/* <span
                    className={cn(
                      'inline-flex items-center rounded-full px-2 py-0.5 text-xs font-medium capitalize',
                      ingredient.is_custom ? 'bg-orange-100 text-orange-800' : 'bg-blue-100 text-blue-800',
                    )}
                  >
                    {ingredient.is_custom ? 'custom' : ingredient.source ?? 'standard'}
                  </span> */}
                </div>
              ))}
            </div>
          )}

          <div className="flex items-center justify-between gap-3">
            <p className="text-sm text-muted-foreground">
              Showing {offset + 1}-{offset + visibleIngredients.length} of {ingredientPage?.meta.total ?? 0}
            </p>
            <div className="flex gap-2">
              <Button
                variant="outline"
                onClick={() => setPage((currentPage) => Math.max(0, currentPage - 1))}
                disabled={page === 0}
              >
                Previous
              </Button>
              <Button
                onClick={() => setPage((currentPage) => currentPage + 1)}
                disabled={offset + PAGE_SIZE >= (ingredientPage?.meta.total ?? 0)}
              >
                Next
              </Button>
            </div>
          </div>
        </>
      )}
    </div>
  );
}