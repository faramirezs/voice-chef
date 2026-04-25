import { useCallback, useEffect, useRef, useState } from "react";
import { KCard } from "@/components/ui/KCard";
import { KInput } from "@/components/ui/KInput";
import { KButton } from "@/components/ui/KButton";
import { VoiceInput } from "@/components/chat/VoiceInput";
import { getSendMessage, useEnvelope, useIsStreaming } from "@/hooks/useAgent";
import { cn } from "@/lib/utils";

interface CommandPaletteProps {
  onClose: () => void;
}

export function CommandPalette({ onClose }: CommandPaletteProps) {
  const [query, setQuery] = useState("");
  const [results, setResults] = useState<Array<{ id: string; name: string }>>([]);
  const [selectedIndex, setSelectedIndex] = useState(0);
  const isStreaming = useIsStreaming();
  const inputRef = useRef<HTMLInputElement>(null);

  // Auto-focus input on mount
  useEffect(() => {
    inputRef.current?.focus();
  }, []);

  // Escape closes palette
  useEffect(() => {
    const handleGlobalKeyDown = (e: KeyboardEvent) => {
      if (e.key === "Escape") {
        onClose();
      }
    };
    document.addEventListener("keydown", handleGlobalKeyDown);
    return () => document.removeEventListener("keydown", handleGlobalKeyDown);
  }, [onClose]);

  // Subscribe to recipes.list envelopes
  useEnvelope("recipes.list", (envelope) => {
    const rawItems = envelope.items;
    if (!Array.isArray(rawItems)) {
      setResults([]);
      return;
    }
    const mapped = rawItems
      .filter(
        (item): item is { id: string; name: string } =>
          typeof item === "object" &&
          item !== null &&
          typeof (item as Record<string, unknown>).id === "string" &&
          typeof (item as Record<string, unknown>).name === "string"
      )
      .map((item) => ({ id: item.id, name: item.name }));
    setResults(mapped);
    setSelectedIndex(0);
  });

  const handleSelectResult = useCallback(
    (result: { id: string; name: string }) => {
      getSendMessage()(`show recipe ${result.id}`);
      onClose();
    },
    [onClose]
  );

  const handleInputKeyDown = useCallback(
    (e: React.KeyboardEvent<HTMLInputElement>) => {
      if (e.key === "ArrowDown") {
        e.preventDefault();
        setSelectedIndex((prev) =>
          results.length > 0 ? (prev + 1) % results.length : 0
        );
      } else if (e.key === "ArrowUp") {
        e.preventDefault();
        setSelectedIndex((prev) =>
          results.length > 0
            ? (prev - 1 + results.length) % results.length
            : 0
        );
      } else if (e.key === "Enter") {
        e.preventDefault();
        if (results.length > 0 && !isStreaming) {
          const result = results[selectedIndex];
          if (result) {
            handleSelectResult(result);
          }
        } else if (!isStreaming && query.trim()) {
          getSendMessage()(query.trim());
          setResults([]);
          setSelectedIndex(0);
        }
      }
    },
    [results, selectedIndex, isStreaming, query, handleSelectResult]
  );

  const handleVoiceTranscript = useCallback((text: string) => {
    setQuery(text);
    getSendMessage()(text);
    setResults([]);
    setSelectedIndex(0);
  }, []);

  const showNoResults = !isStreaming && query.trim() && results.length === 0;
  const showSearching = isStreaming && query.trim();

  return (
    <KCard className="w-full max-w-lg flex flex-col overflow-hidden">
      {/* Input row */}
      <div className="flex items-center gap-2 p-4">
        <KInput
          ref={inputRef}
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          onKeyDown={handleInputKeyDown}
          placeholder="Search recipes..."
          className="flex-1"
          disabled={isStreaming}
        />
        <VoiceInput onTranscript={handleVoiceTranscript} disabled={isStreaming} />
      </div>

      {/* Results list */}
      <div className="flex-1 overflow-y-auto max-h-64 px-4 pb-2">
        {showSearching && (
          <div className="py-4 text-center text-text-muted">Searching...</div>
        )}

        {results.length > 0 && (
          <ul className="space-y-1">
            {results.map((result, index) => (
              <li
                key={result.id}
                className={cn(
                  "px-3 py-2 rounded-lg cursor-pointer transition-colors text-text",
                  index === selectedIndex
                    ? "bg-surface-alt"
                    : "hover:bg-surface-alt/50"
                )}
                onClick={() => handleSelectResult(result)}
                onMouseEnter={() => setSelectedIndex(index)}
              >
                {result.name}
              </li>
            ))}
          </ul>
        )}

        {showNoResults && (
          <div className="py-4 text-center text-text-muted">No results</div>
        )}
      </div>

      {/* Static action shortcuts */}
      <div className="flex items-center gap-2 p-4 border-t border-border/70">
        <KButton
          type="button"
          onClick={() => {
            getSendMessage()("scale current recipe");
            onClose();
          }}
          className="flex-1"
        >
          Scale current recipe
        </KButton>
        <KButton
          type="button"
          onClick={() => {
            getSendMessage()("clear canvas");
            onClose();
          }}
          className="flex-1"
        >
          Clear canvas
        </KButton>
      </div>
    </KCard>
  );
}
