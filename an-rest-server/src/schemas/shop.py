# schemas/shop.py
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
from schemas.base import ProductSimpleBase

class ShopBase(BaseModel):
    name: str
    description: Optional[str] = None
    
    # Address information
    address: str
    city: str
    state: Optional[str] = None
    postal_code: str
    country: str
    
    # GPS coordinates
    latitude: float
    longitude: float
    
    # Metadata
    phone: Optional[str] = None
    email: Optional[str] = None
    website: Optional[str] = None
    opening_hours: Optional[str] = None
    
    # Optional category/tags
    category: Optional[str] = None
    tags: Optional[str] = None


class ShopCreate(ShopBase):
    pass


class ShopUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    address: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    postal_code: Optional[str] = None
    country: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    phone: Optional[str] = None
    email: Optional[str] = None
    website: Optional[str] = None
    opening_hours: Optional[str] = None
    category: Optional[str] = None
    tags: Optional[str] = None
    is_active: Optional[bool] = None


class ShopInDBBase(ShopBase):
    id: int
    is_active: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True


class Shop(ShopInDBBase):
    pass


class ShopWithProducts(Shop):
    # Use the base class to avoid circular imports
    products: List[ProductSimpleBase] = []


class ShopMetadataCreate(BaseModel):
    key: str
    value: str


class ShopMetadataUpdate(BaseModel):
    value: str


class ShopMetadata(BaseModel):
    id: int
    shop_id: int
    key: str
    value: str
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True


class ShopWithMetadata(Shop):
    metadata: Dict[str, str] = {}


class NearbyShopParams(BaseModel):
    latitude: float
    longitude: float
    radius: float = Field(1000, description="Search radius in meters")
    limit: int = Field(10, description="Maximum number of results to return")