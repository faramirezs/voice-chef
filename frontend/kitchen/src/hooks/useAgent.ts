import { useCallback, useRef, useState } from "react";
import { v4 as uuid } from "uuid";
import {
  type Message,
  type AgentSubscriber,
  type RunAgentResult,
  EventType,
  type StateSnapshotEvent,
  type StateDeltaEvent,
} from "@ag-ui/client";
import { chefAgent } from "@/lib/agent";

export interface ToolActivity {
  toolCallId: string;
  toolName: string;
  status: "running" | "done" | "failed";
  result?: string;
  startedAt: number;
}

function normalizeToolName(name: string | undefined): string {
  const raw = (name ?? "tool").trim();
  if (!raw) return "Tool";
  return raw
    .replace(/[_-]+/g, " ")
    .replace(/\s+/g, " ")
    .replace(/\b\w/g, (c) => c.toUpperCase());
}


function applyPatchReplace(
  obj: Record<string, unknown>,
  pointer: string,
  value: unknown
): void {
  const parts = pointer.split("/").slice(1); // skip leading /
  if (parts.length === 0) return;

  let target: unknown = obj;
  for (let i = 0; i < parts.length - 1; i++) {
    const key = parts[i];
    if (target == null || typeof target !== "object") return;
    const arr = target as unknown[];
    const idx = Number(key);
    target = Array.isArray(target) && !Number.isNaN(idx)
      ? arr[idx]
      : (target as Record<string, unknown>)[key];
  }

  const lastKey = parts[parts.length - 1];
  if (target == null || typeof target !== "object") return;

  if (Array.isArray(target)) {
    const idx = Number(lastKey);
    if (!Number.isNaN(idx)) target[idx] = value;
  } else {
    (target as Record<string, unknown>)[lastKey] = value;
  }
}
export function useAgent() {
  const debugStream = import.meta.env.VITE_AGENT_DEBUG_STREAM === "1";
  const [messages, setMessages] = useState<Message[]>([]);
  const [isStreaming, setIsStreaming] = useState(false);
  const [toolActivity, setToolActivity] = useState<ToolActivity[]>([]);
  const [agentState, setAgentState] = useState<unknown>(null);
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
      setToolActivity([]);

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
        onStateSnapshotEvent({ event }: { event: StateSnapshotEvent }) {
          if (debugStream) {
            console.log("[agent-debug] STATE_SNAPSHOT", event.snapshot);
          }
          setAgentState(event.snapshot);
        },
        onStateDeltaEvent({ event }: { event: StateDeltaEvent }) {
          if (debugStream) {
            console.log("[agent-debug] STATE_DELTA", event.delta);
          }
          setAgentState((prev) => {
            if (prev == null || typeof prev !== "object") return prev;
            let next = { ...(prev as Record<string, unknown>) };
            for (const op of event.delta) {
              if (op.op === "replace") {
                applyPatchReplace(next, op.path, op.value);
              }
            }
            return next;
          });
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
            const toolCallId = e.toolCallId ?? "";
            const toolName = normalizeToolName(e.toolCallName);
            setToolActivity((prev) => {
              const existingIndex = prev.findIndex((p) => p.toolCallId === toolCallId);
              if (existingIndex >= 0) {
                return prev.map((item, i) =>
                  i === existingIndex ? { ...item, toolName, status: "running" } : item
                );
              }
              return [
                ...prev,
                {
                  toolCallId,
                  toolName,
                  status: "running",
                  startedAt: Date.now(),
                },
              ];
            });
          }
          if (event.type === EventType.TOOL_CALL_END) {
            const e = event as { toolCallId?: string };
            const toolCallId = e.toolCallId ?? "";
            setToolActivity((prev) =>
              prev.map((item) =>
                item.toolCallId === toolCallId && item.status === "running"
                  ? { ...item, status: "done" }
                  : item
              )
            );
          }
          if (event.type === EventType.TOOL_CALL_RESULT) {
            const e = event as { toolCallId?: string; content?: string };
            setToolActivity((prev) => {
              const toolCallId = e.toolCallId ?? "";
              return prev.map((item) =>
                item.toolCallId === toolCallId
                  ? { ...item, status: "done", result: e.content ?? "" }
                  : item
              );
            });
            syncMessages();
          }
          if (event.type === EventType.RUN_ERROR) {
            setToolActivity((prev) =>
              prev.map((item) =>
                item.status === "running" ? { ...item, status: "failed" } : item
              )
            );
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
        setToolActivity((prev) =>
          prev.map((item) =>
            item.status === "running" ? { ...item, status: "failed" } : item,
          ),
        );
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
    setToolActivity([]);
    setAgentState(null);
    threadIdRef.current = uuid();
  }, []);

  const sortedToolActivity = [...toolActivity].sort((a, b) => a.startedAt - b.startedAt);

  return { messages, isStreaming, toolActivity: sortedToolActivity, agentState, sendMessage, reset };
}
