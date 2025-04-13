from pydantic import BaseModel
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
    product_id: Optional[UUID] = None
    color_id: Optional[int] = None
    size_id: Optional[int] = None
    amount: Optional[int] = None
    description: Optional[str] = None

class InventorySchema(InventoryBase):
    pass