import { useCallback, useRef, useState } from "react";
import { v4 as uuid } from "uuid";
import {
  type Message,
  type AgentSubscriber,
  type RunAgentResult,
  EventType,
} from "@ag-ui/client";
import { chefAgent } from "@/lib/agent";

export interface ToolActivity {
  toolCallId: string;
  toolName: string;
  result?: string;
}

export function useAgent() {
  const debugStream = import.meta.env.VITE_AGENT_DEBUG_STREAM === "1";
  const [messages, setMessages] = useState<Message[]>([]);
  const [isStreaming, setIsStreaming] = useState(false);
  const [toolActivity, setToolActivity] = useState<ToolActivity | null>(null);
  const threadIdRef = useRef(uuid());

  const syncMessages = useCallback(() => {
    setMessages([...chefAgent.messages]);
  }, []);

  const sendMessage = useCallback(
    async (text: string) => {
      const userMsg: Message = {
        id: uuid(),
        role: "user",
        content: text,
      };

      chefAgent.addMessage(userMsg);
      setMessages([...chefAgent.messages]);
      setIsStreaming(true);
      setToolActivity(null);

      if (debugStream) {
        console.log("[agent-debug] run:start", {
          at: new Date().toISOString(),
          textLength: text.length,
        });
      }

      const subscriber: AgentSubscriber = {
        onTextMessageContentEvent(input) {
          if (debugStream) {
            console.log("[agent-debug] event:TEXT_MESSAGE_CONTENT", {
              at: new Date().toISOString(),
              deltaLength: String(input?.event?.delta ?? "").length,
            });
          }
          syncMessages();
        },
        onTextMessageEndEvent(input) {
          if (debugStream) {
            console.log("[agent-debug] event:TEXT_MESSAGE_END", {
              at: new Date().toISOString(),
              messageId: input?.event?.messageId,
            });
          }
          syncMessages();
        },
        onEvent({ event }) {
          if (debugStream) {
            console.log("[agent-debug] event", {
              at: new Date().toISOString(),
              type: event.type,
            });
          }

          if (event.type === EventType.TOOL_CALL_START) {
            const e = event as { toolCallName?: string; toolCallId?: string };
            setToolActivity({
              toolCallId: e.toolCallId ?? "",
              toolName: e.toolCallName ?? "tool",
            });
          }
          if (event.type === EventType.TOOL_CALL_RESULT) {
            const e = event as { toolCallId?: string; content?: string };
            setToolActivity((prev) => {
              if (!prev || prev.toolCallId !== e.toolCallId) return prev;
              return {
                toolCallId: prev.toolCallId,
                toolName: prev.toolName,
                result: e.content ?? "",
              };
            });
            syncMessages();
          }
        },
      };

      try {
        const result: RunAgentResult = await chefAgent.runAgent(
          { runId: uuid() },
          subscriber,
        );
        if (debugStream) {
          console.log("[agent-debug] run:finished", {
            at: new Date().toISOString(),
            result,
          });
        }
        void result;
      } catch (err) {
        console.error("Agent run failed:", err);
        const errorMsg: Message = {
          id: uuid(),
          role: "assistant",
          content:
            "Sorry, something went wrong reaching the kitchen assistant. Please try again.",
        };
        chefAgent.addMessage(errorMsg);
      } finally {
        if (debugStream) {
          console.log("[agent-debug] run:end", {
            at: new Date().toISOString(),
          });
        }
      }

      syncMessages();
      setIsStreaming(false);
    },
    [syncMessages],
  );

  const reset = useCallback(() => {
    chefAgent.setMessages([]);
    setMessages([]);
    setToolActivity(null);
    threadIdRef.current = uuid();
  }, []);

  return { messages, isStreaming, toolActivity, sendMessage, reset };
}
