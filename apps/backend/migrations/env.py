from logging.config import fileConfig

from alembic import context

from apso_backend.core.config import get_settings
from apso_backend.db.base import Base
from apso_backend.db import models  # noqa: F401
from apso_backend.db.session import get_database_url

config = context.config

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

target_metadata = Base.metadata


def run_migrations_offline() -> None:
    settings = get_settings()
    url = get_database_url()
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        include_schemas=False,
        compare_type=True,
    )

    with context.begin_transaction():
        context.run_migrations(environment=settings.environment)


def run_migrations_online() -> None:
    from sqlalchemy import create_engine

    settings = get_settings()
    connectable = create_engine(get_database_url(), pool_pre_ping=True)

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            include_schemas=False,
            compare_type=True,
        )

        with context.begin_transaction():
            context.run_migrations(environment=settings.environment)


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()

