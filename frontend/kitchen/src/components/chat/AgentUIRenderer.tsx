import { KCard } from "@/components/ui/KCard";

interface AgentUIRendererProps {
  content: unknown;
  agentState?: unknown;
  onApplyScaling?: (state: RecipeScalingState) => void;
  onAutoImprove?: (recipeId: string) => void;
}
interface RecipeData {
  id?: string;
  name?: string;
  status?: string;
  description?: string;
  instructions?: string;
  serving_recommendation?: string;
  yield_mode?: string;
  total_raw_weight_grams?: number | string | null;
  total_cooked_weight_grams?: number | string | null;
  portion_size_grams?: number | string | null;
  portions_count_resolved?: number | string | null;
  yield_amount?: number;
  yield_unit?: string;
  use_by_date?: string;
  created_at?: string;
  updated_at?: string;
}

interface PaginationMeta {
  limit: number;
  offset: number;
  total: number;
}

interface RecipesListEnvelope {
  type: "recipes.list";
  version: "1";
  items: RecipeData[];
  meta: PaginationMeta;
  query?: string;
}

interface RecipeDetailEnvelope {
  type: "recipe.detail";
  version: "1";
  item: RecipeData;
}

interface ErrorEnvelope {
  type: "error";
  version: "1";
  source?: string;
  message: string;
}

type TypedEnvelope = RecipesListEnvelope | RecipeDetailEnvelope | ErrorEnvelope;

function tryParseJson(raw: string): unknown {
  try {
    return JSON.parse(raw);
  } catch {
    return null;
  }
}

function extractFencedJson(raw: string): string | null {
  const match = raw.match(/```(?:json)?\s*([\s\S]*?)\s*```/i);
  return match ? match[1] : null;
}

function normalizePayload(content: unknown): unknown {
  if (typeof content === "string") {
    const parsed = tryParseJson(content);
    if (parsed !== null) {
      return parsed;
    }

    const fencedJson = extractFencedJson(content);
    if (fencedJson) {
      const parsedFenced = tryParseJson(fencedJson);
      if (parsedFenced !== null) {
        return parsedFenced;
      }
    }
  }

  if (Array.isArray(content) || isObject(content)) {
    return content;
  }

  return null;
}

function toDisplayText(content: unknown): string {
  if (typeof content === "string") {
    return content;
  }
  if (content == null) {
    return "";
  }
  try {
    return JSON.stringify(content, null, 2);
  } catch {
    return String(content);
  }
}

function isObject(value: unknown): value is Record<string, unknown> {
  return typeof value === "object" && value !== null;
}

function isRecipeData(value: unknown): value is RecipeData {
  return isObject(value);
}

function isPaginationMeta(value: unknown): value is PaginationMeta {
  return (
    isObject(value) &&
    typeof value.limit === "number" &&
    typeof value.offset === "number" &&
    typeof value.total === "number"
  );
}

function parseTypedEnvelope(raw: unknown): TypedEnvelope | null {
  if (!isObject(raw) || typeof raw.type !== "string" || raw.version !== "1") {
    return null;
  }

  if (raw.type === "recipes.list") {
    const items = raw.items;
    const meta = raw.meta;
    if (!Array.isArray(items) || !items.every(isRecipeData) || !isPaginationMeta(meta)) {
      return null;
    }
    return {
      type: "recipes.list",
      version: "1",
      items,
      meta,
      query: typeof raw.query === "string" ? raw.query : undefined,
    };
  }

  if (raw.type === "recipe.detail") {
    if (!isRecipeData(raw.item)) {
      return null;
    }
    return {
      type: "recipe.detail",
      version: "1",
      item: raw.item,
    };
  }

  if (raw.type === "error") {
    if (typeof raw.message !== "string") {
      return null;
    }
    return {
      type: "error",
      version: "1",
      source: typeof raw.source === "string" ? raw.source : undefined,
      message: raw.message,
    };
  }

  return null;
}

function parseLegacyRecipes(raw: unknown): RecipeData[] | null {
  if (Array.isArray(raw) && raw.every(isRecipeData)) {
    return raw;
  }
  if (isRecipeData(raw)) {
    return [raw];
  }
  return null;
}

function StatusBadge({ status }: { status: string }) {
  const color =
    status === "published"
      ? "bg-success/20 text-success"
      : "bg-warning/20 text-warning";
  return (
    <span className={`text-sm px-2 py-0.5 rounded-full ${color}`}>
      {status}
    </span>
  );
}

function RecipeCard({ recipe }: { recipe: RecipeData }) {
  return (
    <KCard className="p-4 space-y-2">
      <div className="flex items-center gap-2 flex-wrap">
        <h3 className="text-lg font-semibold">{recipe.name ?? "Recipe"}</h3>
        {recipe.status && <StatusBadge status={recipe.status} />}
      </div>

      {recipe.description && (
        <p className="text-text-muted text-base">{recipe.description}</p>
      )}

      {recipe.instructions && (
        <div className="text-base whitespace-pre-wrap leading-relaxed">
          {recipe.instructions.length > 300
            ? recipe.instructions.slice(0, 300) + "..."
            : recipe.instructions}
        </div>
      )}

      <div className="flex flex-wrap gap-3 text-sm text-text-muted pt-1">
        {recipe.yield_amount != null && recipe.yield_unit && (
          <span>
            Yield: {recipe.yield_amount} {recipe.yield_unit}
          </span>
        )}
        {recipe.serving_recommendation && (
          <span>Serving: {recipe.serving_recommendation}</span>
        )}
        {recipe.use_by_date && <span>Use by: {recipe.use_by_date}</span>}
      </div>
    </KCard>
  );
}

function asDisplayValue(value: unknown, fallback = "not specified"): string {
  if (value === null || value === undefined || value === "") {
    return fallback;
  }
  return String(value);
}

function DetailRow({ label, value }: { label: string; value: unknown }) {
  return (
    <div className="grid grid-cols-[150px_1fr] gap-2 text-sm">
      <span className="text-text-muted">{label}</span>
      <span className="text-text">{asDisplayValue(value)}</span>
    </div>
  );
}

function RecipeDetailCard({ recipe }: { recipe: RecipeData }) {
  return (
    <KCard className="p-4 space-y-3">
      <div className="flex items-center gap-2 flex-wrap">
        <h3 className="text-lg font-semibold">{recipe.name ?? "Recipe detail"}</h3>
        {recipe.status && <StatusBadge status={recipe.status} />}
      </div>

      <div className="space-y-2">
        <DetailRow label="ID" value={recipe.id} />
        <DetailRow label="Yield mode" value={recipe.yield_mode} />
        <DetailRow label="Portions" value={recipe.portions_count_resolved} />
        <DetailRow label="Portion size (g)" value={recipe.portion_size_grams} />
        <DetailRow label="Total raw weight (g)" value={recipe.total_raw_weight_grams} />
        <DetailRow label="Total cooked weight (g)" value={recipe.total_cooked_weight_grams} />
        <DetailRow label="Description" value={recipe.description} />
        <DetailRow label="Instructions" value={recipe.instructions} />
        <DetailRow label="Created" value={recipe.created_at} />
        <DetailRow label="Updated" value={recipe.updated_at} />
      </div>
    </KCard>
  );
}

function ErrorCard({ message }: { message: string }) {
  return (
    <div className="bg-error/10 border border-error/30 rounded-2xl p-4 text-error">
      <p className="font-semibold">Tool error</p>
      <p className="text-sm mt-1">{message}</p>
    </div>
  );
}

function RecipesListCard({ payload }: { payload: RecipesListEnvelope }) {
  return (
    <div className="space-y-3">
      <div className="text-xs text-text-muted px-1">
        Showing {payload.items.length} of {payload.meta.total}
        {payload.query ? ` for \"${payload.query}\"` : ""}
      </div>
      {payload.items.map((recipe, i) => (
        <RecipeCard key={recipe.name ?? i} recipe={recipe} />
      ))}
    </div>
  );
}

export function AgentUIRenderer({ content }: AgentUIRendererProps) {
  const parsed = normalizePayload(content);
  const typed = parseTypedEnvelope(parsed);
  const textContent = toDisplayText(content);

  if (typed) {
    switch (typed.type) {
      case "recipes.list":
        return <RecipesListCard payload={typed} />;
      case "recipe.detail":
        return <RecipeDetailCard recipe={typed.item} />;
      case "error":
        return <ErrorCard message={typed.message} />;
      default:
        return null;
    }
  }

  // Temporary compatibility fallback while old tool payloads may still appear.
  const legacyRecipes = parseLegacyRecipes(parsed);
  if (legacyRecipes) {
    return (
      <div className="space-y-3">
        {legacyRecipes.map((recipe, i) => (
          <RecipeCard key={recipe.name ?? i} recipe={recipe} />
        ))}
      </div>
    );
  }

  if (
    textContent.toLowerCase().includes("error") ||
    textContent.toLowerCase().includes("not found")
  ) {
    return <ErrorCard message={textContent} />;
  }

  return (
    <KCard className="p-4 text-base whitespace-pre-wrap">
      {textContent}
    </KCard>
  );
}
