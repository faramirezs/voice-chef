import { useCallback, useEffect, useState } from "react";
import { KInput } from "@/components/ui/KInput";
import { KSelect } from "@/components/ui/KSelect";
import { KButton } from "@/components/ui/KButton";
import { useAgentSlots } from "@/components/layout/AgentSlotProvider";
import { chefAgent } from "@/lib/agent";
import { type KitchenState } from "@/types/agent-state";
import { cn } from "@/lib/utils";

interface RecipeSummaryItem {
  id: string;
  name: string;
  status: string;
  yield_mode: string;
  portions_count_resolved: string | null;
}

interface PaginatedMeta {
  total: number;
  limit: number;
  offset: number;
}

interface RecipeListViewProps {
  items?: RecipeSummaryItem[];
  meta?: PaginatedMeta;
}

const STATUS_STYLES: Record<string, string> = {
  draft: "bg-warning/15 text-warning border-warning/30",
  active: "bg-success/15 text-success border-success/30",
  archived: "bg-border/30 text-text-muted border-border/50",
};

const SORT_OPTIONS = [
  { value: "updated_at_desc", label: "Newest" },
  { value: "updated_at_asc", label: "Oldest" },
  { value: "name_asc", label: "Name A-Z" },
  { value: "name_desc", label: "Name Z-A" },
];

const STATUS_OPTIONS = [
  { value: "", label: "All" },
  { value: "draft", label: "Draft" },
  { value: "active", label: "Active" },
  { value: "archived", label: "Archived" },
];

export function RecipeListView(props: RecipeListViewProps) {
  const { dispatch } = useAgentSlots();
  const agentProvidedItems = props.items !== undefined;

  const [recipes, setRecipes] = useState<RecipeSummaryItem[]>(props.items ?? []);
  const [meta, setMeta] = useState<PaginatedMeta>(
    props.meta ?? { total: 0, limit: 18, offset: 0 }
  );
  const [query, setQuery] = useState("");
  const [status, setStatus] = useState("");
  const [sortBy, setSortBy] = useState("updated_at_desc");
  const [mode, setMode] = useState<"props" | "fetch">(
    agentProvidedItems ? "props" : "fetch"
  );
  const [loading, setLoading] = useState(!agentProvidedItems);

  // Sync agent state on mount.
  useEffect(() => {
    chefAgent.setState({
      view: "recipe_list",
      selected_recipe: null,
      scaling: null,
      last_action: { type: "browse", timestamp: Date.now() },
    });
  }, []);

  // Fetch recipes when in fetch mode or when filters change.
  useEffect(() => {
    if (mode === "props") {
      setLoading(false);
      return;
    }

    const controller = new AbortController();
    setLoading(true);

    const params = new URLSearchParams({
      limit: String(meta.limit),
      offset: String(meta.offset),
      sort_by: sortBy,
    });
    if (query) params.set("search", query);
    if (status) params.set("status", status);

    fetch(`/api/recipes?${params}`, { signal: controller.signal })
      .then((r) => r.json())
      .then((data) => {
        setRecipes(data.items ?? []);
        setMeta(
          data.meta ?? { total: 0, limit: meta.limit, offset: meta.offset }
        );
      })
      .catch((err) => {
        if (err.name !== "AbortError") {
          console.error("Failed to fetch recipes:", err);
        }
      })
      .finally(() => setLoading(false));

    return () => controller.abort();
  }, [query, status, sortBy, meta.offset, meta.limit, mode]);

  const openRecipe = useCallback(
    (recipe: RecipeSummaryItem) => {
      const ks: KitchenState = {
        view: "recipe_detail",
        selected_recipe: {
          id: recipe.id,
          name: recipe.name,
          portions: recipe.portions_count_resolved
            ? parseFloat(recipe.portions_count_resolved)
            : null,
          yield_mode: recipe.yield_mode,
        },
        scaling: null,
        last_action: { type: "select", timestamp: Date.now() },
      };
      chefAgent.setState(ks);

      fetch(`/api/recipes/${recipe.id}`)
        .then((r) => r.json())
        .then((data) =>
          dispatch("canvas", "recipe_detail", { recipe: data, from_list: true })
        );
    },
    [dispatch]
  );

  const totalPages = Math.max(1, Math.ceil(meta.total / meta.limit));
  const currentPage = Math.floor(meta.offset / meta.limit) + 1;

  const goToPage = (page: number) => {
    const clamped = Math.max(1, Math.min(page, totalPages));
    setMeta((prev) => ({ ...prev, offset: (clamped - 1) * prev.limit }));
  };

  const transitionToFetch = () => {
    setMode("fetch");
    setMeta((prev) => ({ ...prev, offset: 0 }));
  };

  return (
    <div className="w-full h-full flex flex-col px-4">
      {/* Header */}
      <div className="flex items-center justify-between gap-3 flex-shrink-0">
        <h2 className="text-2xl font-semibold text-text">Recipes</h2>
      </div>

      {/* Filter bar */}
      <div className="grid grid-cols-1 sm:grid-cols-3 gap-3 flex-shrink-0">
        <KInput
          placeholder="Search..."
          value={query}
          onChange={(e) => {
            setQuery(e.target.value);
            transitionToFetch();
          }}
        />
        <KSelect
          options={STATUS_OPTIONS}
          value={status}
          onChange={(e) => {
            setStatus(e.target.value);
            transitionToFetch();
          }}
        />
        <KSelect
          options={SORT_OPTIONS}
          value={sortBy}
          onChange={(e) => {
            setSortBy(e.target.value);
            transitionToFetch();
          }}
        />
      </div>

      {/* Grid */}
      <div className="mt-2 flex-1 min-h-0 overflow-hidden">
        {loading ? (
          <div className="py-8 text-center text-text-muted">Loading...</div>
        ) : recipes.length === 0 ? (
          <div className="py-8 text-center text-text-muted">No recipes found</div>
        ) : (
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-3 h-full content-start">
            {recipes.map((recipe) => (
              <button
                key={recipe.id}
                type="button"
                onClick={() => openRecipe(recipe)}
                className="text-left p-3 rounded-xl border border-border/70 bg-surface/80 hover:bg-surface-alt transition-colors space-y-1"
              >
                <div className="flex items-start justify-between gap-2">
                  <h3 className="text-base font-semibold text-text truncate">
                    {recipe.name}
                  </h3>
                </div>
                <div className="flex items-center gap-2 text-sm text-text-muted">
                  {recipe.portions_count_resolved && (
                    <span className="flex items-center gap-1">
                      <svg
                        width="14"
                        height="14"
                        viewBox="0 0 16 16"
                        fill="none"
                        stroke="currentColor"
                        strokeWidth="2"
                        strokeLinecap="round"
                        strokeLinejoin="round"
                      >
                        <circle cx="8" cy="8" r="6" />
                        <path d="M8 5v3l2 2" />
                      </svg>
                      {recipe.portions_count_resolved} portions
                    </span>
                  )}
                  <span
                    className={cn(
                      "text-xs px-2 py-0.5 rounded-full border",
                      STATUS_STYLES[recipe.status] ?? STATUS_STYLES.archived
                    )}
                  >
                    {recipe.status}
                  </span>
                </div>
              </button>
            ))}
          </div>
        )}
      </div>

      {/* Pagination */}
      {mode === "fetch" && totalPages > 1 && (
        <div className="flex items-center justify-center gap-2 pt-2 flex-shrink-0">
          <KButton
            type="button"
            variant="ghost"
            className="h-10 px-3 text-base"
            disabled={currentPage <= 1}
            onClick={() => goToPage(currentPage - 1)}
          >
            &#8249;
          </KButton>
          {Array.from({ length: totalPages }, (_, i) => i + 1).map((page) => (
            <KButton
              key={page}
              type="button"
              variant={page === currentPage ? "default" : "ghost"}
              className="h-10 w-10 text-base"
              onClick={() => goToPage(page)}
            >
              {page}
            </KButton>
          ))}
          <KButton
            type="button"
            variant="ghost"
            className="h-10 px-3 text-base"
            disabled={currentPage >= totalPages}
            onClick={() => goToPage(currentPage + 1)}
          >
            &#8250;
          </KButton>
        </div>
      )}
    </div>
  );
}
