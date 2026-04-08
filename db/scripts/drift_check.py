"""
drift_check.py

Programmatic schema drift detector using Alembic's compare_metadata API.
Call at app startup or from CI to block deployment on schema drift.
"""
import re
import sys
import importlib.util
import argparse
from pathlib import Path
from typing import Any

from alembic.autogenerate import compare_metadata
from alembic.runtime.migration import MigrationContext
from sqlalchemy import create_engine, text

MANAGED_TABLES = {"users", "tenants", "recipes"}


def _split_selector_values(raw_values: list[str] | None) -> list[str]:
    if not raw_values:
        return []

    values: list[str] = []
    for raw in raw_values:
        for item in raw.split(","):
            token = item.strip()
            if token:
                values.append(token)
    return values


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Schema drift check with optional class/table scope selectors")
    parser.add_argument(
        "--table",
        action="append",
        default=[],
        help="Table selector(s). Accepts repeated flags or comma-separated names.",
    )
    parser.add_argument(
        "--class",
        dest="classes",
        action="append",
        default=[],
        help="Class selector(s). Accepts repeated flags or comma-separated class names.",
    )
    return parser.parse_args()


def _resolve_scope(table_selectors: list[str] | None = None, class_selectors: list[str] | None = None) -> set[str]:
    table_tokens = _split_selector_values(table_selectors)
    class_tokens = _split_selector_values(class_selectors)

    if not table_tokens and not class_tokens:
        return set(MANAGED_TABLES)

    selected_tables: set[str] = set()
    selected_tables.update(table_tokens)

    class_to_table = {
        cls.__name__: cls.__table__.name
        for cls in SQLModel.__subclasses__()
        if getattr(cls, "__table__", None) is not None
    }

    missing_classes = [name for name in class_tokens if name not in class_to_table]
    if missing_classes:
        known = ", ".join(sorted(class_to_table.keys()))
        unknown = ", ".join(sorted(missing_classes))
        raise ValueError(f"Unknown class selector(s): {unknown}. Known classes: {known}")

    selected_tables.update(class_to_table[name] for name in class_tokens)
    return selected_tables


def _load_models_module() -> None:
    """Load split *_models.py modules first, then fallback to models.py."""
    repo_root = Path(__file__).resolve().parents[2]

    # Ensure 'app.*' imports inside split model wrappers resolve when called from repo root.
    for package_root in (repo_root / "fastapi", Path("/code")):
        root_str = str(package_root)
        if package_root.exists() and root_str not in sys.path:
            sys.path.insert(0, root_str)

    app_dirs = [
        repo_root / "fastapi" / "app",
        Path("/code/app"),
    ]
    candidates: list[Path] = []

    for app_dir in app_dirs:
        if not app_dir.exists():
            continue
        split_models = sorted(app_dir.glob("*_models.py"))
        if split_models:
            candidates.extend(split_models)
            continue
        fallback = app_dir / "models.py"
        if fallback.exists():
            candidates.append(fallback)

    for models_path in candidates:
        if models_path.exists():
            spec = importlib.util.spec_from_file_location("_drift_models", str(models_path))
            if spec is None or spec.loader is None:
                continue
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
    if candidates:
        return

    raise ModuleNotFoundError("Could not locate split *_models.py or fallback models.py for drift metadata loading")


_load_models_module()

from sqlmodel import SQLModel

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


def assert_no_drift(db_url: str, table_selectors: list[str] | None = None, class_selectors: list[str] | None = None) -> None:
    global MANAGED_TABLES
    MANAGED_TABLES = _resolve_scope(table_selectors=table_selectors, class_selectors=class_selectors)

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
    args = _parse_args()
    url = os.environ.get("DATABASE_URL")
    if not url:
        print("❌  DATABASE_URL environment variable is not set.")
        sys.exit(1)
    try:
        assert_no_drift(url, table_selectors=args.table, class_selectors=args.classes)
    except ValueError as exc:
        print(f"❌  {exc}")
        sys.exit(1)