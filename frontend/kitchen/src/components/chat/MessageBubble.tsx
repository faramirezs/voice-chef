import type { Message } from "@ag-ui/client";
import { AgentUIRenderer } from "./AgentUIRenderer";

interface MessageBubbleProps {
  message: Message;
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

export function MessageBubble({ message }: MessageBubbleProps) {
  const isUser = message.role === "user";
  const messageText =
    typeof message.content === "string"
      ? message.content
      : JSON.stringify(message.content ?? "", null, 2);

  if (message.role === "tool") {
    if (isMeaninglessToolContent(message.content)) {
      return null;
    }

    return (
      <div className="flex justify-start">
        <div className="max-w-[90%] rounded-2xl border border-border/70 bg-surface-alt/70 p-2 shadow-[0_10px_24px_rgba(0,0,0,0.2)]">
          <AgentUIRenderer content={message.content} />
        </div>
      </div>
    );
  }

  return (
    <div className={`flex ${isUser ? "justify-end" : "justify-start"}`}>
      <div
        className={`max-w-[85%] rounded-3xl px-5 py-3 text-lg leading-relaxed ring-1 shadow-[0_8px_22px_rgba(0,0,0,0.18)]
          ${
            isUser
              ? "bg-user-bubble text-text ring-border/70"
              : "bg-assistant-bubble text-text ring-border/55"
          }`}
      >
        <p className="whitespace-pre-wrap">{messageText}</p>
      </div>
    </div>
  );
}
