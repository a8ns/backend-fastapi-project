
from models import *  # Import all models from models package
from .session import engine
from db.base_model import Base  # Importing Base from db/base.py
from sqlalchemy import insert, update, select, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
import logging
import json



async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

async def close_db():
    await engine.dispose()
    logging.info("Database connection closed.")