import os
import importlib.util
from pathlib import Path
from logging.config import fileConfig

from sqlalchemy import engine_from_config
from sqlalchemy import pool


from alembic import context

# this is the Alembic Config object, which provides
# access to the values within the .ini file in use.
config = context.config

url = os.getenv("DATABASE_URL") or config.get_main_option("sqlalchemy.url")
config.set_main_option("sqlalchemy.url", url)

# Interpret the config file for Python logging.
# This line sets up loggers basically.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# add your model's MetaData object here
# for 'autogenerate' support
# from myapp import mymodel
# target_metadata = mymodel.Base.metadata
def _load_models_module() -> None:
    """Load split *_models.py modules first, then fallback to models.py."""
    repo_root = Path(__file__).resolve().parents[2]
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
            spec = importlib.util.spec_from_file_location(f"_alembic_models_{models_path.stem}", str(models_path))
            if spec is None or spec.loader is None:
                continue
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
    if candidates:
        return

    raise ModuleNotFoundError("Could not locate split *_models.py or fallback models.py for Alembic metadata loading")


_load_models_module()
from sqlmodel import SQLModel

target_metadata = SQLModel.metadata
MODEL_TABLE_NAMES = set(target_metadata.tables.keys())


def include_object(object, name, type_, reflected, compare_to):
    """Limit autogenerate scope to SQLModel-managed tables and related objects."""
    if type_ == "table":
        return name in MODEL_TABLE_NAMES

    if type_ in {"column", "index", "unique_constraint", "foreign_key_constraint", "primary_key_constraint"}:
        table_name = None
        parent = getattr(object, "table", None)
        if parent is not None:
            table_name = getattr(parent, "name", None)
        if table_name is None and compare_to is not None:
            compare_parent = getattr(compare_to, "table", None)
            if compare_parent is not None:
                table_name = getattr(compare_parent, "name", None)
        if table_name is not None:
            return table_name in MODEL_TABLE_NAMES

    return True

# other values from the config, defined by the needs of env.py,
# can be acquired:
# my_important_option = config.get_main_option("my_important_option")
# ... etc.


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode.

    This configures the context with just a URL
    and not an Engine, though an Engine is acceptable
    here as well.  By skipping the Engine creation
    we don't even need a DBAPI to be available.

    Calls to context.execute() here emit the given string to the
    script output.

    """
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        include_object=include_object,
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Run migrations in 'online' mode.

    In this scenario we need to create an Engine
    and associate a connection with the context.

    """
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            include_object=include_object,
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
