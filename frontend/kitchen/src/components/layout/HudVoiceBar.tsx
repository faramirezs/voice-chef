import { useState, useCallback, useEffect } from "react";
import { VoiceInput } from "@/components/chat/VoiceInput";
import { getSendMessage } from "@/hooks/useAgent";

export function HudVoiceBar() {
  const [heardChip, setHeardChip] = useState<string | null>(null);

  const handleTranscript = useCallback((text: string) => {
    getSendMessage()(text);
    setHeardChip(text);
  }, []);

  // Auto-dismiss the "heard" chip after 3 seconds.
  useEffect(() => {
    if (!heardChip) return;
    const timer = setTimeout(() => setHeardChip(null), 3000);
    return () => clearTimeout(timer);
  }, [heardChip]);

  return (
    <div className="flex items-center justify-center pb-6 gap-4">
      <VoiceInput onTranscript={handleTranscript} />
      {heardChip && (
        <span className="text-sm text-text-muted bg-surface-alt/80 px-3 py-1.5 rounded-full border border-border/50 max-w-xs truncate">
          {heardChip}
        </span>
      )}
    </div>
  );
}
