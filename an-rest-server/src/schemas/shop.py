from pydantic import BaseModel
from typing import Optional
from datetime import datetime

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
    email: str
    website: Optional[str] = None
    opening_hours: str
    category: Optional[str] = None
    tags: Optional[str] = None

class ShopCreateSchema(ShopBase):
    pass

class ShopUpdateSchema(BaseModel):
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
    category: Optional[str] = None
    tags: Optional[str] = None

class ShopSchema(ShopBase):
    pass