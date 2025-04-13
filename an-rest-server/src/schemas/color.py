from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class ColorBase(BaseModel):
    name: str
    code: Optional[str] = None

class ColorCreateSchema(ColorBase):
    pass

class ColorUpdateSchema(BaseModel):
    name: Optional[str] = None
    code: Optional[str] = None

class ColorSchema(ColorBase):
    pass