from core.config import settings
from core.logging import logger
import asyncio
from sqlalchemy.ext.asyncio import async_scoped_session
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy_utils.functions import create_database, database_exists, drop_database





# Check if we're in testing mode
if settings.testing:
    DATABASE_URL = f"postgresql+asyncpg://{settings.postgres_test_user}:{settings.postgres_test_password}@{settings.postgres_test_server}:{settings.postgres_port}/{settings.postgres_test_db}"
    logger.info(f"Testing mode: {DATABASE_URL}")

else:
    DATABASE_URL = f"postgresql+asyncpg://{settings.postgres_user}:{settings.postgres_password}@{settings.postgres_server}:{settings.postgres_port}/{settings.postgres_db}"
    logger.info(f"Production mode: {DATABASE_URL}")

engine = create_async_engine(DATABASE_URL, 
                                echo=False,
                                pool_pre_ping=True,
                                pool_recycle=300
                            )

# AsyncSessionLocal = sessionmaker(bind=engine,
#                                     class_=AsyncSession,
#                                     expire_on_commit=False,
#                                     autoflush=False
#                                 )
async_session_factory = sessionmaker(bind=engine, 
                                    expire_on_commit=False, 
                                    class_=AsyncSession
                                    )

AsyncSessionLocal = async_scoped_session(async_session_factory, scopefunc=asyncio.current_task)

async def init_test_db():
    """Initialize test database: Drop if exists and then create anew."""
    if database_exists(DATABASE_URL):
        logger.info(f"Dropping existing test database: {DATABASE_URL}")
        drop_database(DATABASE_URL)
    logger.info(f"Creating test database: {DATABASE_URL}")
    create_database(DATABASE_URL)


async def get_db():
    session = AsyncSessionLocal()
    try:
        yield session
    finally:
        await session.close()
