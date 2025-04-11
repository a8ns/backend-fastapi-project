from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime

# Base product schema for use in other schemas
class ProductSimpleBase(BaseModel):
    id: int
    title: str
    price: float
    image_url: Optional[str] = None
    
    class Config:
        orm_mode = True

# Base shop schema for use in other schemas
class ShopSimpleBase(BaseModel):
    id: int
    name: str
    city: str
    
    class Config:
        orm_mode = True