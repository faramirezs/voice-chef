"""Compatibility wrapper for split recipe model during phased migration.

Canonical SQLModel definitions currently live in app.models.
This module re-exports recipe classes so split-model import paths keep working
without diverging metadata from the migration source of truth.
"""

from app.models import Recipe, Recipes
