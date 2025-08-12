# === AGGIUNGI QUESTO BLOCCO ===
import os, sys

# Rende importabile il tuo pacchetto "app" quando lanci alembic dalla root progetto
# Se la tua struttura è: /.../authService4Ever/app/...
# e stai eseguendo:     cd /.../authService4Ever && alembic ...
# allora la root è già sul sys.path. Il blocco sotto è una "rete di sicurezza".
ROOT_DIR = os.path.dirname(os.path.dirname(__file__))  # -> .../authService4Ever
if ROOT_DIR not in sys.path:
    sys.path.append(ROOT_DIR)

from app.db_base import Base         # contiene Base = declarative_base()
from app import models          # IMPORTANTE: carica i modelli (User, RefreshToken, ...)
# === FINE BLOCCO AGGIUNTO ===
#TODO: javid da qui in poi già c'era devo chiedere cgpt cosa devo fare con questo
from logging.config import fileConfig

from sqlalchemy import engine_from_config
from sqlalchemy import pool

from alembic import context

# this is the Alembic Config object, which provides
# access to the values within the .ini file in use.
config = context.config

# Interpret the config file for Python logging.
# This line sets up loggers basically.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# add your model's MetaData object here
# for 'autogenerate' support
# from myapp import mymodel
# target_metadata = mymodel.Base.metadata
target_metadata = Base.metadata

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
            connection=connection, target_metadata=target_metadata
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
