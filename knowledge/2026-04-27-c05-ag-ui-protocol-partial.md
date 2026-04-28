---
id: 2026-04-27-c05
concept: AG-UI Protocol
source-coverage: C05
created: 2026-04-27
---

# AG-UI Protocol (partial)

AG-UI is a wire protocol between frontend and agent. The agent exposes a POST endpoint (/) that the frontend fetches. The response is NOT a single JSON blob — it is a stream of server-sent events (SSE). AG-UI provides a grammar of event types that structure this stream: tool calls, text deltas, state changes, etc.

## In Their Words
> "The agent service exposes a /post endpoint that can be fetched by the frontend. The frontend needs to send requests in a very specific way, and there is a stream of data coming from the agent — thinking, calling tools, sending text. AG-UI provides a grammar for the agent to follow these patterns."

## Connections
- [[2026-04-27-c04-agent-service]] enables — AG-UI is the protocol that connects frontend to the agent service
- [[2026-04-27-c08-agent-subscriber-partial]] enables — the subscriber is how the frontend consumes this stream

## Open Questions
- Does not yet know the specific event type names (STATE_SNAPSHOT, STATE_DELTA, TOOL_CALL_START, etc.)
- Does not yet know the request body shape (RunAgentInput)

## Tags
#protocol #intermediate #partial
