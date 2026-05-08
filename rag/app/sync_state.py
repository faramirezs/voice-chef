"""Shared state for the rag service's sync/reindex lifecycle.

Single source of truth for "is the index rebuilding right now and how far
along is it." Consumed by:
- /search responses (Light tier — `indexing` boolean)
- /status endpoint (Medium-tier-ready — full progress snapshot)
- /reindex endpoint (sets state on entry, clears on exit)

The light tier exposes only `running`. The full snapshot — items_done,
items_total, elapsed, eta — is computed and exposed via /status so a
future kitchen-frontend banner can poll it without backend changes.
"""
from __future__ import annotations

import time
from dataclasses import dataclass, field


@dataclass
class SyncState:
    running: bool = False
    started_at: float | None = None
    completed_at: float | None = None
    items_done: int = 0
    items_total: int = 0
    last_error: str | None = None
    # Optional human-readable phase ("backfilling recipes", "embedding ingredients").
    phase: str | None = None

    def start(self, phase: str | None = None) -> None:
        self.running = True
        self.started_at = time.time()
        self.completed_at = None
        self.items_done = 0
        self.items_total = 0
        self.last_error = None
        self.phase = phase

    def set_total(self, total: int) -> None:
        self.items_total = total

    def progress(self, done: int) -> None:
        self.items_done = done

    def finish(self, error: str | None = None) -> None:
        self.running = False
        self.completed_at = time.time()
        self.last_error = error

    def snapshot(self) -> dict:
        """Full progress snapshot. Used by /status. Light tier consumers
        only need `indexing`; everything else is for Medium-tier UI."""
        elapsed = (
            (time.time() - self.started_at) if self.started_at else 0.0
        )
        eta: int | None = None
        if (
            self.running
            and self.items_done > 0
            and self.items_total > self.items_done
        ):
            eta = int(
                elapsed
                * (self.items_total - self.items_done)
                / self.items_done
            )
        return {
            "indexing": self.running,
            "phase": self.phase,
            "items_done": self.items_done,
            "items_total": self.items_total,
            "elapsed_seconds": int(elapsed) if elapsed else None,
            "eta_seconds": eta,
            "last_error": self.last_error,
            "completed_at": self.completed_at,
        }


# Module-level singleton — main.py imports this. One state per service
# process; the asyncio lock in sync.py ensures we never have two writers.
state = SyncState()
