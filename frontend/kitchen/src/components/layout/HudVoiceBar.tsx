import { useVoiceSubmit } from "@/hooks/useVoiceSubmit";
import { type SttResult } from "@/components/chat/VoiceInput";
import { useState, useCallback, useEffect } from "react";
import { VoiceInput } from "@/components/chat/VoiceInput";

export function HudVoiceBar() {
  const [heardChip, setHeardChip] = useState<string | null>(null);
  const [confidenceWarning, setConfidenceWarning] = useState("");
  const submitVoice = useVoiceSubmit();

  const handleTranscript = useCallback((text: string, sttResult?: SttResult) => {
    const result = submitVoice(text, sttResult);
    if (result.submitted) {
      setHeardChip(text);
      if (result.warning) {
        setConfidenceWarning(result.warning);
      }
    }
  }, [submitVoice]);

  // Auto-dismiss low-confidence warning after 4 seconds.
  useEffect(() => {
    if (!confidenceWarning) return;
    const timer = setTimeout(() => setConfidenceWarning(""), 4000);
    return () => clearTimeout(timer);
  }, [confidenceWarning]);

  // Auto-dismiss the "heard" chip after 10 seconds — matches the longer
  // dwell time we use for error toasts. Earlier 3 s was too quick for a
  // kitchen kiosk where the user may be looking at ingredients, not the
  // chip, when their voice was transcribed.
  useEffect(() => {
    if (!heardChip) return;
    const timer = setTimeout(() => setHeardChip(null), 10000);
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
      {confidenceWarning && (
        <span className="text-xs text-warning bg-warning/10 px-2 py-1 rounded-full">
          {confidenceWarning}
        </span>
      )}
    </div>
  );
}
