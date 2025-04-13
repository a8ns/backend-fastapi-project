from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class CategoryBase(BaseModel):
    name: str
    description: Optional[str] = None

class CategoryCreateSchema(CategoryBase):
    pass

class CategoryUpdateSchema(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None

class CategorySchema(CategoryBase):
    pass