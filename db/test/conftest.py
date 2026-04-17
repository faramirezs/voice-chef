import os
import pytest
from sqlalchemy import create_engine
from sqlalchemy.pool import NullPool
from alembic.config import Config


TEST_DB_URL = os.environ.get(
    "DATABASE_URL",
    "postgresql+psycopg://recipe_user:recipe_pass123@localhost:5432/recipe_db",
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