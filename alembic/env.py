# Конфигурация alembic для миграций базы данных.

from alembic import context
from sqlalchemy import engine_from_config, pool
from logging.config import fileConfig

# Объект конфигурации alembic
config = context.config

# Настройка логирования из файла конфигурации
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Подключение метаданных моделей для автоматической генерации миграций
from app.core.db import Base
from app.models import CharityProject, Donation  # noqa

target_metadata = Base.metadata


def run_migrations_offline():
    """Выполнить миграции в офлайн-режиме (без подключения к БД)."""
    database_url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=database_url,
        target_metadata=target_metadata,
        literal_binds=True,
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online():
    """Выполнить миграции в онлайн-режиме (с подключением к БД)."""
    connectable = engine_from_config(
        config.get_section(config.config_ini_section),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
