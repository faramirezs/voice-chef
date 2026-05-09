import os
import pytest
from sqlalchemy import create_engine
from sqlalchemy.pool import NullPool
from alembic.config import Config


# DATABASE_URL must be set (from .env or environment)
TEST_DB_URL = os.environ.get("DATABASE_URL")
if not TEST_DB_URL:
    raise RuntimeError(
        "DATABASE_URL environment variable is not set. "
        "Please set it before running tests (e.g., from .env file)."
    )


@pytest.fixture(scope="session")
def db_engine():
    """
    Session-scoped engine — reused across all tests in a CI run.
    NullPool prevents connection leaks between test processes.
    """
    engine = create_engine(TEST_DB_URL, poolclass=NullPool)
    yield engine
    engine.dispose()


# ── pytest-alembic required fixtures ────────────────────────────────────────

@pytest.fixture(scope="session")
def alembic_config():
    """
    pytest-alembic reads this to find alembic.ini and run migrations.
    Override sqlalchemy.url so the test DB is used, not production.
    """
    cfg = Config("alembic.ini")
    cfg.set_main_option("sqlalchemy.url", TEST_DB_URL)
    return cfg


@pytest.fixture(scope="session")
def alembic_engine(alembic_config):
    """
    pytest-alembic uses this engine to apply migrations during tests.
    Must match the URL in alembic_config.
    """
    return create_engine(
        alembic_config.get_main_option("sqlalchemy.url"),
        poolclass=NullPool,
    )