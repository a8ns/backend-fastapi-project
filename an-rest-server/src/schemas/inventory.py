from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from uuid import UUID

class InventoryBase(BaseModel):
    product_id: UUID
    color_id: Optional[int] = None
    size_id: Optional[int] = None
    amount: int = 0
    description: Optional[str] = None

class InventoryCreateSchema(InventoryBase):
    pass

class InventoryUpdateSchema(BaseModel):
    inventory_id: int = Field(alias="id", serialization_alias="inventory_id")
    product_id: Optional[UUID] = None
    color_id: Optional[int] = None
    size_id: Optional[int] = None
    amount: Optional[int] = None
    description: Optional[str] = None
    
    class Config:
        from_attributes = True
        populate_by_name = True

class InventorySchema(InventoryBase):
    inventory_id: int = Field(alias="id", serialization_alias="inventory_id")
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True  # This enables ORM mode for Pydantic v2
        populate_by_name = True 