import asyncio
import os
from logging.config import fileConfig

from alembic import context
from sqlalchemy import pool
from sqlalchemy.ext.asyncio import create_async_engine

config = context.config
if config.config_file_name is not None:
    try:
        fileConfig(config.config_file_name, disable_existing_loggers=False)
    except KeyError:
        # Some deployments provide a minimal alembic.ini without formatter/handler sections.
        # Skip logger config in that case so migrations can still run.
        pass

direct_url = os.getenv("DATABASE_URL_DIRECT") or os.getenv("DATABASE_URL")
if direct_url:
    if direct_url.startswith("postgres://"):
        direct_url = direct_url.replace("postgres://", "postgresql+asyncpg://", 1)
    elif direct_url.startswith("postgresql://") and "+asyncpg" not in direct_url:
        direct_url = direct_url.replace("postgresql://", "postgresql+asyncpg://", 1)
    config.set_main_option("sqlalchemy.url", direct_url)


def run_migrations_offline() -> None:
    # TODO: implement
    url = config.get_main_option("sqlalchemy.url")
    context.configure(url=url, target_metadata=None, literal_binds=True, dialect_opts={"paramstyle": "named"})
    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    url = config.get_main_option("sqlalchemy.url")
    connectable = create_async_engine(url, poolclass=pool.NullPool)

    def do_run_migrations(connection) -> None:
        context.configure(connection=connection, target_metadata=None)
        with context.begin_transaction():
            context.run_migrations()

    async def run_async_migrations() -> None:
        async with connectable.connect() as connection:
            await connection.run_sync(do_run_migrations)
        await connectable.dispose()

    asyncio.run(run_async_migrations())


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
