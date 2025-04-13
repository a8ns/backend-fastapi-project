from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from datetime import datetime
from uuid import UUID

class ProductBase(BaseModel):
    shop_id: UUID
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
    pass

class ProductUpdateSchema(BaseModel):
    shop_id: Optional[UUID] = None
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
    pass