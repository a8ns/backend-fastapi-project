from core.logging import logger
import json
import asyncio
from sqlalchemy import inspect, text
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from models import *  # Import all models from models package
from .session import engine
from models.base_model import Base  # Importing Base from db/base_model.py


async def retry_async(func, max_retries=5, initial_delay=1, backoff_factor=2):
    """
    Generic retry function for async operations.
    
    Args:
        func: Async function to retry
        max_retries: Maximum number of retry attempts
        initial_delay: Initial delay in seconds
        backoff_factor: Multiplier for delay between retries
    """
    last_exception = None
    delay = initial_delay
    
    for attempt in range(max_retries):
        try:
            logger.info(f"Attempt {attempt+1}/{max_retries}")
            return await func()
        except Exception as e:
            last_exception = e
            logger.warning(f"Attempt {attempt+1} failed: {str(e)}")
            
            if attempt < max_retries - 1:
                logger.info(f"Retrying in {delay} seconds...")
                await asyncio.sleep(delay)
                delay *= backoff_factor
            else:
                logger.error(f"All {max_retries} attempts failed")
                raise last_exception

async def install_extensions():
    """Install PostgreSQL extensions."""
    async with engine.begin() as conn:
        try:
            # Install pgvector extension
            logger.info("Installing pgvector extension if not exists")
            await conn.execute(text("CREATE EXTENSION IF NOT EXISTS vector"))
            logger.info("Vector extension successfully installed")
        except Exception as e:
            logger.error(f"Error installing extensions: {str(e)}")
            raise

async def create_tables():
    """Function to create database tables."""
    async with engine.begin() as conn:
        def create_if_needed(sync_conn):
            try:
                inspector = inspect(sync_conn)
                existing_tables = inspector.get_table_names()
                missing_tables = [
                    table.name for table in Base.metadata.sorted_tables
                    if table.name not in existing_tables
                ]
                
                if missing_tables:
                    logger.info(f"Creating missing tables: {missing_tables}")
                    Base.metadata.create_all(bind=sync_conn, checkfirst=True)
                else:
                    logger.info("All tables already exist. No action taken.")
            except Exception as e:
                logger.warning(f"Exception during table creation: {e}")
                raise  # We'll let the retry mechanism handle this
                
        await conn.run_sync(create_if_needed)

async def init_db():
    """Initialize database with retry mechanism."""
    try:
        # First install required extensions
        await retry_async(install_extensions)
        
        # Then create tables
        await retry_async(create_tables)
        
    except Exception as e:
        logger.error(f"Database initialization failed: {str(e)}")
        # Decide whether to re-raise based on your application's needs
        raise


async def close_db():
    await engine.dispose()
    logger.info("Database connection closed.")