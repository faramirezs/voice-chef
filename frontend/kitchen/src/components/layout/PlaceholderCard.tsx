import { KCard } from "@/components/ui/KCard";

interface PlaceholderCardProps {
  message?: string;
  slot?: string;
}

export function PlaceholderCard(props: Record<string, unknown>) {
  const { message = "Slot active", slot } = props as PlaceholderCardProps;

  return (
    <KCard className="p-4 space-y-2">
      <div className="flex items-center justify-between">
        <h3 className="text-sm font-medium text-primary">Placeholder</h3>
        {slot && (
          <span className="text-xs text-text-muted bg-surface/60 px-2 py-0.5 rounded-full">
            {slot}
          </span>
        )}
      </div>
      <p className="text-sm text-text-muted">{message}</p>
    </KCard>
  );
}
