import contextvars

_auth_headers: contextvars.ContextVar[dict[str, str]] = contextvars.ContextVar(
    "auth_headers", default={}
)

# Tracks notifications already shown in the current request to prevent
# LLM loops where it calls show_notification repeatedly for the same event.
_notification_cache: contextvars.ContextVar[set[str]] = contextvars.ContextVar(
    "notification_cache", default=set()
)


def set_auth_headers(headers: dict[str, str]) -> None:
    _auth_headers.set(headers)


def get_auth_headers() -> dict[str, str]:
    return _auth_headers.get()


def init_notification_cache() -> None:
    """Call once at the start of each request to clear the dedup set."""
    _notification_cache.set(set())


def mark_notification_shown(key: str) -> bool:
    """Record that a notification was shown. Returns True if it was already shown."""
    cache = _notification_cache.get()
    if key in cache:
        return True
    cache.add(key)
    return False
