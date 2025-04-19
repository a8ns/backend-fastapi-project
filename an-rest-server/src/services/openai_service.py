from typing import Dict, Any, Optional
from core.logging import logger
from openai import AsyncOpenAI
from core.config import settings


class OpenAIService:
    """Service for interacting with OpenAI APIs"""
    
    def __init__(self, api_key: Optional[str] = None):
        self.client = AsyncOpenAI(api_key=api_key or settings.openai_api_key)
        self.default_model = settings.default_llm_model or "gpt-4-turbo"
    
    async def generate_text(
        self,
        prompt: str,
        model: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 1000,
        **kwargs
    ) -> Dict[str, Any]:
        """Generate text using OpenAI's API"""
        
        try:
            response = await self.client.chat.completions.create(
                model=model or self.default_model,
                messages=[{"role": "user", "content": prompt}],
                temperature=temperature,
                max_tokens=max_tokens,
                **kwargs
            )
            
            return {
                "text": response.choices[0].message.content,
                "model": model or self.default_model,
                "tokens": {
                    "prompt": response.usage.prompt_tokens,
                    "completion": response.usage.completion_tokens,
                    "total": response.usage.total_tokens
                },
                "finish_reason": response.choices[0].finish_reason
            }
        except Exception as e:
            logger.error(f"Error generating text with OpenAI: {e}")
            raise