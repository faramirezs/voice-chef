import { KCard } from "@/components/ui/KCard";

interface AgentUIRendererProps {
  content: string;
}

interface RecipeData {
  name?: string;
  status?: string;
  description?: string;
  instructions?: string;
  serving_recommendation?: string;
  yield_amount?: number;
  yield_unit?: string;
  use_by_date?: string;
}

function tryParseRecipe(raw: string): RecipeData | RecipeData[] | null {
  try {
    return JSON.parse(raw);
  } catch {
    return null;
  }
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

function ErrorCard({ message }: { message: string }) {
  return (
    <div className="bg-error/10 border border-error/30 rounded-2xl p-4 text-error">
      <p className="font-semibold">Tool error</p>
      <p className="text-sm mt-1">{message}</p>
    </div>
  );
}

export function AgentUIRenderer({ content }: AgentUIRendererProps) {
  const parsed = tryParseRecipe(content);

  if (!parsed) {
    if (
      content.toLowerCase().includes("error") ||
      content.toLowerCase().includes("not found")
    ) {
      return <ErrorCard message={content} />;
    }
    return (
      <KCard className="p-4 text-base whitespace-pre-wrap">
        {content}
      </KCard>
    );
  }

  const recipes = Array.isArray(parsed) ? parsed : [parsed];

  return (
    <div className="space-y-3">
      {recipes.map((recipe, i) => (
        <RecipeCard key={recipe.name ?? i} recipe={recipe} />
      ))}
    </div>
  );
}
