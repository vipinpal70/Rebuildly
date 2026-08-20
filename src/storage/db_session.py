import asyncio
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.pool import NullPool
from config.settings import settings
from src.storage.models import Base
from src.utils.logger import logger

_engine = None
_engine_loop = None


def get_engine():
    global _engine, _engine_loop
    try:
        current_loop = asyncio.get_running_loop()
    except RuntimeError:
        current_loop = None

    if _engine is None or _engine_loop != current_loop:
        # Use NullPool for async operations across multiple asyncio.run() calls
        _engine = create_async_engine(settings.DATABASE_URL, echo=False, poolclass=NullPool)
        _engine_loop = current_loop

    return _engine


def AsyncSessionLocal():
    engine = get_engine()
    return async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)()


async def init_db():
    """Initializes PostgreSQL database tables if they do not exist."""
    try:
        async with get_engine().begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        logger.info("PostgreSQL database tables initialized successfully.")
    except Exception as err:
        logger.error(f"Failed to initialize database tables: {err}")
        raise err
