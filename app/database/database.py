from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.ext.asyncio.engine import AsyncEngine
from sqlalchemy.orm import sessionmaker, DeclarativeBase
from app.config.config import Config
from app.constants.constants import DataBaseConstants
from typing import AsyncGenerator


class Base(DeclarativeBase):
    pass


# async engine creation
engine: AsyncEngine = create_async_engine(
    url=Config().DATABASE_URL,
    echo=DataBaseConstants.ECHO,
    future=DataBaseConstants.FUTURE,
    pool_size=DataBaseConstants.POOL_SIZE,
    max_overflow=DataBaseConstants.MAX_OVERFLOW,
    pool_timeout=DataBaseConstants.POOL_TIMEOUT,
    pool_recycle=DataBaseConstants.POOL_RECYCLE,
    pool_pre_ping=DataBaseConstants.POOL_PRE_PING,
)

# sessionmaker configuration
AsyncSessionLocal: sessionmaker = sessionmaker(
    bind=engine, class_=AsyncSession, expire_on_commit=False
)


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """
    Dependency function to get a database session.

    :rtype: AsyncGenerator[AsyncSession, None]
    :returns: AsyncGenerator yielding an AsyncSession
    """
    async with AsyncSessionLocal() as session:
        try:
            yield session
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()
