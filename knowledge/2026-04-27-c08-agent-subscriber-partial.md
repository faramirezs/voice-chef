---
id: 2026-04-27-c08
concept: AgentSubscriber (partial)
source-coverage: C08
created: 2026-04-27
---

# AgentSubscriber (partial)

In useAgent.ts, there is a subscriber object with callback functions that handle different event types from the SSE stream. Each callback corresponds to a specific event type: onTextMessageContentEvent for text deltas, onTextMessageEndEvent for text completion, onStateSnapshotEvent for state snapshots, onStateDeltaEvent for incremental state patches, and onEvent as a catch-all that filters by event.type (e.g., EventType.TOOL_CALL_START).

## In Their Words
> "In the useAgent.ts hook there is a useAgent function that gets the data. onTextMessageEndEvent for end text, onTextMessageContentEvent for text content, onStateSnapshotEvent for snapshots, onStateDeltaEvent for delta, onEvent gets events and then we filter with if like if (event.type === EventType.TOOL_CALL_START)."

## Connections
- [[2026-04-27-c05-ag-ui-protocol-partial]] enables — the subscriber consumes the AG-UI protocol stream

## Open Questions
- Does not yet know what the subscriber does AFTER receiving events (shared stores, re-rendering, etc.)
- Does not yet know why some callbacks return { stopPropagation: true }

## Tags
#protocol #intermediate #partial
