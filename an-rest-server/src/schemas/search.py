from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from uuid import UUID
from datetime import datetime

# Base search result model
class SearchResult(BaseModel):
    id: str
    relevance: float = Field(ge=0.0, le=1.0, description="Search relevance score")

# Product search result
class ProductSearchResult(SearchResult):
    title: str
    description: Optional[str] = None
    price: float
    brand: Optional[str] = None
    image_url: Optional[str] = None
    category_id: Optional[int] = None
    category_name: Optional[str] = None
    tags: Optional[str] = None
    
    class Config:
        from_attributes = True

# Category search result
class CategorySearchResult(SearchResult):
    name: str
    description: Optional[str] = None
    product_count: Optional[int] = None
    
    class Config:
        from_attributes = True

# Color search result
class ColorSearchResult(SearchResult):
    name: str
    code: Optional[str] = None
    
    class Config:
        from_attributes = True

# Size search result
class SizeSearchResult(SearchResult):
    name: str
    
    class Config:
        from_attributes = True

# Vector search configuration
class VectorSearchConfig(BaseModel):
    api_key: Optional[str] = None
    embedding_model: str = "text-embedding-3-small"
    dimensions: int = 1536

# Search request models
class ProductSearchRequest(BaseModel):
    query: str
    method: str = "text"  # "text", "vector", or "hybrid"
    category_id: Optional[int] = None
    brand: Optional[str] = None
    min_price: Optional[float] = None
    max_price: Optional[float] = None
    limit: int = 20

class CategorySearchRequest(BaseModel):
    query: str
    method: str = "text"  # "text", "vector", or "hybrid"
    limit: int = 20

# Response models
class SearchResponse(BaseModel):
    results: List[SearchResult]
    total: int
    query: str
    method: str
    execution_time_ms: float

class BackfillStatus(BaseModel):
    status: str
    processed: int
    total_remaining: int
    last_updated: datetime = Field(default_factory=datetime.now)