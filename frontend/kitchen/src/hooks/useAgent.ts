import { useCallback, useEffect, useSyncExternalStore, useRef, useState } from "react";
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

// --- Envelope subscription system ---
// Module-level subscriber map shared between useAgent and useEnvelope.
// This works because there is exactly one agent instance per browser session.
type EnvelopeHandler = (envelope: Record<string, unknown>) => void;
const _envelopeSubscribers = new Map<string, Set<EnvelopeHandler>>();

// --- Shared agent state store ---
// STATE_SNAPSHOT/STATE_DELTA are processed once (in the useAgent subscriber)
// but must be visible to any component (e.g., slotted cards) that wasn't
// part of the original useAgent() call.
let _agentState: unknown = null;
const _agentStateListeners = new Set<() => void>();

function _notifyAgentStateListeners() {
  for (const fn of _agentStateListeners) fn();
}

function _setSharedAgentState(state: unknown) {
  _agentState = state;
  _notifyAgentStateListeners();
}

function _patchSharedAgentState(updater: (prev: unknown) => unknown) {
  _agentState = updater(_agentState);
  _notifyAgentStateListeners();
}

function _clearSharedAgentState() {
  _agentState = null;
  _notifyAgentStateListeners();
}

function _subscribeAgentState(listener: () => void) {
  _agentStateListeners.add(listener);
  return () => { _agentStateListeners.delete(listener); };
}

/** Read the shared agent state from any component. */
export function useAgentState(): unknown {
  return useSyncExternalStore(
    _subscribeAgentState,
    () => _agentState,
  );
}



// --- Shared streaming state store ---
// isStreaming is written by useAgent() but must be readable
// from HudStatusIndicator and other HUD components.
let _isStreaming = false;
const _isStreamingListeners = new Set<() => void>();

function _notifyIsStreamingListeners() {
  for (const fn of _isStreamingListeners) fn();
}

function _setIsStreaming(value: boolean) {
  _isStreaming = value;
  _notifyIsStreamingListeners();
}

function _subscribeIsStreaming(listener: () => void) {
  _isStreamingListeners.add(listener);
  return () => { _isStreamingListeners.delete(listener); };
}

export function useIsStreaming(): boolean {
  return useSyncExternalStore(
    _subscribeIsStreaming,
    () => _isStreaming,
  );
}

// --- Shared tool activity store ---
let _toolActivity: ToolActivity[] = [];
const _toolActivityListeners = new Set<() => void>();

function _notifyToolActivityListeners() {
  for (const fn of _toolActivityListeners) fn();
}

function _setToolActivity(value: ToolActivity[] | ((prev: ToolActivity[]) => ToolActivity[])) {
  _toolActivity = typeof value === "function" ? value(_toolActivity) : value;
  _notifyToolActivityListeners();
}

function _subscribeToolActivity(listener: () => void) {
  _toolActivityListeners.add(listener);
  return () => { _toolActivityListeners.delete(listener); };
}

export function useToolActivity(): ToolActivity[] {
  return useSyncExternalStore(
    _subscribeToolActivity,
    () => _toolActivity,
  );
}

// --- Stable sendMessage / reset getters ---
// These are set by useAgent() once during mount, then callable from any component.
let _sendMessage: ((text: string) => void) | null = null;
let _reset: (() => void) | null = null;

export function getSendMessage(): (text: string) => void {
  if (!_sendMessage) throw new Error("Agent not initialized");
  return _sendMessage;
}

export function getReset(): () => void {
  if (!_reset) throw new Error("Agent not initialized");
  return _reset;
}

function emitEnvelope(raw: string): void {
  let parsed: unknown;
  try {
    parsed = JSON.parse(raw);
  } catch {
    console.warn("[emitEnvelope] JSON parse failed for:", raw.slice(0, 200));
    return;
  }
  if (
    typeof parsed !== "object" ||
    parsed === null ||
    typeof (parsed as Record<string, unknown>).type !== "string"
  ) {
    console.warn("[emitEnvelope] Invalid envelope shape:", parsed);
    return;
  }
  const envelope = parsed as Record<string, unknown>;
  const envelopeType = envelope.type as string;
  console.log("[emitEnvelope] type=", envelopeType, envelope);
  const handlers = _envelopeSubscribers.get(envelopeType);
  if (handlers) {
    for (const handler of handlers) {
      handler(envelope);
    }
  } else {
    console.warn("[emitEnvelope] No handlers for type:", envelopeType);
  }
}

export function useEnvelope(
  type: string,
  handler: EnvelopeHandler
): void {
  const handlerRef = useRef(handler);
  handlerRef.current = handler;

  useEffect(() => {
    let set = _envelopeSubscribers.get(type);
    if (!set) {
      set = new Set();
      _envelopeSubscribers.set(type, set);
    }
    const stable = (e: Record<string, unknown>) => handlerRef.current(e);
    set.add(stable);
    return () => {
      set!.delete(stable);
      if (set!.size === 0) _envelopeSubscribers.delete(type);
    };
  }, [type]);
}

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
      _setIsStreaming(true);
      setToolActivity([]);
      _setToolActivity([]);

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
          _setSharedAgentState(event.snapshot);
        },
        onStateDeltaEvent({ event }: { event: StateDeltaEvent }) {
          if (debugStream) {
            console.log("[agent-debug] STATE_DELTA", event.delta);
          }
          setAgentState((prev: unknown) => {
            if (prev == null || typeof prev !== "object") return prev;
            let next = { ...(prev as Record<string, unknown>) };
            for (const op of event.delta) {
              if (op.op === "replace") {
                applyPatchReplace(next, op.path, op.value);
              }
            }
            return next;
          });
          _patchSharedAgentState((prev) => {
            if (prev == null || typeof prev !== "object") return prev;
            const next = { ...(prev as Record<string, unknown>) };
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
            _setToolActivity((prev) => {
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
            _setToolActivity((prev) =>
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
            _setToolActivity((prev) => {
              const toolCallId = e.toolCallId ?? "";
              return prev.map((item) =>
                item.toolCallId === toolCallId
                  ? { ...item, status: "done", result: e.content ?? "" }
                  : item
              );
            });
            if (e.content) emitEnvelope(e.content);
            syncMessages();
          }
          if (event.type === EventType.RUN_ERROR) {
            setToolActivity((prev) =>
              prev.map((item) =>
                item.status === "running" ? { ...item, status: "failed" } : item
              )
            );
            _setToolActivity((prev) =>
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
        _setToolActivity((prev) =>
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
      _setIsStreaming(false);
    },
    [syncMessages],
  );

  const reset = useCallback(() => {
    chefAgent.setMessages([]);
    setMessages([]);
    setToolActivity([]);
    _setToolActivity([]);
    setAgentState(null);
    _clearSharedAgentState();
    _setIsStreaming(false);
    threadIdRef.current = uuid();
  }, []);
  const sortedToolActivity = [...toolActivity].sort((a, b) => a.startedAt - b.startedAt);

  _sendMessage = sendMessage;
  _reset = reset;

  return { messages, isStreaming, toolActivity: sortedToolActivity, agentState, sendMessage, reset };
}
