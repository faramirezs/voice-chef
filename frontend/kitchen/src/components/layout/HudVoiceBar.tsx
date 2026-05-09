import { useVoiceSubmit } from "@/hooks/useVoiceSubmit";
import { type SttResult } from "@/components/chat/VoiceInput";
import { useState, useCallback, useEffect } from "react";
import { VoiceInput } from "@/components/chat/VoiceInput";

export function HudVoiceBar() {
  const [confidenceWarning, setConfidenceWarning] = useState("");
  const submitVoice = useVoiceSubmit();

  const handleTranscript = useCallback((text: string, sttResult?: SttResult) => {
    const result = submitVoice(text, sttResult);
    if (result.submitted && result.warning) {
      setConfidenceWarning(result.warning);
    }
  }, [submitVoice]);

  // Auto-dismiss low-confidence warning after 8 seconds.
  useEffect(() => {
    if (!confidenceWarning) return;
    const timer = setTimeout(() => setConfidenceWarning(""), 8000);
    return () => clearTimeout(timer);
  }, [confidenceWarning]);

  return (
    <div className="flex items-center justify-center pb-6 gap-4">
      <VoiceInput onTranscript={handleTranscript} />
      {confidenceWarning && (
        <span className="text-xs text-warning bg-warning/10 px-2 py-1 rounded-full">
          {confidenceWarning}
        </span>
      )}
    </div>
  );
}
