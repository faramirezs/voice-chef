# Learning Route

## Overview
Build mental model from outside in: system picture, then protocol, then backend, then frontend rendering. Arc: "what exists" -> "how it talks" -> "how it thinks" -> "how it shows."

## Sessions

### Session 1 — System Architecture (4 concepts) — IN PROGRESS
- [x] C01: Docker Compose Multi-Service Architecture — COVERED
- [ ] C02: Kitchen Frontend vs Office Frontend — not yet asked
- [x] C03: Backend REST API (FastAPI) — COVERED
- [x] C04: Agent Service (Pydantic AI) — COVERED

### Session 2 — AG-UI Protocol (6 concepts)
- [~] C05: AG-UI Protocol — PARTIAL (knows endpoint + stream + grammar, not event types or request shape)
- [ ] C06: HttpAgent — frontend client that sends requests
- [ ] C07: RunAgentInput — the request body shape
- [~] C08: AgentSubscriber — PARTIAL (knows callback names, not post-processing or stopPropagation)
- [ ] C09: Event Types — STATE_SNAPSHOT, STATE_DELTA, TOOL_CALL_*, etc.
- [ ] C10: Bidirectional State — frontend sends state, agent receives it

### Session 3 — Pydantic AI Agent Backend (7 concepts)
- [ ] C11: Agent definition — model, system_prompt, deps_type
- [ ] C12: StateDeps / StateHandler — how state enters the agent
- [ ] C13: @agent.instructions — dynamic prompt injection from state
- [ ] C14: @agent.tool vs @agent.tool_plain — context access difference
- [ ] C15: RunContext — tool access to deps/state
- [ ] C16: AGUIAdapter.dispatch_request — HTTP to agent bridge
- [ ] C17: Tool return to Event conversion

### Session 4 — Bidirectional State (4 concepts)
- [ ] C18: KitchenState — shared state model
- [ ] C19: Dual-State Architecture — chefAgent.state vs _agentState
- [ ] C20: stopPropagation pattern — protecting chefAgent.state
- [ ] C21: JSON Patch / State Delta operations

### Session 5 — React / TSX Frontend (5 concepts)
- [ ] C22: TSX / JSX — HTML-like syntax in JavaScript
- [ ] C23: React Hooks — useState, useEffect, useCallback, useSyncExternalStore
- [ ] C24: React Context API — AgentSlotProvider
- [ ] C25: Lazy Loading + Suspense — component registry
- [ ] C26: Module-level shared stores — outside React state

### Session 6 — Slot & Component System (4 concepts)
- [ ] C27: Slot-based Layout System — canvas, sticky, chips, notifications, overlay
- [ ] C28: Component Registry — string to React component mapping
- [ ] C29: useEnvelope subscription — type-based message routing
- [ ] C30: Typed UI Envelopes — type + version discriminator

### Session 7 — Wiring & Data Flow (3 concepts)
- [ ] C31: Voice Input to Agent pipeline
- [ ] C32: Tool Activity Tracking
- [ ] C33: Envelope Pattern — structured tool results

## Route Rationale
Start with visible containers (Docker), move to wire protocol (AG-UI), then backend logic (Pydantic AI), then frontend rendering (React/TSX). Each session builds a traceable slice before adding the next abstraction.

## Next Session Start
Resume with C02 (Kitchen vs Office Frontend) to finish Session 1, then deepen C05 and C08 before continuing Session 2.
