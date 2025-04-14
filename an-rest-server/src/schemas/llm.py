from pydantic import BaseModel, Field
from typing import Dict, Any, Optional, List

# Basic request and response models
class LLMRequest(BaseModel):
    prompt: str
    model: Optional[str] = None
    temperature: Optional[float] = 0.2  # Updated default for deterministic JSON responses
    max_tokens: Optional[int] = 300     # Updated default for JSON responses
    additional_params: Optional[Dict[str, Any]] = None

class LLMResponse(BaseModel):
    text: str
    model: str
    tokens: Dict[str, int]
    finish_reason: Optional[str] = None

# Simplified product keyword extraction request
class ProductKeywordExtractionRequest(BaseModel):
    text: str = Field(..., description="Text to extract product keywords from")
    model: Optional[str] = None
    temperature: Optional[float] = 0.2
    max_tokens: Optional[int] = 300

# More specific schemas for different product services
class ProductDescriptionRequest(BaseModel):
    title: str
    key_points: List[str]
    tone: str = Field("professional", description="The tone of the description")
    length: str = Field("medium", description="Length of the description (short, medium, long)")
    model: Optional[str] = None

class ProductNameGenerationRequest(BaseModel):
    product_type: str
    features: List[str]
    target_audience: Optional[str] = None
    brand_style: Optional[str] = None
    count: int = Field(5, description="Number of name suggestions to generate")
    model: Optional[str] = None