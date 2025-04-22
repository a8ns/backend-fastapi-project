from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

class CategoryBase(BaseModel):
    name: str
    description: Optional[str] = None

class CategoryCreateSchema(CategoryBase):
    pass

class CategoryUpdateSchema(BaseModel):
    category_id: int = Field(alias="id", serialization_alias="category_id")
    name: Optional[str] = None
    description: Optional[str] = None

class CategorySchema(CategoryBase):
    category_id: int = Field(alias="id", serialization_alias="category_id")
    
    class Config:
        from_attributes = True
        populate_by_name = True  