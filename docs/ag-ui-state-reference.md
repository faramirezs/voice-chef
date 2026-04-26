# AG-UI Bidirectional State — Reference Document

## Verified Finding: AG-UI Is Bidirectional, Not Unidirectional

The AG-UI protocol supports bidirectional state synchronization between frontend and agent. The mechanism is `RunAgentInput.state`, which the frontend sets before every run and the agent reads at run start.

---

## The State Contract

### Frontend: `RunAgentInput.state`

Every POST to the agent endpoint carries a `RunAgentInput` body:

```typescript
interface RunAgentInput {
  threadId: string
  runId: string
  parentRunId?: string
  state: any           // ← shared state snapshot
  messages: Message[]
  tools: Tool[]
  context: Context[]
  forwardedProps: any
}
```

**Source verified**: `frontend/kitchen/node_modules/@ag-ui/core/dist/index.d.ts` line 2264-2268

The `AbstractAgent` class maintains a `.state` property:

```typescript
abstract class AbstractAgent {
  state: State
  setState(state: State): void  // ← frontend calls this before runAgent()
  // ...
}
```

**Source verified**: `frontend/kitchen/node_modules/@ag-ui/client/dist/index.d.ts` line 457, 503

When `chefAgent.runAgent()` is called, the HttpAgent constructs the HTTP request body including the current `this.state` value.

---

### Backend: How the Agent Receives State

The `AGUIAdapter` (pydantic-ai side) extracts state from the incoming request:

```python
class AGUIAdapter(UIAdapter):
    @cached_property
    def state(self) -> dict[str, Any] | None:
        state = self.run_input.state  # ← from RunAgentInput body
        if state is None:
            return None
        if isinstance(state, Mapping) and not state:
            return None
        return cast('dict[str, Any]', state)
```

**Source verified**: `/usr/local/lib/python3.12/site-packages/pydantic_ai/ui/ag_ui/__init__.py` line 74-83

When the agent runs, the adapter attempts to inject this state into the agent's `deps`:

```python
def run_stream_native(self, ...):
    if isinstance(deps, StateHandler):
        raw_state = self.state or {}
        deps.state = raw_state  # ← injected here
    elif self.state:
        warnings.warn(
            "State was provided but `deps` of type `NoneType` "
            "does not implement the `StateHandler` protocol..."
        )
```

**Source verified**: `/usr/local/lib/python3.12/site-packages/pydantic_ai/ui/_adapter.py` line 155-168

---

## Critical Insight: `defaultApplyEvents` Overwrites `agent.state`

AG-UI's `defaultApplyEvents` function (used by `runAgent` when no custom apply logic is provided) **automatically overwrites `agent.state`** when `STATE_SNAPSHOT` or `STATE_DELTA` events arrive from the SSE stream:

```typescript
// From @ag-ui/client/src/apply/default.ts (extracted from source map)
case EventType.STATE_SNAPSHOT: {
  // ... subscriber callbacks ...
  applyMutation(mutation);

  if (mutation.stopPropagation !== true) {
    const { snapshot } = event as StateSnapshotEvent;
    state = snapshot;           // ← overwrites local state variable
    applyMutation({ state });   // ← writes to agent.state
  }
}

case EventType.STATE_DELTA: {
  // ... subscriber callbacks ...
  applyMutation(mutation);

  if (mutation.stopPropagation !== true) {
    const { delta } = event as StateDeltaEvent;
    const result = jsonpatch.applyPatch(state, delta, true, false);
    state = result.newDocument;  // ← overwrites local state variable
    applyMutation({ state });    // ← writes to agent.state
  }
}
```

**Source verified**: `frontend/kitchen/node_modules/@ag-ui/client/dist/index.mjs.map` → `../src/apply/default.ts`

### The Problem

When the agent returns a `STATE_SNAPSHOT` (e.g., from `scale_recipe` returning a `recipe.scaling` widget state), `defaultApplyEvents` replaces `chefAgent.state` with that widget payload. On the next `sendMessage` call, `chefAgent.state` no longer contains `KitchenState` — it contains the widget's JSON. The `sendMessage` function then reconstructs a fallback `KitchenState` from `_agentState`, which loses `selected_recipe` context and defaults to `view: "empty"`.

### The Fix

Return `{ stopPropagation: true }` from subscriber handlers to prevent `defaultApplyEvents` from mutating `agent.state`:

```typescript
const subscriber: AgentSubscriber = {
  onStateSnapshotEvent({ event }: { event: StateSnapshotEvent }) {
    setAgentState(event.snapshot);
    _setSharedAgentState(event.snapshot);
    return { stopPropagation: true };  // ← prevents agent.state overwrite
  },
  onStateDeltaEvent({ event }: { event: StateDeltaEvent }) {
    setAgentState((prev) => applyPatch(prev, event.delta));
    _patchSharedAgentState((prev) => applyPatch(prev, event.delta));
    return { stopPropagation: true };  // ← prevents agent.state overwrite
  },
};
```

**Source verified**: `frontend/kitchen/src/hooks/useAgent.ts` lines 321-354

---

## Dual-State Architecture

Voice Chef maintains **two separate state stores** with different purposes:

| Store | Purpose | Mutated By | Read By |
|---|---|---|---|
| `chefAgent.state` | `KitchenState` sent to agent in `RunAgentInput` | Explicit `chefAgent.setState()` calls from components | `sendMessage()` (serialized into request body) |
| `_agentState` (module-level) | Widget state from agent (`recipe.scaling`, etc.) | `STATE_SNAPSHOT` / `STATE_DELTA` events | `useAgentState()` hook (consumed by `RecipeDetailCard`, etc.) |

### Why Two Stores?

- **`chefAgent.state`** must remain a stable `KitchenState` so the agent always receives the correct navigation context (`view`, `selected_recipe`, `scaling`).
- **`_agentState`** must receive agent-emitted widget data so components can render scaling editors, notifications, etc.

Without `stopPropagation: true`, these two concerns collide: agent widget data corrupts the `KitchenState`, causing the agent to lose context on subsequent runs.

### Data Flow

```
Component (RecipeListView, RecipeDetailCard)
    │
    ▼
chefAgent.setState(kitchenState)  ← preserves KitchenState
    │
    ▼
sendMessage() reads chefAgent.state → sends in RunAgentInput
    │
    ▼
Agent receives KitchenState → makes decisions
    │
    ▼
Agent emits STATE_SNAPSHOT (widget data)
    │
    ▼
Subscriber: setAgentState(snapshot) + _setSharedAgentState(snapshot)
    │
    ▼
Components read widget state via useAgentState()
    │
    ▼
Components update chefAgent.setState(newKitchenState) if needed
```

**Source verified**: `frontend/kitchen/src/hooks/useAgent.ts`

---

## How to Enable State Reception

### Step 1: Define a state model

```python
from pydantic import BaseModel
from typing import Any

class SelectedRecipe(BaseModel):
    id: str
    name: str
    portions: float | None
    yield_mode: str

class ScalingContext(BaseModel):
    target_portions: float | None
    is_dirty: bool

class LastAction(BaseModel):
    type: str
    timestamp: int

class KitchenState(BaseModel):
    view: str = "empty"  # "empty" | "recipe_list" | "recipe_detail" | "scaling"
    selected_recipe: SelectedRecipe | None = None
    scaling: ScalingContext | None = None
    last_action: LastAction | None = None
```

**Source verified**: `agent/app/state.py`

### Step 2: Use `StateDeps` as the deps type

```python
from pydantic_ai import Agent
from pydantic_ai.ui import StateDeps

agent = Agent(
    model,
    system_prompt="...",
    deps_type=StateDeps[KitchenState],  # ← enables state reception
)
```

**Source verified**: `agent/app/agent.py` line 113-117

### Step 3: Inject state into the LLM prompt

Use `@agent.instructions` to make state visible to the LLM:

```python
@agent.instructions
def state_instructions(ctx: RunContext[StateDeps[KitchenState]]) -> str:
    state = ctx.deps.state
    lines = ["CURRENT STATE:"]
    if state.selected_recipe:
        lines.append(f'- Selected recipe: "{state.selected_recipe.name}" (id: {state.selected_recipe.id})')
    else:
        lines.append("- No recipe selected")
    return "\n".join(lines)
```

**Source verified**: `agent/app/agent.py` lines 120-151

`@agent.instructions` is called fresh on every LLM request. It reads `ctx.deps.state` (populated by `AGUIAdapter` from the request body) and returns a text block that the LLM can read as context.

### Step 4: Access state in tools

```python
from pydantic_ai import RunContext

@agent.tool
async def scale_recipe(
    ctx: RunContext[StateDeps[KitchenState]],
    recipe_id: str = "",
    target_portions: float = 0,
) -> dict:
    state = ctx.deps.state
    if not recipe_id and state.selected_recipe:
        recipe_id = state.selected_recipe.id
    # ... fetch recipe, compute scaling ...
```

**Source verified**: `agent/app/agent.py` lines 221-265, 376-476

### Step 5: Frontend sends state on every run

```typescript
function sendMessage(text: string) {
  // Capture KitchenState BEFORE runAgent
  const kitchenState: KitchenState = {
    view: agentState?.view ?? "empty",
    selected_recipe: agentState?.selected_recipe ?? null,
    scaling: agentState?.scaling ?? null,
    last_action: { type: "search", timestamp: Date.now() },
  };

  // Set state synchronously before runAgent so it's in the request body
  chefAgent.setState(kitchenState);

  // runAgent() serializes chefAgent.state into RunAgentInput.state
  chefAgent.runAgent({ runId: uuid() }, subscriber);
}
```

**Source verified**: `frontend/kitchen/src/hooks/useAgent.ts` lines 262-300, 456-459

---

## How State Delta Events Work (Agent → Frontend)

When tools return `StateDeltaEvent` or `StateSnapshotEvent`, pydantic-ai emits them through the SSE stream:

```python
# From _event_stream.py line 192-196
if isinstance(result, ToolReturnPart):
    possible_event = result.metadata or result.content
    if isinstance(possible_event, BaseEvent):
        yield possible_event  # ← streamed to frontend
```

The frontend's `useAgent` subscriber processes these **without** allowing `defaultApplyEvents` to mutate `agent.state`:

```typescript
onStateSnapshotEvent({ event }) {
  setAgentState(event.snapshot);        // ← React local state
  _setSharedAgentState(event.snapshot); // ← module-level shared store
  return { stopPropagation: true };     // ← protects chefAgent.state
},
onStateDeltaEvent({ event }) {
  _patchSharedAgentState((prev) => applyPatch(prev, event.delta));
  return { stopPropagation: true };     // ← protects chefAgent.state
},
```

**Source verified**: `frontend/kitchen/src/hooks/useAgent.ts` lines 321-354

This creates the loop:
1. Frontend sets `KitchenState` on `chefAgent.state` → sends in `RunAgentInput`
2. Agent reads state via `ctx.deps.state` → makes decisions
3. Agent updates widget state → emits `STATE_SNAPSHOT` / `STATE_DELTA`
4. Frontend receives delta → updates `_agentState` (shared store) → components re-render
5. Components update `chefAgent.setState(newKitchenState)` if navigation changes

---

## State Field Design for Voice Chef

Current `KitchenState` shape:

```typescript
// frontend/kitchen/src/types/agent-state.ts
interface KitchenState {
  view: "empty" | "recipe_list" | "recipe_detail" | "scaling";
  selected_recipe: {
    id: string;
    name: string;
    portions: number | null;
    yield_mode: string;
  } | null;
  scaling: {
    target_portions: number | null;
    is_dirty: boolean;
  } | null;
  last_action: {
    type: "search" | "select" | "scale" | "apply" | "browse" | "clear";
    timestamp: number;
  } | null;
}
```

Python equivalent:

```python
# agent/app/state.py
class KitchenState(BaseModel):
    view: str = "empty"
    selected_recipe: SelectedRecipe | None = None
    scaling: ScalingContext | None = None
    last_action: LastAction | None = None
```

### Why this matters for voice

With this state, the agent can handle ambiguous commands:

```
Chef: "Scale this to 20 portions"
Agent reads state:
  state.selected_recipe.id = "bd3083..."
  state.selected_recipe.name = "CW Chimichurri"
  state.view = "recipe_detail"

→ Agent knows exactly which recipe without searching.
→ Calls scale_recipe(state.selected_recipe.id, 20)
```

Without state:
```
Chef: "Scale this to 20 portions"
Agent has no context → must ask "which recipe?" or search history
```

---

## Implementation Status

| Component | State Support | Status |
|---|---|---|
| Frontend `HttpAgent` | Has `.setState()` and `.state` | ✅ Implemented |
| `useAgent()` hook | Calls `chefAgent.setState()` before `runAgent()` with `stopPropagation` protection | ✅ Implemented |
| `AgentSlotProvider` | Tracks slot state; components call `chefAgent.setState()` on mount | ✅ Implemented |
| Agent `agent.py` | `deps_type=StateDeps[KitchenState]` with `@agent.instructions` | ✅ Implemented |
| Agent tools | Use `@agent.tool` with `RunContext[StateDeps[KitchenState]]` | ✅ Implemented |
| Python `KitchenState` | Defined in `agent/app/state.py` | ✅ Implemented |
| TypeScript `KitchenState` | Defined in `frontend/kitchen/src/types/agent-state.ts` | ✅ Implemented |

---

## References

- AG-UI State Management: https://docs.ag-ui.com/concepts/state
- AG-UI Architecture: https://docs.ag-ui.com/concepts/architecture
- pydantic-ai `StateDeps`: `pydantic_ai.ui.StateDeps`
- pydantic-ai `StateHandler`: `pydantic_ai.ui.StateHandler`
- pydantic-ai `@agent.instructions`: https://ai.pydantic.dev/ag-ui
- `RunAgentInput` schema: `@ag-ui/core` zod schema line 2264
- `@ag-ui/client` `defaultApplyEvents`: `frontend/kitchen/node_modules/@ag-ui/client/dist/index.mjs.map` → `../src/apply/default.ts`
