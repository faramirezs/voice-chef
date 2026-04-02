"""
drift_check.py

Programmatic schema drift detector using Alembic's compare_metadata API.
Call at app startup or from CI to block deployment on schema drift.
"""
import re
import sys
from typing import Any

from alembic.autogenerate import compare_metadata
from alembic.runtime.migration import MigrationContext
from sqlalchemy import create_engine, text

# Import ALL models so SQLModel.metadata is fully populated.
# Every model module must be imported here — missing one = false clean pass.
try:
    from fastapi.app.models.user_models import Users, Tenants
    from fastapi.app.models.recipe_models import Recipe
except ModuleNotFoundError:
    from app.models.user_models import Users, Tenants
    from app.models.recipe_models import Recipe

from sqlmodel import SQLModel

MANAGED_TABLES = {"users", "tenants", "recipes"}

_PG_CAST_RE = re.compile(r"::[a-z _]+", re.IGNORECASE)


def _normalize(raw: str | None) -> str:
    if not raw:
        return ""
    return _PG_CAST_RE.sub("", raw).strip("'\" ").lower()


def _compare_server_default(
    context: Any,
    inspected_column: Any,
    metadata_column: Any,
    inspected_default: str | None,
    metadata_default: Any,
    rendered_metadata_default: str | None,
) -> bool | None:
    a = _normalize(inspected_default)
    b = _normalize(rendered_metadata_default)
    if not a and not b:
        return False
    if bool(a) != bool(b):
        return True
    return False if a == b else None


def _include_object(
    obj: Any, name: str, type_: str, reflected: bool, compare_to: Any
) -> bool:
    if type_ == "table":
        return name in MANAGED_TABLES
    return True


def assert_no_drift(db_url: str) -> None:
    engine = create_engine(db_url, echo=False)

    # Fast-fail: verify pgcrypto is installed (needed for gen_random_uuid)
    with engine.connect() as conn:
        result = conn.execute(
            text("SELECT extname FROM pg_extension WHERE extname = 'pgcrypto'")
        )
        if not result.fetchone():
            print("❌  pgcrypto extension not found. Run: CREATE EXTENSION pgcrypto;")
            sys.exit(1)

    with engine.connect() as conn:
        ctx = MigrationContext.configure(
            conn,
            opts={
                "compare_type": True,
                "compare_server_default": _compare_server_default,
                "include_object": _include_object,
                "user_module_prefix": "sqlmodel.sql.sqltypes.",  # SQLModel type rendering
            },
        )
        diffs = compare_metadata(ctx, SQLModel.metadata)

    if not diffs:
        print("✅  No schema drift — models are in sync with the database.")
        return

    print(f"❌  Schema drift detected — {len(diffs)} difference(s):\n")
    for i, diff in enumerate(diffs, 1):
        print(f"  {i}. {diff}")
    sys.exit(1)


if __name__ == "__main__":
    import os
    url = os.environ.get("DATABASE_URL")
    if not url:
        print("❌  DATABASE_URL environment variable is not set.")
        sys.exit(1)
    assert_no_drift(url)