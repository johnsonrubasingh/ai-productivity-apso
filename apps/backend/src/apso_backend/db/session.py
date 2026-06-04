import os
from collections.abc import Generator

from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from apso_backend.core.config import get_settings


def get_database_url() -> str:
    settings = get_settings()
    value = os.getenv(settings.supabase.db_url_env)
    if not value:
        raise RuntimeError(
            f"Database URL environment variable '{settings.supabase.db_url_env}' is not set"
        )
    return value


def create_session_factory() -> sessionmaker[Session]:
    engine = create_engine(get_database_url(), pool_pre_ping=True)
    return sessionmaker(bind=engine, autoflush=False, autocommit=False)


def get_db_session() -> Generator[Session, None, None]:
    factory = create_session_factory()
    session = factory()
    try:
        yield session
    finally:
        session.close()


def get_optional_db_session() -> Generator[Session | None, None, None]:
    try:
        factory = create_session_factory()
    except RuntimeError:
        yield None
        return
    session = factory()
    try:
        yield session
    finally:
        session.close()
