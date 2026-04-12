import os
from logging.config import fileConfig

from sqlalchemy import engine_from_config
from sqlalchemy import pool

from alembic import context

import sys
import os

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../backend"))
sys.path.insert(0, BASE_DIR)


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


###############################################################################

target_metadata = None

###############################################################################
# import backend.app.models  # noqa
# from sqlmodel import SQLModel

# target_metadata = SQLModel.metadata

# ####--- ADD THIS BLOCK FOR FILTERING ---
# def include_object(object, name, type_, reflected, compare_to):
#     """
#     A hook to filter which database objects are included in the 'autogenerate' process.
#     """
#     # We only want to compare the tables we have refactored.
#     # tables_to_check = ["users", "tenants", "recipes", "ingredients", "nutritionfacts"]
#     tables_to_check = {"recipes", "users", "tenants", "ingredients", "recipe_ingredients"}  # <-- Adjust this list to include only the tables you want to check
#     if type_ == "table" and name not in tables_to_check:
#         return False
    
#     # For all other objects (columns, indexes, etc.), let them be compared.
#     # Alembic will automatically ignore them if their parent table is ignored.
#     return True
# # # --- END OF BLOCK ---
##############################################################################



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
##############################################################################
    # url = config.get_main_option("sqlalchemy.url")
    # context.configure(
    #     url=url,
    #     target_metadata=target_metadata,
    #     literal_binds=True,
    #     dialect_opts={"paramstyle": "named"},
    # )
    # with context.begin_transaction():
    #     context.run_migrations()
##############################################################################
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        # include_object=include_object,  # <-- Tell Alembic to use our filter
    )
    with context.begin_transaction():
        context.run_migrations()
##############################################################################



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
##############################################################################
    # with connectable.connect() as connection:
    #     context.configure(
    #         connection=connection, 
    #         target_metadata=target_metadata,
    #     )
    
    #     with context.begin_transaction():
    #         context.run_migrations()
#############################################################################
    with connectable.connect() as connection:
        context.configure(
            connection=connection, 
            target_metadata=target_metadata,
            # include_object=include_object,  # <-- Tell Alembic to use our filter here too
        )

        with context.begin_transaction():
            context.run_migrations()
##############################################################################



if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()