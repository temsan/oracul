"""
Подключение к базе данных
"""

import logging
from contextlib import asynccontextmanager
from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import (
    AsyncSession,
    create_async_engine,
    async_sessionmaker
)
from sqlalchemy.pool import NullPool

try:
    import redis.asyncio as redis
    HAS_REDIS = True
except ImportError:
    HAS_REDIS = False

from config.settings import settings
from models.database import Base

logger = logging.getLogger(__name__)

# Создание асинхронного движка (только если settings доступны)
engine = None
AsyncSessionLocal = None
redis_client = None

if settings:
    db_url = settings.DATABASE_URL
    # Поддержка PostgreSQL и SQLite
    if db_url.startswith("postgresql://"):
        db_url = db_url.replace("postgresql://", "postgresql+asyncpg://")

    engine = create_async_engine(
        db_url,
        echo=settings.DEBUG,
        poolclass=NullPool if settings.DEBUG else None,
        pool_pre_ping=True,
    )

    AsyncSessionLocal = async_sessionmaker(
        engine,
        class_=AsyncSession,
        expire_on_commit=False
    )


async def init_database():
    """Инициализация базы данных"""
    global redis_client

    if engine is None:
        logger.warning("БД не настроена — settings отсутствуют")
        return

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    if HAS_REDIS and settings:
        try:
            redis_client = redis.from_url(settings.REDIS_URL)
            logger.info("Redis подключен")
        except Exception as e:
            logger.warning(f"Redis недоступен: {e}")

    logger.info("БД инициализирована")


async def close_database():
    """Закрытие подключений"""
    global redis_client

    if engine:
        await engine.dispose()

    if redis_client:
        await redis_client.close()

    logger.info("Подключения к БД закрыты")


@asynccontextmanager
async def get_db_session() -> AsyncGenerator[AsyncSession, None]:
    """Контекстный менеджер для работы с БД"""
    if AsyncSessionLocal is None:
        raise RuntimeError("БД не инициализирована")

    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


async def get_redis():
    """Получение Redis клиента (может быть None)"""
    global redis_client
    if redis_client is None and HAS_REDIS and settings:
        try:
            redis_client = redis.from_url(settings.REDIS_URL)
        except Exception:
            pass
    return redis_client


# Алиас для совместимости
get_session = get_db_session


class CacheManager:
    """Менеджер кеша (работает если Redis доступен)"""

    @staticmethod
    async def get(key: str):
        redis_conn = await get_redis()
        if redis_conn:
            return await redis_conn.get(key)
        return None

    @staticmethod
    async def set(key: str, value: str, expire: int = 3600) -> bool:
        redis_conn = await get_redis()
        if redis_conn:
            return await redis_conn.set(key, value, ex=expire)
        return False

    @staticmethod
    async def delete(key: str) -> bool:
        redis_conn = await get_redis()
        if redis_conn:
            return await redis_conn.delete(key)
        return False

    @staticmethod
    async def exists(key: str) -> bool:
        redis_conn = await get_redis()
        if redis_conn:
            return await redis_conn.exists(key)
        return False


cache = CacheManager()
