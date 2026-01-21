from logging.config import fileConfig

from sqlalchemy import engine_from_config
from sqlalchemy import pool

from alembic import context
import os
import sys

# 1. Dodajemy ścieżkę do projektu
sys.path.append(os.getcwd())

# 2. Importujemy gotowy URL z Twojego pliku database.py
from database import SQLALCHEMY_DATABASE_URL
from models import Base

config = context.config

# --- WAŻNE: USUNĘLIŚMY LINIĘ config.set_main_option(...) ---
# Ona powodowała błąd z procentami (%).
# Zamiast tego URL przekażemy niżej, bezpośrednio do silnika.

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

target_metadata = Base.metadata

def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode."""
    # Tutaj używamy naszego URL bezpośrednio
    url = SQLALCHEMY_DATABASE_URL
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
    
    # Pobieramy konfigurację z pliku (tam jest ta atrapa sqlite)
    configuration = config.get_section(config.config_ini_section)
    if configuration is None:
        configuration = {}
        
    # --- KLUCZOWA ZMIANA ---
    # Nadpisujemy URL w słowniku konfiguracji w pamięci.
    # Dzięki temu omijamy parser plików .ini i błąd z procentami.
    configuration["sqlalchemy.url"] = SQLALCHEMY_DATABASE_URL

    connectable = engine_from_config(
        configuration,
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