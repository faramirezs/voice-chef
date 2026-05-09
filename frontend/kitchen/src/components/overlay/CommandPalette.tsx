import { useVoiceSubmit } from "@/hooks/useVoiceSubmit";
import { type SttResult } from "@/components/chat/VoiceInput";
import { useCallback, useEffect, useMemo, useRef, useState } from "react";
import { KCard } from "@/components/ui/KCard";
import { KButton } from "@/components/ui/KButton";
import { KInput } from "@/components/ui/KInput";
import { VoiceInput } from "@/components/chat/VoiceInput";
import { getSendMessage, useEnvelope, useIsStreaming, setSharedAgentState, getAbortAgent } from "@/hooks/useAgent";
import { useAgentSlots } from "@/components/layout/AgentSlotProvider";
import { cn } from "@/lib/utils";
import { chefAgent } from "@/lib/agent";
import { useRecipeScaling } from "@/hooks/useRecipeScaling";
import { type KitchenState } from "@/types/agent-state";
import { closePalette } from "@/lib/palette-state";

interface CommandItem {
  id: string;
  label: string;
  action: () => void;
}

export function CommandPalette() {
  const { dispatch, clear } = useAgentSlots();
  const [query, setQuery] = useState("");
  const [results, setResults] = useState<Array<{ id: string; name: string }>>([]);
  const [confidenceWarning, setConfidenceWarning] = useState("");
  const { activateScaling } = useRecipeScaling();
  const submitVoice = useVoiceSubmit();
  const [selectedIndex, setSelectedIndex] = useState(0);
  const isStreaming = useIsStreaming();
  const inputRef = useRef<HTMLInputElement>(null);

  const isCommandMode = query.startsWith("/");

  const commands = useMemo<CommandItem[]>(
    () => [
      {
        id: "/show-all",
        label: "/show-all — Browse all recipes",
        action: () => {
          const ks: KitchenState = {
            view: "recipe_list",
            selected_recipe: null,
            scaling: null,
            last_action: { type: "browse", timestamp: Date.now() },
          };
          chefAgent.setState(ks);
          dispatch("canvas", "recipe_list", {});
        },
      },
      {
        id: "/scale",
        label: "/scale — Scale current recipe",
        action: async () => {
          const result = await activateScaling();
          if (!result.success) {
            dispatch("notifications", "notification", {
              message: result.error ?? "Cannot scale recipe",
              level: "warning",
              duration: 4000,
            });
          }
        },
      },
      {
        id: "/clear",
        label: "/clear — Clear canvas",
        action: () => {
          clear("canvas");
          setSharedAgentState(null);
          chefAgent.setState({
            view: "empty",
            selected_recipe: null,
            scaling: null,
            last_action: { type: "clear", timestamp: Date.now() },
          });
          closePalette();
        },
      },
    ],
    [dispatch, clear, activateScaling]
  );
  const filteredCommands = useMemo(() => {
    if (!isCommandMode) return [];
    const term = query.slice(1).toLowerCase();
    return commands.filter((c) => c.id.toLowerCase().includes(term));
  }, [isCommandMode, query, commands]);

  // Auto-focus input on mount
  useEffect(() => {
    inputRef.current?.focus();
  }, []);

  // Escape closes palette; aborts agent if streaming.
  useEffect(() => {
    const handleGlobalKeyDown = (e: KeyboardEvent) => {
      if (e.key === "Escape") {
        if (isStreaming) {
          getAbortAgent()();
        }
        closePalette();
      }
    };
    document.addEventListener("keydown", handleGlobalKeyDown);
    return () => document.removeEventListener("keydown", handleGlobalKeyDown);
  }, [isStreaming]);

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
      const ks: KitchenState = {
        view: "recipe_detail",
        selected_recipe: {
          id: result.id,
          name: result.name,
          portions: null,
          yield_mode: "count",
        },
        scaling: null,
        last_action: { type: "select", timestamp: Date.now() },
      };
      chefAgent.setState(ks);
      getSendMessage()(`show recipe ${result.id}`);
    },
    []
  );

  const handleInputKeyDown = useCallback(
    (e: React.KeyboardEvent<HTMLInputElement>) => {
      const items = isCommandMode
        ? filteredCommands
        : results;

      if (e.key === "ArrowDown") {
        e.preventDefault();
        setSelectedIndex((prev) =>
          items.length > 0 ? (prev + 1) % items.length : 0
        );
      } else if (e.key === "ArrowUp") {
        e.preventDefault();
        setSelectedIndex((prev) =>
          items.length > 0
            ? (prev - 1 + items.length) % items.length
            : 0
        );
      } else if (e.key === "Enter") {
        e.preventDefault();
        if (items.length > 0 && !isStreaming) {
          const item = items[selectedIndex];
          if (item) {
            if (isCommandMode) {
              (item as CommandItem).action();
            } else {
              handleSelectResult(item as { id: string; name: string });
            }
          }
        } else if (!isStreaming && query.trim() && !isCommandMode) {
          const currentState = chefAgent.state as KitchenState | null;
          const ks: KitchenState = currentState && typeof currentState.view === "string"
            ? { ...currentState, last_action: { type: "search", timestamp: Date.now() } }
            : { view: "empty", selected_recipe: null, scaling: null, last_action: { type: "search", timestamp: Date.now() } };
          chefAgent.setState(ks);
          getSendMessage()(query.trim());
          setResults([]);
          setSelectedIndex(0);
        }
      }
    },
    [
      isCommandMode,
      filteredCommands,
      results,
      selectedIndex,
      isStreaming,
      query,
      handleSelectResult,
    ]
  );

  const handleVoiceTranscript = useCallback((text: string, sttResult?: SttResult) => {
    const result = submitVoice(text, sttResult);
    if (result.submitted) {
      setQuery(text);
      setResults([]);
      setSelectedIndex(0);
      if (result.warning) {
        setConfidenceWarning(result.warning);
      }
    }
  }, [submitVoice]);

  // Auto-dismiss low-confidence warning after 4 seconds.
  useEffect(() => {
    if (!confidenceWarning) return;
    const timer = setTimeout(() => setConfidenceWarning(""), 4000);
    return () => clearTimeout(timer);
  }, [confidenceWarning]);


  const activeItems = isCommandMode
    ? filteredCommands.map((c) => ({ id: c.id, name: c.label }))
    : results;

  const showNoResults =
    !isStreaming && query.trim() && activeItems.length === 0;

  return (
    <KCard className="w-full max-w-lg flex flex-col overflow-hidden">
      {/* Input row */}
      <div className="relative flex items-center gap-2 p-4">
        <div className="relative flex-1 flex items-center gap-2">
          <KInput
            ref={inputRef}
            value={query}
            onChange={(e) => {
              setQuery(e.target.value);
              setSelectedIndex(0);
            }}
            onKeyDown={handleInputKeyDown}
            placeholder="Search recipes... (type / for commands)"
            className="w-full"
            disabled={isStreaming}
          />

        </div>
        <VoiceInput
          onTranscript={handleVoiceTranscript}
          onConfidenceWarning={(w) => setConfidenceWarning(w)}
          disabled={isStreaming}
        />
        {confidenceWarning && (
          <span className="absolute -bottom-5 left-4 text-xs text-warning bg-warning/10 px-2 py-0.5 rounded">
            {confidenceWarning}
          </span>
        )}
      </div>

      <div className="flex-1 overflow-y-auto max-h-64 px-4 pb-2 relative">
        {/* Streaming thinking indicator */}
        {isStreaming && (
          <div className="flex items-center justify-center gap-3 py-6">
            <svg
              width="20"
              height="20"
              viewBox="0 0 24 24"
              fill="none"
              stroke="currentColor"
              strokeWidth="2"
              strokeLinecap="round"
              strokeLinejoin="round"
              className="animate-spin text-primary"
            >
              <path d="M21 12a9 9 0 1 1-6.219-8.56" />
            </svg>
            <span className="text-text font-medium">Thinking...</span>
            <KButton
              type="button"
              onClick={() => getAbortAgent()()}
              variant="ghost"
              size="icon"
              className="bg-error text-white ring-error/60 animate-pulse h-10 w-10"
            >
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                <rect x="6" y="6" width="12" height="12" rx="2" />
              </svg>
            </KButton>
          </div>
        )}

        {isCommandMode && query === "/" && (
          <div className="py-1 text-xs text-text-muted uppercase tracking-wide">
            Commands
          </div>
        )}

        {activeItems.length > 0 && !isStreaming && (
          <ul className="space-y-1">
            {activeItems.map((item, index) => (
              <li
                key={item.id}
                className={cn(
                  "px-3 py-2 rounded-lg cursor-pointer transition-colors text-text",
                  index === selectedIndex
                    ? "bg-surface-alt"
                    : "hover:bg-surface-alt/50"
                )}
                onClick={() => {
                  if (isCommandMode) {
                    filteredCommands[index]?.action();
                  } else {
                    handleSelectResult(results[index]);
                  }
                }}
                onMouseEnter={() => setSelectedIndex(index)}
              >
                {item.name}
              </li>
            ))}
          </ul>
        )}

        {showNoResults && (
          <div className="py-4 text-center text-text-muted">
            {isCommandMode ? "No matching commands" : "No results"}
          </div>
        )}
      </div>
    </KCard>
  );
}
