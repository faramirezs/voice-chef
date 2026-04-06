"""
test_schema_drift.py

Three complementary drift detection strategies:
  1. pytest-alembic built-in suite     — migration chain integrity
  2. compare_metadata programmatic     — live model vs DB diff
  3. SQLAlchemy inspect()              — surgical column/index/constraint audit
"""
import re
import importlib.util
from pathlib import Path
from typing import Any

import pytest
from alembic.autogenerate import compare_metadata
from alembic.runtime.migration import MigrationContext
from sqlalchemy import inspect, text
from sqlmodel import SQLModel

def _load_models_module() -> None:
    """Load models.py directly so package __init__ imports do not pollute metadata."""
    repo_root = Path(__file__).resolve().parents[2]
    candidates = [
        repo_root / "fastapi" / "app" / "models" / "models.py",
        Path("/code/app/models/models.py"),
    ]

    for models_path in candidates:
        if models_path.exists():
            spec = importlib.util.spec_from_file_location("_test_drift_models", str(models_path))
            if spec is None or spec.loader is None:
                continue
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            return

    raise ModuleNotFoundError("Could not locate models.py for drift test metadata loading")


_load_models_module()

MANAGED_TABLES = {"users", "tenants", "recipes"}
_PG_CAST_RE = re.compile(r"::[a-z _]+", re.IGNORECASE)


def _normalize(raw: str | None) -> str:
    if not raw:
        return ""
    return _PG_CAST_RE.sub("", raw).strip("'\" ").lower()


def _compare_server_default(
    context: Any, inspected_column: Any, metadata_column: Any,
    inspected_default: str | None, metadata_default: Any,
    rendered_metadata_default: str | None,
) -> bool | None:
    a = _normalize(inspected_default)
    b = _normalize(rendered_metadata_default)
    if not a and not b:
        return False
    if bool(a) != bool(b):
        return True
    return False if a == b else None


# ── 1. pytest-alembic built-in tests ────────────────────────────────────────
# These four tests are automatically collected by pytest-alembic when
# alembic_config and alembic_engine fixtures are present in conftest.py.
# They are not written here — they come from the library itself:
#
#   test_single_head_revision     → no branched migration chain
#   test_upgrade                  → every upgrade() runs without error
#   test_model_definitions_match_ddl → models == DB after upgrade head
#   test_up_down_consistency      → downgrade() doesn't corrupt the chain


# ── 2. Programmatic compare_metadata ────────────────────────────────────────
class TestCompareMeta:
    """
    Runs compare_metadata with our custom server_default normaliser.
    Fails the test with a detailed diff if any drift is found.
    """

    def test_no_schema_drift(self, db_engine):
        with db_engine.connect() as conn:
            ctx = MigrationContext.configure(
                conn,
                opts={
                    "compare_type": True,
                    "compare_server_default": _compare_server_default,
                    "include_object": lambda obj, name, type_, reflected, compare_to: (
                        name in MANAGED_TABLES if type_ == "table" else True
                    ),
                    "user_module_prefix": "sqlmodel.sql.sqltypes.",
                },
            )
            diffs = compare_metadata(ctx, SQLModel.metadata)

        assert not diffs, (
            f"{len(diffs)} schema difference(s) detected between models and DB:\n"
            + "\n".join(f"  • {d}" for d in diffs)
        )


# ── 3. Surgical inspect() audit ─────────────────────────────────────────────
class TestInspect:
    """
    Column-by-column, index-by-index, constraint-by-constraint verification.
    More transparent than compare_metadata — each assertion is independent,
    so failures pinpoint exactly which column or index is wrong.
    """

    @pytest.fixture(autouse=True)
    def _setup(self, db_engine):
        self.inspector = inspect(db_engine)
        self.db_tables  = set(self.inspector.get_table_names())

    # ── Tables ────────────────────────────────────────────────────────────
    @pytest.mark.parametrize("table_name", sorted(MANAGED_TABLES))
    def test_table_exists(self, table_name):
        assert table_name in self.db_tables, f"Table '{table_name}' not found in DB"

    # ── Columns ───────────────────────────────────────────────────────────
    @pytest.mark.parametrize("table_name", sorted(MANAGED_TABLES))
    def test_columns_present(self, table_name):
        if table_name not in self.db_tables:
            pytest.skip(f"Table {table_name} missing — caught by test_table_exists")

        db_col_names = {
            c["name"] for c in self.inspector.get_columns(table_name)
        }
        model_col_names = {
            col.name
            for col in SQLModel.metadata.tables[table_name].columns
        }
        missing = model_col_names - db_col_names
        assert not missing, (
            f"Columns missing from '{table_name}' in DB: {missing}"
        )

    @pytest.mark.parametrize("table_name", sorted(MANAGED_TABLES))
    def test_nullable_matches(self, table_name):
        if table_name not in self.db_tables:
            pytest.skip()

        db_cols = {
            c["name"]: c for c in self.inspector.get_columns(table_name)
        }
        errors = []
        for col in SQLModel.metadata.tables[table_name].columns:
            if col.name not in db_cols:
                continue
            db_nullable    = db_cols[col.name]["nullable"]
            model_nullable = col.nullable
            if db_nullable != model_nullable:
                errors.append(
                    f"  {col.name}: model={model_nullable}, db={db_nullable}"
                )
        assert not errors, (
            f"Nullable mismatch in '{table_name}':\n" + "\n".join(errors)
        )

    # ── Indexes ───────────────────────────────────────────────────────────
    @pytest.mark.parametrize("table_name", sorted(MANAGED_TABLES))
    def test_indexes_present(self, table_name):
        if table_name not in self.db_tables:
            pytest.skip()

        db_idx    = {i["name"] for i in self.inspector.get_indexes(table_name)}
        model_idx = {
            i.name
            for i in SQLModel.metadata.tables[table_name].indexes
            if i.name
        }
        missing = model_idx - db_idx
        assert not missing, (
            f"Indexes missing from '{table_name}' in DB: {missing}"
        )

    # ── Unique constraints ────────────────────────────────────────────────
    @pytest.mark.parametrize("table_name", sorted(MANAGED_TABLES))
    def test_unique_constraints_present(self, table_name):
        if table_name not in self.db_tables:
            pytest.skip()

        db_uq = {
            uc["name"]
            for uc in self.inspector.get_unique_constraints(table_name)
            if uc["name"]
        }
        model_uq = {
            c.name
            for c in SQLModel.metadata.tables[table_name].constraints
            if c.name and "unique" in type(c).__name__.lower()
        }
        missing = model_uq - db_uq
        assert not missing, (
            f"Unique constraints missing from '{table_name}' in DB: {missing}"
        )

    # ── PostgreSQL extensions ─────────────────────────────────────────────
    def test_pgcrypto_installed(self, db_engine):
        """gen_random_uuid() requires pgcrypto — fail fast if missing."""
        with db_engine.connect() as conn:
            result = conn.execute(
                text("SELECT extname FROM pg_extension WHERE extname = 'pgcrypto'")
            )
            assert result.fetchone(), (
                "pgcrypto extension not installed. "
                "Run: CREATE EXTENSION IF NOT EXISTS pgcrypto;"
            )