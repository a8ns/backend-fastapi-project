from typing import AsyncGenerator, Optional
from fastapi import Depends

from services.openai_service import OpenAIService
from services.claude_service import ClaudeService
from core.config import settings

async def get_openai_service() -> OpenAIService:
    """
    Get an instance of the OpenAI service with the default API key from settings.
    """
    return OpenAIService(api_key=settings.openai_api_key)

async def get_claude_service() -> ClaudeService:
    """
    Get an instance of the Claude service with the default API key from settings.
    """
    return ClaudeService(api_key=settings.anthropic_api_key)

# This function is kept for backward compatibility with existing code
# but we're now preferring direct dependency injection of specific services
async def get_llm_service(provider: Optional[str] = None):
    """
    Get the appropriate LLM service based on provider parameter or settings default.
    For new code, prefer using get_openai_service or get_claude_service directly.
    """
    provider = provider or settings.default_llm_provider
    
    if provider and provider.lower() == "claude":
        return await get_claude_service()
    else:
        # Default to OpenAI
        return await get_openai_service()