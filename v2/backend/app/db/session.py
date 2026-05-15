import socket
from collections.abc import Generator
from urllib.parse import urlparse

from sqlalchemy import create_engine, text
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker

from app.core.config import settings


class Base(DeclarativeBase):
    pass


engine = create_engine(
    settings.database_url,
    pool_pre_ping=True,
    connect_args={"connect_timeout": 3},
) if settings.database_url else None
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False) if engine else None


def get_db() -> Generator[Session, None, None]:
    if SessionLocal is None:
        raise RuntimeError("DATABASE_URL no configurado.")
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def check_database() -> dict:
    if engine is None:
        return {"ok": False, "detail": "DATABASE_URL no configurado."}
    parsed = urlparse(settings.database_url)
    host = parsed.hostname or "127.0.0.1"
    port = parsed.port or 5432
    try:
        with socket.create_connection((host, port), timeout=1):
            pass
    except OSError:
        return {"ok": False, "detail": f"PostgreSQL no escucha en {host}:{port}."}
    try:
        with engine.connect() as connection:
            connection.execute(text("select 1"))
        return {"ok": True, "detail": "PostgreSQL conectado."}
    except Exception as exc:
        return {"ok": False, "detail": str(exc).splitlines()[0]}


def init_database() -> dict:
    if engine is None:
        return {"ok": False, "detail": "DATABASE_URL no configurado."}
    parsed = urlparse(settings.database_url)
    host = parsed.hostname or "127.0.0.1"
    port = parsed.port or 5432
    try:
        with socket.create_connection((host, port), timeout=1):
            pass
    except OSError:
        return {"ok": False, "detail": f"PostgreSQL no escucha en {host}:{port}."}
    try:
        from app.models import crm, identity, tenant  # noqa: F401
        from app.db.migrations import apply_compatibility_migrations

        Base.metadata.create_all(bind=engine)
        apply_compatibility_migrations(engine)
        return {"ok": True, "detail": "Esquema verificado."}
    except Exception as exc:
        return {"ok": False, "detail": str(exc).splitlines()[0]}
