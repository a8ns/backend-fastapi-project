import logging
import json

from sqlalchemy import inspect
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from models import *  # Import all models from models package
from .session import engine
from db.base_model import Base  # Importing Base from db/base_model.py


async def init_db():
    async with engine.begin() as conn:
        def create_if_needed(sync_conn):
            inspector = inspect(sync_conn)
            existing_tables = inspector.get_table_names()

            missing_tables = [
                table.name for table in Base.metadata.sorted_tables
                if table.name not in existing_tables
            ]

            if missing_tables:
                logging.info(f"Creating missing tables: {missing_tables}")
                Base.metadata.create_all(bind=sync_conn)
            else:
                logging.info("All tables already exist. No action taken.")

        await conn.run_sync(create_if_needed)


async def close_db():
    await engine.dispose()
    logging.info("Database connection closed.")