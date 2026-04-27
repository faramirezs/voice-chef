# Learning Route

## Overview
We will build your mental model from the outside in: first the big system picture, then the protocol that connects frontend and agent, then the backend agent mechanics, then the React frontend patterns that render everything. The arc moves from "what exists" to "how it talks" to "how it thinks" to "how it shows."

## Sessions

### Session 1 — System Architecture (4 concepts, ~10 min)
- [ ] C01: Docker Compose Multi-Service Architecture
- [ ] C02: Kitchen Frontend vs Office Frontend
- [ ] C03: Backend REST API (FastAPI)
- [ ] C04: Agent Service (Pydantic AI)

### Session 2 — AG-UI Protocol (6 concepts, ~15 min)
- [ ] C05: AG-UI Protocol — what it is, HTTP streaming, SSE
- [ ] C06: HttpAgent — frontend client that sends requests
- [ ] C07: RunAgentInput — the request body shape
- [ ] C08: AgentSubscriber — event callbacks
- [ ] C09: Event Types — STATE_SNAPSHOT, STATE_DELTA, TOOL_CALL_*, etc.
- [ ] C10: Bidirectional State — frontend sends state, agent receives it

### Session 3 — Pydantic AI Agent Backend (7 concepts, ~18 min)
- [ ] C11: Agent definition — model, system_prompt, deps_type
- [ ] C12: StateDeps / StateHandler — how state enters the agent
- [ ] C13: @agent.instructions — dynamic prompt injection from state
- [ ] C14: @agent.tool vs @agent.tool_plain — context access difference
- [ ] C15: RunContext — tool access to deps/state
- [ ] C16: AGUIAdapter.dispatch_request — HTTP to agent bridge
- [ ] C17: Tool return to Event conversion

### Session 4 — Bidirectional State (4 concepts, ~12 min)
- [ ] C18: KitchenState — shared state model
- [ ] C19: Dual-State Architecture — chefAgent.state vs _agentState
- [ ] C20: stopPropagation pattern — protecting chefAgent.state
- [ ] C21: JSON Patch / State Delta operations

### Session 5 — React / TSX Frontend (5 concepts, ~15 min)
- [ ] C22: TSX / JSX — HTML-like syntax in JavaScript
- [ ] C23: React Hooks — useState, useEffect, useCallback, useSyncExternalStore
- [ ] C24: React Context API — AgentSlotProvider
- [ ] C25: Lazy Loading + Suspense — component registry
- [ ] C26: Module-level shared stores — outside React state

### Session 6 — Slot & Component System (4 concepts, ~12 min)
- [ ] C27: Slot-based Layout System — canvas, sticky, chips, notifications, overlay
- [ ] C28: Component Registry — string to React component mapping
- [ ] C29: useEnvelope subscription — type-based message routing
- [ ] C30: Typed UI Envelopes — type + version discriminator

### Session 7 — Wiring & Data Flow (3 concepts, ~10 min)
- [ ] C31: Voice Input to Agent pipeline
- [ ] C32: Tool Activity Tracking
- [ ] C33: Envelope Pattern — structured tool results

## Route Rationale
As a C/C++ programmer, you are used to compile-time linking and explicit call graphs. Web/React/Pydantic-AI has layers of indirection (hooks, context, event streams, adapters) that make the call graph invisible. This route starts with the visible containers (Docker services), moves to the wire protocol (AG-UI), then to the backend logic (Pydantic AI), then to the frontend rendering (React/TSX). Each session builds a complete slice you can trace end-to-end before adding the next layer of abstraction.
