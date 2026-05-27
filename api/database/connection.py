from sqlalchemy import text
from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from contextlib import asynccontextmanager

from core.config import settings

# A URL deve usar o driver oracledb_async
# O formato de settings.ORACLE_DSN é host:porta/service_name
DATABASE_URL = f"oracle+oracledb_async://{settings.ORACLE_USER}:{settings.ORACLE_APP_PASSWORD}@{settings.ORACLE_DSN}"

engine = create_async_engine(
    DATABASE_URL,
    pool_size=settings.ORACLE_POOL_MIN,
    max_overflow=settings.ORACLE_POOL_MAX - settings.ORACLE_POOL_MIN,
    pool_pre_ping=True,
    echo=False,
)

AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


async def init_pool() -> None:
    """Valida a conexão com o banco no startup."""
    async with engine.connect() as conn:
        await conn.execute(text("SELECT 1 FROM DUAL"))


async def close_pool() -> None:
    """Fecha o pool de conexões no shutdown."""
    await engine.dispose()


@asynccontextmanager
async def get_session() -> AsyncGenerator[AsyncSession, None]:
    """
    Context manager assíncrono para sessões do SQLAlchemy.
    Faz commit automático em caso de sucesso e rollback em caso de erro.
    """
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()
