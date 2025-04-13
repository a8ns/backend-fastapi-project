from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime


class ColorBase(BaseModel):
    name: str
    code: Optional[str] = None


class ColorCreate(ColorBase):
    pass


class ColorInDBBase(ColorBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True


class Color(ColorInDBBase):
    pass


class SizeBase(BaseModel):
    name: str


class SizeCreate(SizeBase):
    pass


class SizeInDBBase(SizeBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True


class Size(SizeInDBBase):
    pass


class CategoryBase(BaseModel):
    name: str
    description: Optional[str] = None
    parent_id: Optional[int] = None


class CategoryCreate(CategoryBase):
    pass


class CategoryInDBBase(CategoryBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True


class Category(CategoryInDBBase):
    pass


class CategoryWithChildren(Category):
    subcategories: List['CategoryWithChildren'] = []

    class Config:
        orm_mode = True


# Define self-reference for CategoryWithChildren
CategoryWithChildren.update_forward_refs()


class InventoryBase(BaseModel):
    product_id: int
    color_id: Optional[int] = None
    size_id: Optional[int] = None
    amount: int = 0
    short_description: Optional[str] = None


class InventoryCreate(BaseModel):
    color_id: Optional[int] = None
    size_id: Optional[int] = None
    amount: int = 0
    short_description: Optional[str] = None


class InventoryUpdate(BaseModel):
    color_id: Optional[int] = None
    size_id: Optional[int] = None
    amount: Optional[int] = None
    short_description: Optional[str] = None


class InventoryInDBBase(InventoryBase):
    inventory_id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True


class Inventory(InventoryInDBBase):
    pass


class InventoryWithDetails(Inventory):
    color: Optional[Color] = None
    size: Optional[Size] = None

    class Config:
        orm_mode = True