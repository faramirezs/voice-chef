import { useCallback } from "react";
import { getSendMessage, useIsStreaming } from "./useAgent";
import { chefAgent } from "@/lib/agent";
import { type KitchenState } from "@/types/agent-state";
import { type SttResult } from "@/components/chat/VoiceInput";
import { openPalette } from "@/lib/palette-state";

export interface VoiceSubmitResult {
  submitted: boolean;
  warning?: string;
}

export function useVoiceSubmit() {
  const isStreaming = useIsStreaming();

  return useCallback(
    (text: string, sttResult?: SttResult): VoiceSubmitResult => {
      if (isStreaming) {
        return { submitted: false };
      }
      const trimmed = text.trim();
      if (!trimmed) {
        return { submitted: false };
      }

      let agentText = trimmed;
      let warning: string | undefined;

      if (sttResult && sttResult.confidence !== "high") {
        agentText = `[voice, confidence: ${sttResult.confidence}, language: ${sttResult.language}]\n${agentText}`;
        warning = "Low confidence — review before sending";
      }

      const currentState = chefAgent.state as KitchenState | null;
      const ks: KitchenState = currentState && typeof currentState.view === "string"
        ? { ...currentState, last_action: { type: "voice", timestamp: Date.now() } }
        : { view: "empty", selected_recipe: null, scaling: null, last_action: { type: "voice", timestamp: Date.now() } };
      chefAgent.setState(ks);
      openPalette();
      getSendMessage()(agentText);

      return { submitted: true, warning };
    },
    [isStreaming],
  );
}
