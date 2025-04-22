from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

class SizeBase(BaseModel):
    name: str

class SizeCreateSchema(SizeBase):
    pass

class SizeUpdateSchema(BaseModel):
    size_id: int = Field(alias="id", serialization_alias="size_id")
    name: str

class SizeSchema(SizeBase):
    size_id: int = Field(alias="id", serialization_alias="size_id") 
    
    class Config:
        from_attributes = True
        populate_by_name = True