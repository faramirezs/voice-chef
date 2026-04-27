import { cn } from "@/lib/utils";

interface YieldField {
  label: string;
  value: number | null;
  isTarget: boolean;
}

interface RecipeYieldBarProps {
  fields: YieldField[];
  mode: "detail" | "scaling";
  onChange?: (index: number, raw: string) => void;
}

function formatValue(value: number | null): string {
  if (value == null) return "\u2014";
  // Strip unnecessary trailing zeros
  const str = value.toFixed(2);
  return str.replace(/\.?0+$/, "");
}

export function RecipeYieldBar({
  fields,
  mode,
  onChange,
}: RecipeYieldBarProps) {
  return (
    <div className="grid grid-cols-3 gap-3">
      {fields.map((field, i) =>
        mode === "detail" ? (
          <YieldChip key={field.label} field={field} />
        ) : (
          <YieldInput
            key={field.label}
            field={field}
            onChange={(raw) => onChange?.(i, raw)}
          />
        )
      )}
    </div>
  );
}

function YieldChip({ field }: { field: YieldField }) {
  return (
    <div
      className={cn(
        "rounded-2xl bg-surface/60 border px-4 py-3",
        field.isTarget
          ? "border-l-2 border-l-primary border-border/40"
          : "border-border/40"
      )}
    >
      <div className="flex items-center gap-1 mb-1">
        <span className="text-xs text-text-muted uppercase tracking-wide">
          {field.label}
        </span>
        {field.isTarget && (
          <span className="text-[10px] text-primary bg-primary/15 px-1.5 py-0.5 rounded">
            drive
          </span>
        )}
      </div>
      <div className="text-base font-mono font-medium text-text">
        {formatValue(field.value)}
      </div>
    </div>
  );
}

function YieldInput({
  field,
  onChange,
}: {
  field: YieldField;
  onChange: (raw: string) => void;
}) {
  return (
    <div className="space-y-1">
      <label className="text-xs text-text-muted flex items-center gap-1">
        {field.label}
        {field.isTarget && (
          <span className="text-[10px] text-primary bg-primary/15 px-1 rounded">
            drive
          </span>
        )}
      </label>
      <input
        type="number"
        step="any"
        value={field.value ?? ""}
        onChange={(e) => onChange(e.target.value)}
        className="w-full h-12 px-3 text-sm rounded-xl bg-surface/90 border border-border text-text font-mono
          focus:outline-none focus:ring-2 focus:ring-primary/50 focus:border-primary/60"
      />
    </div>
  );
}
