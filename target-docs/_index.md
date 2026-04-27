# Target Documentation Index

## Total Concepts: 33

## Concept Map

| ID | Concept | Dependencies | Complexity | Domain |
|----|---------|--------------|------------|--------|
| C01 | Docker Compose Multi-Service Architecture | none | foundational | System |
| C02 | Kitchen Frontend vs Office Frontend | C01 | foundational | System |
| C03 | Backend REST API (FastAPI) | C01 | foundational | System |
| C04 | Agent Service (Pydantic AI) | C01, C03 | intermediate | System |
| C05 | AG-UI Protocol | C04 | intermediate | Protocol |
| C06 | HttpAgent (frontend client) | C05 | intermediate | Protocol |
| C07 | RunAgentInput | C05 | intermediate | Protocol |
| C08 | AgentSubscriber | C05 | intermediate | Protocol |
| C09 | Event Types (STATE_SNAPSHOT, STATE_DELTA, etc.) | C05 | intermediate | Protocol |
| C10 | Bidirectional State | C05, C07 | advanced | Protocol |
| C11 | Agent definition (Pydantic AI) | C04 | intermediate | Backend |
| C12 | StateDeps / StateHandler | C11 | advanced | Backend |
| C13 | @agent.instructions | C11, C12 | advanced | Backend |
| C14 | @agent.tool vs @agent.tool_plain | C11 | intermediate | Backend |
| C15 | RunContext | C14 | advanced | Backend |
| C16 | AGUIAdapter.dispatch_request | C11, C05 | advanced | Backend |
| C17 | Tool return to Event conversion | C14, C09 | advanced | Backend |
| C18 | KitchenState | C12 | intermediate | State |
| C19 | Dual-State Architecture | C18, C06, C09 | advanced | State |
| C20 | stopPropagation pattern | C19, C09 | advanced | State |
| C21 | JSON Patch / State Delta | C09 | intermediate | State |
| C22 | TSX / JSX | none | foundational | Frontend |
| C23 | React Hooks | C22 | foundational | Frontend |
| C24 | React Context API | C22, C23 | intermediate | Frontend |
| C25 | Lazy Loading + Suspense | C22 | intermediate | Frontend |
| C26 | Module-level shared stores | C23 | advanced | Frontend |
| C27 | Slot-based Layout System | C22 | intermediate | Frontend |
| C28 | Component Registry | C25, C27 | intermediate | Frontend |
| C29 | useEnvelope subscription | C26, C08 | advanced | Frontend |
| C30 | Typed UI Envelopes | C05, C28 | intermediate | Frontend |
| C31 | Voice Input to Agent pipeline | C06, C03 | intermediate | System |
| C32 | Tool Activity Tracking | C08, C09 | intermediate | Frontend |
| C33 | Envelope Pattern (structured results) | C30 | intermediate | Backend |

## Key Themes

- **System Architecture**: covers C01, C02, C03, C04, C31
- **AG-UI Protocol & Events**: covers C05, C06, C07, C08, C09, C10
- **Pydantic AI Agent Backend**: covers C11, C12, C13, C14, C15, C16, C17
- **Bidirectional State Management**: covers C18, C19, C20, C21
- **React / TSX Frontend Patterns**: covers C22, C23, C24, C25, C26
- **Slot & Component System**: covers C27, C28, C29, C30

## Coverage Baseline

Total atomic concepts: 33
Estimated questions to full coverage: 50

---

## Source Files Ingested

- `ag-ui/ag-ui-reference.md` — AG-UI protocol reference, event types, envelope patterns
- `ag-ui/ag-ui-state-reference.md` — Bidirectional state, dual-state architecture, KitchenState
- `frontend/kitchen/src/hooks/useAgent.ts` — AG-UI client hook, shared stores, envelope system
- `frontend/kitchen/src/lib/agent.ts` — HttpAgent initialization
- `frontend/kitchen/src/agent-ui/types.ts` — Slot types, render instruction types
- `frontend/kitchen/src/agent-ui/registry.ts` — Component registry, lazy loading
- `frontend/kitchen/src/components/layout/HudCanvas.tsx` — Slot layout composition
- `frontend/kitchen/src/components/layout/AgentSlotProvider.tsx` — React Context for slots
- `frontend/kitchen/src/components/layout/SlotOutlet.tsx` — Slot rendering with Suspense
- `frontend/kitchen/src/components/recipe/RecipeDetailCard.tsx` — Complex component consuming state
- `frontend/kitchen/src/components/chat/VoiceInput.tsx` — Voice → STT → text pipeline
- `frontend/kitchen/src/types/agent-state.ts` — KitchenState TypeScript interface
- `agent/app/agent.py` — Agent tools, system prompt, envelopes
- `agent/app/main.py` — FastAPI endpoint, AGUIAdapter.dispatch_request
- `agent/app/state.py` — KitchenState Pydantic model
- `ag-ui/AGENTS.md` — Project architecture overview

## Data Flow Summary

```
[Browser - Kitchen]
  VoiceInput → STT service → text
  text → sendMessage() → chefAgent.runAgent()
    ↓ POST / (RunAgentInput: state + messages + context)
[Agent Service]
  AGUIAdapter → pydantic-ai Agent → LLM (OpenRouter)
  Agent tools → backend REST API → PostgreSQL
  Tool results → typed envelopes / STATE_SNAPSHOT / STATE_DELTA
    ↓ SSE stream
[Browser - Kitchen]
  Subscriber → onStateSnapshotEvent / onStateDeltaEvent
  _setSharedAgentState() → components re-render
  SlotOutlet → registry lookup → React component + props
```

## Critical Patterns

1. **Dual-State**: `chefAgent.state` holds KitchenState for outbound requests; `_agentState` holds widget state from inbound events. `stopPropagation: true` prevents collision.
2. **Envelopes**: Every tool result is a dict with `type` + `version`. Frontend parses once, then renders typed components.
3. **Slots**: Agent renders UI by name into named slots (canvas, chips, etc.). Registry maps names to lazy-loaded React components.
4. **StateDeps**: Agent declares `deps_type=StateDeps[KitchenState]`. Adapter injects request body state into `ctx.deps.state`. Tools read state to avoid asking redundant questions.
