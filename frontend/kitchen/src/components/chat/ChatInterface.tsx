import { useEffect, useRef, useState, type FormEvent } from "react";
import { useAgent } from "@/hooks/useAgent";
import { KButton } from "@/components/ui/KButton";
import { KInput } from "@/components/ui/KInput";
import { MessageBubble } from "./MessageBubble";
import { VoiceInput } from "./VoiceInput";
import type { ToolActivity } from "@/hooks/useAgent";
import type { Message } from "@ag-ui/client";

function StreamingDots() {
  return (
    <div className="flex gap-1 items-center px-5 py-3">
      <span className="h-2.5 w-2.5 rounded-full bg-primary animate-bounce [animation-delay:0ms]" />
      <span className="h-2.5 w-2.5 rounded-full bg-primary animate-bounce [animation-delay:150ms]" />
      <span className="h-2.5 w-2.5 rounded-full bg-primary animate-bounce [animation-delay:300ms]" />
    </div>
  );
}

function ToolCallActivityRow({ activity }: { activity: ToolActivity }) {
  const statusConfig = {
    running: {
      icon: (
        <span className="inline-block h-2.5 w-2.5 rounded-full bg-primary animate-pulse" />
      ),
      label: "Running",
      badgeClass: "bg-primary/20 text-primary border border-primary/30",
    },
    done: {
      icon: <span className="inline-block h-2.5 w-2.5 rounded-full bg-success" />,
      label: "Done",
      badgeClass: "bg-success/15 text-success border border-success/30",
    },
    failed: {
      icon: <span className="inline-block h-2.5 w-2.5 rounded-full bg-error" />,
      label: "Failed",
      badgeClass: "bg-error/15 text-error border border-error/30",
    },
  }[activity.status];

  return (
    <div className="flex items-center justify-between gap-3 rounded-xl border border-border/65 bg-surface-alt/65 px-3 py-2 text-sm">
      <div className="flex items-center gap-2 min-w-0">
        {statusConfig.icon}
        <span className="truncate text-text">{activity.toolName}</span>
      </div>
      <span
        className={`flex-shrink-0 rounded-full px-2 py-0.5 text-xs font-medium ${statusConfig.badgeClass}`}
      >
        {statusConfig.label}
      </span>
    </div>
  );
}

function isMeaninglessToolContent(content: unknown): boolean {
  if (content == null) return true;

  if (typeof content === "string") {
    const normalized = content.trim();
    return (
      normalized === "" ||
      normalized === '""' ||
      normalized === "''" ||
      normalized === "null" ||
      normalized === "{}"
    );
  }

  if (typeof content === "object") {
    return Object.keys(content as Record<string, unknown>).length === 0;
  }

  return false;
}

function hasToolCalls(message: Message): boolean {
  const maybeToolCalls = (message as Message & { toolCalls?: unknown }).toolCalls;
  return Array.isArray(maybeToolCalls) && maybeToolCalls.length > 0;
}

function shouldHideAssistantNarration(messages: Message[], index: number): boolean {
  const message = messages[index];
  if (message.role !== "assistant") return false;

  const text =
    typeof message.content === "string"
      ? message.content.trim()
      : JSON.stringify(message.content ?? "").trim();

  if (isMeaninglessToolContent(text)) return true;
  if (hasToolCalls(message)) return false;

  const previousMessage = messages[index - 1];
  if (!previousMessage || previousMessage.role !== "tool") {
    return false;
  }

  return !isMeaninglessToolContent(previousMessage.content);
}

export function ChatInterface() {
  const { messages, isStreaming, toolActivity, sendMessage, reset } =
    useAgent();
  const visibleMessages = messages.filter(
    (_msg, index) => !shouldHideAssistantNarration(messages, index),
  );
  const [input, setInput] = useState("");
  const bottomRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLInputElement>(null);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [visibleMessages, isStreaming, toolActivity]);

  const handleSubmit = (e: FormEvent) => {
    e.preventDefault();
    const text = input.trim();
    if (!text || isStreaming) return;
    setInput("");
    sendMessage(text);
  };

  const handleVoiceTranscript = (text: string) => {
    setInput(text);
    inputRef.current?.focus();
  };

  return (
    <div className="h-full flex flex-col bg-surface/85 backdrop-blur-sm">
      {/* Header */}
      <header className="flex-shrink-0 flex items-center justify-between px-6 py-4 border-b border-border/70 bg-surface-alt/80 backdrop-blur-sm shadow-[0_8px_24px_rgba(0,0,0,0.22)]">
        <h1 className="text-xl font-semibold tracking-tight text-text">
          Voice chef
        </h1>
        <KButton
          type="button"
          onClick={reset}
          variant="ghost"
          className="h-auto px-3 py-1.5 text-sm rounded-xl bg-transparent ring-transparent hover:bg-surface hover:ring-border/70"
        >
          New chat
        </KButton>
      </header>

      {/* Messages */}
      <div className="flex-1 overflow-y-auto px-4 py-6 space-y-4 bg-[#FCFFEF]">
        {messages.length === 0 && (
          <div className="flex flex-col items-center justify-center h-full text-center text-text-muted space-y-3">
            <p className="text-2xl text-text">Ask me anything about recipes</p>
            <p className="text-base">
              Try: "Recalculate recipe X for Y portions" or "Show me
              chicken recipes"
            </p>
          </div>
        )}

        {visibleMessages.map((msg) => (
          <MessageBubble key={msg.id} message={msg} />
        ))}

        {toolActivity.length > 0 && (
          <div className="space-y-2 px-2">
            {toolActivity.map((activity) => (
              <ToolCallActivityRow
                key={activity.toolCallId || `${activity.toolName}-${activity.status}`}
                activity={activity}
              />
            ))}
          </div>
        )}

        {isStreaming && <StreamingDots />}

        <div ref={bottomRef} />
      </div>

      {/* Input bar */}
      <form
        onSubmit={handleSubmit}
        className="flex-shrink-0 flex items-center gap-3 px-4 py-4 border-t border-border/70 bg-surface-alt/80 backdrop-blur-sm"
      >
        <VoiceInput
          onTranscript={handleVoiceTranscript}
          disabled={isStreaming}
        />

        <KInput
          ref={inputRef}
          type="text"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          placeholder="Ask the kitchen assistant..."
          disabled={isStreaming}
          className="flex-1"
        />

        <KButton
          type="submit"
          disabled={isStreaming || !input.trim()}
          size="default"
          className="flex-shrink-0"
        >
          Send
        </KButton>
      </form>
    </div>
  );
}
