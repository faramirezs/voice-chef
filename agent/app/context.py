import contextvars

_auth_headers: contextvars.ContextVar[dict[str, str]] = contextvars.ContextVar(
    "auth_headers", default={}
)

# Tracks notifications already shown in the current request to prevent
# LLM loops where it calls show_notification repeatedly for the same event.
_notification_cache: contextvars.ContextVar[set[str]] = contextvars.ContextVar(
    "notification_cache", default=set()
)

# True once a canvas-rendering tool has succeeded in the current request.
# Used by show_notification to suppress contradicting "No match" messages
# the LLM sometimes emits in parallel with a successful get_recipe_detail.
_canvas_rendered: contextvars.ContextVar[bool] = contextvars.ContextVar(
    "canvas_rendered", default=False
)

# True once a search tool returned at least one confident hit in the current
# request. Set EARLIER than _canvas_rendered (search runs before
# get_recipe_detail), so it catches the parallel-tool race where the LLM
# emits both get_recipe_detail and a "No recipe found" notification at the
# same time — show_notification finishes first and would otherwise see
# canvas_rendered still False.
_search_succeeded: contextvars.ContextVar[bool] = contextvars.ContextVar(
    "search_succeeded", default=False
)

# True only when a search tool's response in THIS request had
# `indexing: true`. Used to suppress the "Recipe index is rebuilding"
# notification when the LLM emits it from conversation memory but the
# current rag state is fine.
_indexing_observed: contextvars.ContextVar[bool] = contextvars.ContextVar(
    "indexing_observed", default=False
)

# Per-tool counter of rag-search invocations in the current request.
# Capped to prevent the LLM from looping on rephrased queries — each
# search costs a sentence-transformers + BM25 pass on the rag container,
# and 3+ back-to-back searches can spike Docker VM CPU into thermal
# throttling on macOS.
SEARCH_CALL_LIMIT = 2
_search_call_counts: contextvars.ContextVar[dict[str, int]] = contextvars.ContextVar(
    "search_call_counts", default={}
)

# True once a "No …" notification was actually shown to the user in the
# current request (i.e. it passed the suppression gate). If a render
# later succeeds in the same run, get_recipe_detail uses this to also
# emit a ui.clear so the user doesn't see the now-stale notification
# next to the rendered card.
_no_match_notification_shown: contextvars.ContextVar[bool] = contextvars.ContextVar(
    "no_match_notification_shown", default=False
)


def set_auth_headers(headers: dict[str, str]) -> None:
    _auth_headers.set(headers)


def get_auth_headers() -> dict[str, str]:
    return _auth_headers.get()


def init_notification_cache() -> None:
    """Call once at the start of each request to clear the dedup set
    and reset the per-request flags used by show_notification's guards."""
    _notification_cache.set(set())
    _canvas_rendered.set(False)
    _search_succeeded.set(False)
    _indexing_observed.set(False)
    _search_call_counts.set({})
    _no_match_notification_shown.set(False)


def mark_notification_shown(key: str) -> bool:
    """Record that a notification was shown. Returns True if it was already shown."""
    cache = _notification_cache.get()
    if key in cache:
        return True
    cache.add(key)
    return False


def mark_canvas_rendered() -> None:
    _canvas_rendered.set(True)


def was_canvas_rendered() -> bool:
    return _canvas_rendered.get()


def mark_search_succeeded() -> None:
    _search_succeeded.set(True)


def was_search_succeeded() -> bool:
    return _search_succeeded.get()


def mark_indexing_observed() -> None:
    _indexing_observed.set(True)


def was_indexing_observed() -> bool:
    return _indexing_observed.get()


def mark_no_match_notification_shown() -> None:
    _no_match_notification_shown.set(True)


def was_no_match_notification_shown() -> bool:
    return _no_match_notification_shown.get()


def bump_search_call(tool_name: str) -> int:
    """Increment the per-tool search counter for the current request and
    return the new count. Caller compares against SEARCH_CALL_LIMIT to
    decide whether to proceed or return a forced-stop envelope."""
    counts = _search_call_counts.get()
    # Copy-on-write: contextvars share the underlying dict across tasks
    # in the same context, so mutating in place would leak across
    # requests if the default were ever reused.
    counts = dict(counts)
    counts[tool_name] = counts.get(tool_name, 0) + 1
    _search_call_counts.set(counts)
    return counts[tool_name]
