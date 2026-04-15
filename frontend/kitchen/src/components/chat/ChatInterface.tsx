import { useEffect, useRef, useState, type FormEvent } from "react";
import { useAgent } from "@/hooks/useAgent";
import { KButton } from "@/components/ui/KButton";
import { KInput } from "@/components/ui/KInput";
import { MessageBubble } from "./MessageBubble";
import { VoiceInput } from "./VoiceInput";

function StreamingDots() {
  return (
    <div className="flex gap-1 items-center px-5 py-3">
      <span className="h-2.5 w-2.5 rounded-full bg-primary animate-bounce [animation-delay:0ms]" />
      <span className="h-2.5 w-2.5 rounded-full bg-primary animate-bounce [animation-delay:150ms]" />
      <span className="h-2.5 w-2.5 rounded-full bg-primary animate-bounce [animation-delay:300ms]" />
    </div>
  );
}

export function ChatInterface() {
  const { messages, isStreaming, toolActivity, sendMessage, reset } =
    useAgent();
  const [input, setInput] = useState("");
  const bottomRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLInputElement>(null);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, isStreaming, toolActivity]);

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
      <div className="flex-1 overflow-y-auto px-4 py-6 space-y-4">
        {messages.length === 0 && (
          <div className="flex flex-col items-center justify-center h-full text-center text-text-muted space-y-3">
            <p className="text-2xl text-text">Ask me anything about recipes</p>
            <p className="text-base">
              Try: "Recalculate recipe X for Y portions" or "Show me
              chicken recipes"
            </p>
          </div>
        )}

        {messages.map((msg) => (
          <MessageBubble key={msg.id} message={msg} />
        ))}

        {isStreaming && toolActivity && !toolActivity.result && (
          <div className="flex items-center gap-2 text-text-muted text-base px-2">
            <span className="inline-block animate-spin text-lg">&#128269;</span>
            <span>Looking up {toolActivity.toolName}...</span>
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
