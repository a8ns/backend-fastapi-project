from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from uuid import UUID

class InventoryBase(BaseModel):
    color_id: Optional[int] = None
    size_id: Optional[int] = None
    amount: int = 0
    description: Optional[str] = None

class InventoryCreateSchema(InventoryBase):
    pass

class InventoryUpdateSchema(BaseModel):
    product_id: Optional[UUID] = None
    color_id: Optional[int] = None
    size_id: Optional[int] = None
    amount: Optional[int] = None
    description: Optional[str] = None

class InventorySchema(InventoryBase):
    id: UUID  # Add the id field here
    is_active: bool  # Added this field as it's in your model
    created_at: Optional[datetime] = None  # Add timestamp fields if they exist in your model
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True  # This enables ORM mode for Pydantic v2