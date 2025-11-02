"""
Database Configuration and Connection Management
PostgreSQL setup with async connection pooling for CropGPT
"""

import asyncpg
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
import redis.asyncio as redis
from typing import AsyncGenerator

from app.core.config import settings


# SQLAlchemy Base
Base = declarative_base()

# Async database engine for FastAPI
async_engine = create_async_engine(
    settings.DATABASE_URL.replace("postgresql://", "postgresql+asyncpg://"),
    pool_size=settings.DATABASE_POOL_SIZE,
    max_overflow=settings.DATABASE_MAX_OVERFLOW,
    echo=settings.DEBUG,
    future=True
)

# Async session factory
AsyncSessionLocal = async_sessionmaker(
    bind=async_engine,
    class_=AsyncSession,
    expire_on_commit=False
)

# Sync engine for migrations (fallback)
sync_engine = create_engine(
    settings.DATABASE_URL,
    echo=settings.DEBUG
)

# Redis connection
redis_client: redis.Redis = None


async def get_async_db() -> AsyncGenerator[AsyncSession, None]:
    """Get async database session"""
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()


async def get_redis() -> redis.Redis:
    """Get Redis client connection"""
    global redis_client
    if redis_client is None:
        redis_client = redis.from_url(
            settings.REDIS_URL,
            encoding="utf-8",
            decode_responses=True
        )
    return redis_client


async def init_db():
    """Initialize database tables and Redis connection"""
    try:
        # Create tables
        async with async_engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        print("✅ Database tables created successfully")

        # Initialize Redis connection
        await get_redis()
        await redis_client.ping()
        print("✅ Redis connection established")

    except Exception as e:
        print(f"❌ Database initialization failed: {e}")
        raise


async def close_db():
    """Close database connections"""
    await async_engine.dispose()
    if redis_client:
        await redis_client.close()


class DatabaseManager:
    """Database utility class for common operations"""

    @staticmethod
    async def execute_raw_query(query: str, params: dict = None) -> list:
        """Execute raw SQL query"""
        async with async_engine.begin() as conn:
            result = await conn.execute(query, params or {})
            return result.fetchall()

    @staticmethod
    async def check_connection() -> bool:
        """Check database connection health"""
        try:
            async with async_engine.begin() as conn:
                await conn.execute("SELECT 1")
            return True
        except Exception:
            return False


# Cache utilities
class CacheManager:
    """Redis cache management utilities"""

    def __init__(self, redis_client: redis.Redis):
        self.redis = redis_client

    async def get(self, key: str) -> str:
        """Get cached value"""
        return await self.redis.get(key)

    async def set(self, key: str, value: str, ttl: int = None) -> bool:
        """Set cached value with TTL"""
        return await self.redis.setex(key, ttl or settings.REDIS_CACHE_TTL, value)

    async def delete(self, key: str) -> bool:
        """Delete cached value"""
        return await self.redis.delete(key) > 0

    async def exists(self, key: str) -> bool:
        """Check if key exists in cache"""
        return await self.redis.exists(key) > 0

    async def get_json(self, key: str) -> dict:
        """Get JSON value from cache"""
        import json
        value = await self.get(key)
        return json.loads(value) if value else None

    async def set_json(self, key: str, value: dict, ttl: int = None) -> bool:
        """Set JSON value in cache"""
        import json
        json_value = json.dumps(value)
        return await self.set(key, json_value, ttl)