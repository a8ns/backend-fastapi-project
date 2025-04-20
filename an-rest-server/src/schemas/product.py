from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from datetime import datetime
from uuid import UUID

class ProductBase(BaseModel):
    title: str
    description: Optional[str] = None
    price: float
    brand: Optional[str] = None
    article_number: Optional[str] = None
    barcode: Optional[str] = None
    image_url: Optional[str] = None
    additional_images: Optional[Dict[str, Any] | List[Any]] = None
    category_id: Optional[int] = None
    tags: Optional[str] = None

class ProductCreateSchema(ProductBase):
    shop_id: UUID

class ProductUpdateSchema(BaseModel):
    id: UUID
    title: Optional[str] = None
    description: Optional[str] = None
    price: Optional[float] = None
    brand: Optional[str] = None
    article_number: Optional[str] = None
    barcode: Optional[str] = None
    image_url: Optional[str] = None
    additional_images: Optional[Dict[str, Any] | List[Any]] = None
    category_id: Optional[int] = None
    tags: Optional[str] = None

class ProductSchema(ProductBase):
    id: UUID
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True