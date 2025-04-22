from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
from uuid import UUID

class ShopBase(BaseModel):
    name: str
    description: Optional[str] = None
    address: Optional[str] = None
    city: Optional[str] = None
    state_or_province: Optional[str] = None
    postal_code: Optional[str] = None
    country: Optional[str] = None
    latitude: float
    longitude: float
    phone: Optional[str] = None
    email: Optional[str] = None
    website: Optional[str] = None
    opening_hours: Optional[str] = None
    image_url: Optional[str] = None
    additional_images: Optional[Dict[str, Any] | List[Any]] = None
    category: Optional[str] = None
    tags: Optional[str] = None

class ShopCreateSchema(ShopBase):
    pass

class ShopUpdateSchema(BaseModel):
    shop_id: UUID = Field(alias="id", serialization_alias="shop_id")
    name: Optional[str] = None
    description: Optional[str] = None
    address: Optional[str] = None
    city: Optional[str] = None
    state_or_province: Optional[str] = None
    postal_code: Optional[str] = None
    country: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    phone: Optional[str] = None
    email: Optional[str] = None
    website: Optional[str] = None
    opening_hours: Optional[str] = None
    image_url: Optional[str] = None
    additional_images: Optional[Dict[str, Any] | List[Any]] = None
    category: Optional[str] = None
    tags: Optional[str] = None
    
    class Config:
        from_attributes = True  # This enables ORM mode for Pydantic v2
        populate_by_name = True

class ShopSchema(ShopBase):
    shop_id: UUID = Field(alias="id", serialization_alias="shop_id")
    is_active: bool
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True  # This enables ORM mode for Pydantic v2
        populate_by_name = True  