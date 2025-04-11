from pydantic import BaseModel, Field
from typing import Dict, Any, Optional, List


class LLMRequest(BaseModel):
    prompt: str
    model: Optional[str] = None
    temperature: float = 0.7
    max_tokens: int = 1000
    additional_params: Optional[Dict[str, Any]] = None
    provider: Optional[str] = Field(None, description="LLM provider to use (openai or claude)")


class LLMResponse(BaseModel):
    text: str
    model: str
    tokens: Dict[str, int]
    finish_reason: Optional[str] = None


class ProductDescriptionRequest(BaseModel):
    title: str
    key_points: List[str]
    tone: str = Field("professional", description="The tone of the description (casual, professional, enthusiastic, etc.)")
    length: str = Field("medium", description="Length of the description (short, medium, long)")
    provider: Optional[str] = Field(None, description="LLM provider to use (openai or claude)")


class ProductNameGenerationRequest(BaseModel):
    product_type: str
    features: List[str]
    target_audience: Optional[str] = None
    brand_style: Optional[str] = None
    count: int = Field(5, description="Number of name suggestions to generate")
    provider: Optional[str] = Field(None, description="LLM provider to use (openai or claude)")