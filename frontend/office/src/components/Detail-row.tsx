export function DetailRow({ label, value }: 
    { label: string; value: string | number | boolean | null | undefined }) {
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