from typing import AsyncGenerator, Optional
from fastapi import Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from db.session import get_db
from services.openai_service import OpenAIService
from services.claude_service import ClaudeService
from core.config import settings

async def get_openai_service() -> OpenAIService:
    """
    Get an instance of the OpenAI service.
    """
    return OpenAIService()

async def get_claude_service() -> ClaudeService:
    """
    Get an instance of the Claude service.
    """
    return ClaudeService()

async def get_llm_service(
    provider: Optional[str] = Query(None, description="LLM provider to use (openai or claude)")
):
    """
    Get the appropriate LLM service based on provider parameter or settings default.
    """
    provider = provider or settings.default_llm_provider
    
    if provider.lower() == "openai":
        return await get_openai_service()
    elif provider.lower() == "claude" or provider.lower() == "anthropic":
        return await get_claude_service()
    else:
        # Default to OpenAI if provider is not recognized
        return await get_openai_service()