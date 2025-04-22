from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

class ColorBase(BaseModel):
    name: str
    code: Optional[str] = None



class ColorCreateSchema(ColorBase):
    pass

class ColorUpdateSchema(BaseModel):
    color_id: int = Field(alias="id", serialization_alias="color_id")
    name: Optional[str] = None
    code: Optional[str] = None

class ColorSchema(ColorBase):
    color_id: int = Field(alias="id", serialization_alias="color_id")
    
    class Config:
        from_attributes = True
        populate_by_name = True