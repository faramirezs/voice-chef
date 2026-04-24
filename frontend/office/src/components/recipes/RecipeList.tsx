import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useRecipes } from '@/hooks/useRecipes';
import { RecipeCard } from './RecipeCard';
import { Input } from '@/components/ui/input';
import { Button } from '@/components/ui/button';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select';
import { cn } from '@/lib/utils';

const PAGE_SIZE = 12;

const SORT_OPTIONS = [
  { value: 'name_asc', label: 'Name (A-Z)' },
  { value: 'name_desc', label: 'Name (Z-A)' },
  { value: 'updated_at_asc', label: 'Modification date (first-last)' },
  { value: 'updated_at_desc', label: 'Modification date (last-first)' },
  { value: 'created_at_asc', label: 'Creation date (first-last)' },
  { value: 'created_at_desc', label: 'Creation date (last-first)' },
] as const;

type SortOption = (typeof SORT_OPTIONS)[number]['value'];

function RecipeSkeleton() {
  return (
    <div className="rounded-lg border bg-card p-4 space-y-3 animate-pulse">
      <div className="flex justify-between gap-2">
        <div className="h-4 bg-muted rounded w-3/4" />
        <div className="h-4 bg-muted rounded w-12" />
      </div>
      <div className="h-3 bg-muted rounded w-1/2" />
    </div>
  );
}

export function RecipeList() {
  const navigate = useNavigate();
  const [statusFilter, setStatusFilter] = useState('');
  const [nameFilter, setNameFilter] = useState('');
  const [sortBy, setSortBy] = useState<SortOption>('updated_at_desc');
  const [page, setPage] = useState(0);
  const [viewMode, setViewMode] = useState<'grid' | 'list'>('grid');

  const statusOptions: Array<{ label: string; value: 'draft' | 'active' | '' }> = [
    { label: 'All', value: '' },
    { label: 'Draft', value: 'draft' },
    { label: 'Active', value: 'active' },
  ];

  const offset = page * PAGE_SIZE;
  const normalizedNameFilter = nameFilter.trim();

  const { data: recipePage, isLoading, isError, error } = useRecipes({
    ...(statusFilter ? { status: statusFilter } : {}),
    ...(normalizedNameFilter ? { name: normalizedNameFilter } : {}),
    sort_by: sortBy,
    offset,
    limit: PAGE_SIZE,
  });
  const visibleRecipes = recipePage?.items ?? [];
  const isInitialLoading = isLoading && !recipePage;

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
         <div className="inline-flex items-center rounded-md bg-background p-1">
          {statusOptions.map((option) => (
            <Button
              key={option.value || 'all'}
              type="button"
              variant={statusFilter === option.value ? 'default' : 'ghost'}
              className="h-8 px-3"
              onClick={() => {
                setStatusFilter(option.value);
                setPage(0);
              }}
            >
              {option.label}
            </Button>
          ))}
        </div>
        <Input
          placeholder="Filter by status (e.g. draft, active)…"
          className="max-w-sm"
          value={statusFilter}
          onChange={(e) => {
            setStatusFilter(e.target.value);
            setPage(0);
          }}
        />
        <Select
          value={sortBy}
          onValueChange={(value) => {
            setSortBy(value as SortOption);
            setPage(0);
          }}
        >
          <SelectTrigger aria-label="Sort recipes" className="w-[280px]">
            <SelectValue placeholder="Sort recipes" />
          </SelectTrigger>
          <SelectContent>
            {SORT_OPTIONS.map((option) => (
              <SelectItem key={option.value} value={option.value}>
                {option.label}
              </SelectItem>
            ))}
          </SelectContent>
        </Select>
        {!isInitialLoading && recipePage && (
          <span className="text-sm text-muted-foreground">
            {recipePage.meta.total} recipe{recipePage.meta.total !== 1 ? 's' : ''}
          </span>
        )}
        <div className="flex gap-2 ml-auto">
          <Button
            variant="outline"
            type="button"
            onClick={() => setViewMode((mode) => (mode === 'grid' ? 'list' : 'grid'))}
          >
            {viewMode === 'grid' ? 'List view' : 'Grid view'}
          </Button>
          <Button variant="outline" type="button">
            Import
          </Button>
          <Button variant="outline" type="button">
            Export
          </Button>
        </div>
      </div>

      {isError && (
        <div className="rounded-lg border border-destructive/50 bg-destructive/10 p-4 text-sm text-destructive">
          Failed to load recipes:{' '}
          {error instanceof Error ? error.message : 'Unknown error'}
        </div>
      )}

      {isInitialLoading && (
        <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-3">
          {Array.from({ length: 6 }).map((_, i) => (
            <RecipeSkeleton key={i} />
          ))}
        </div>
      )}

      {!isInitialLoading && !isError && visibleRecipes.length === 0 && (
        <div className="rounded-lg border border-dashed p-8 text-center text-muted-foreground">
          No recipes found.
        </div>
      )}

      {!isInitialLoading && visibleRecipes.length > 0 && (
        <>
          {viewMode === 'grid' ? (
            <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-6">
              {visibleRecipes.map((recipe) => (
                <RecipeCard key={recipe.id} recipe={recipe} />
              ))}
            </div>
          ) : (
            <div className="space-y-2">
              {visibleRecipes.map((recipe) => (
                <button
                  key={recipe.id}
                  type="button"
                  className="flex w-full items-center justify-between rounded-lg border bg-card px-4 py-3 text-left transition-colors hover:bg-muted/40"
                  onClick={() => navigate(`/recipes/${recipe.id}`)}
                >
                  <span className="font-medium">{recipe.name}</span>
                  <span
                    className={cn(
                      'inline-flex items-center rounded-full px-2 py-0.5 text-xs font-medium capitalize',
                      recipe.status === 'draft'
                        ? 'bg-yellow-100 text-yellow-800'
                        : recipe.status === 'active'
                        ? 'bg-green-100 text-green-800'
                        : 'bg-gray-100 text-gray-600',
                    )}
                  >
                    {recipe.status}
                  </span>
                </button>
              ))}
            </div>
          )}

          <div className="flex items-center justify-between gap-3">
            <p className="text-sm text-muted-foreground">
              Showing {offset + 1}-{offset + visibleRecipes.length} of {recipePage?.meta.total ?? 0}
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
                disabled={offset + PAGE_SIZE >= (recipePage?.meta.total ?? 0)}
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
