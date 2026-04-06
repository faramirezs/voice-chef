"""Compatibility wrapper for split user/tenant models during phased migration.

Canonical SQLModel definitions currently live in app.models.
This module re-exports user/tenant classes so split-model import paths keep
working without diverging metadata from the migration source of truth.
"""

from app.models import Tenants, Users
