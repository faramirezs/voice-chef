import { useCallback } from "react";
import { getSendMessage, useIsStreaming } from "./useAgent";
import { chefAgent } from "@/lib/agent";
import { type KitchenState } from "@/types/agent-state";
import { type SttResult } from "@/components/chat/VoiceInput";

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

      const ks: KitchenState = {
        view: "empty",
        selected_recipe: null,
        scaling: null,
        last_action: { type: "search", timestamp: Date.now() },
      };
      chefAgent.setState(ks);
      getSendMessage()(agentText);

      return { submitted: true, warning };
    },
    [isStreaming],
  );
}
