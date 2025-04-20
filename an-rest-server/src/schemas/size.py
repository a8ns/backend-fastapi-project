from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class SizeBase(BaseModel):
    name: str

class SizeCreateSchema(SizeBase):
    pass

class SizeUpdateSchema(BaseModel):
    id: int
    name: Optional[str] = None

class SizeSchema(SizeBase):
    id: int
    
    class Config:
        from_attributes = True