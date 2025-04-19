from typing import Dict, Any, Optional
from core.logging import logger
import anthropic

from core.config import settings

class ClaudeService:
    """Service for interacting with Anthropic Claude API"""
    
    def __init__(self, api_key: Optional[str] = None):
        self.client = anthropic.AsyncAnthropic(api_key=api_key or settings.anthropic_api_key)
        self.default_model = settings.default_claude_model or "claude-3-opus-20240229"
    
    async def generate_text(
        self,
        prompt: str,
        model: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 1000,
        **kwargs
    ) -> Dict[str, Any]:
        """Generate text using Anthropic's Claude API"""
        
        try:
            response = await self.client.messages.create(
                model=model or self.default_model,
                messages=[{"role": "user", "content": prompt}],
                temperature=temperature,
                max_tokens=max_tokens,
                **kwargs
            )
            
            return {
                "text": response.content[0].text,
                "model": model or self.default_model,
                "tokens": {
                    "prompt": response.usage.input_tokens,
                    "completion": response.usage.output_tokens,
                    "total": response.usage.input_tokens + response.usage.output_tokens
                },
                "finish_reason": response.stop_reason
            }
        except Exception as e:
            logger.error(f"Error generating text with Claude: {e}")
            raise