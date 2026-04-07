import os
from importlib import import_module
from logging.config import fileConfig

from sqlalchemy import engine_from_config
from sqlalchemy import pool
from sqlmodel import SQLModel


from alembic import context

# ---------------------------------------------------------------------------
# Ensure fastapi/ src root is on sys.path so model imports work from both
# local runs (PYTHONPATH=./fastapi) and GitHub Actions (working-directory: db)
# ---------------------------------------------------------------------------
_here = os.path.dirname(os.path.abspath(__file__))          # db/alembic/
_db_root = os.path.dirname(_here)                            # db/
_repo_root = os.path.dirname(_db_root)                       # repo root
_fastapi_root = os.path.join(_repo_root, "fastapi")          # fastapi/

for _p in (_fastapi_root, _db_root, _repo_root):
    if _p not in sys.path:
        sys.path.insert(0, _p)

# ---------------------------------------------------------------------------
# Alembic config
# ---------------------------------------------------------------------------
config = context.config

url = os.getenv("DATABASE_URL") or config.get_main_option("sqlalchemy.url")
config.set_main_option("sqlalchemy.url", url)

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# add your model's MetaData object here
# for 'autogenerate' support
# from myapp import mymodel
# target_metadata = mymodel.Base.metadata
try:
    from fastapi.app.models.user_models import Users, Tenants  # noqa: F401
    from fastapi.app.models.recipe_models import Recipe  # noqa: F401
except ModuleNotFoundError:
    user_models = import_module("app.models.user_models")
    recipe_models = import_module("app.models.recipe_models")
    Users = user_models.Users
    Tenants = user_models.Tenants
    Recipe = recipe_models.Recipe

target_metadata = SQLModel.metadata

# other values from the config, defined by the needs of env.py,
# can be acquired:
# my_important_option = config.get_main_option("my_important_option")
# ... etc.


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode."""
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )
    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Run migrations in 'online' mode."""
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )
    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            compare_type=True,
            user_module_prefix="sqlmodel.sql.sqltypes.",
        )
        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
