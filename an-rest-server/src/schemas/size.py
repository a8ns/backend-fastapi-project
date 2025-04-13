from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class SizeBase(BaseModel):
    name: str

class SizeCreateSchema(SizeBase):
    pass

class SizeUpdateSchema(BaseModel):
    name: Optional[str] = None

class SizeSchema(SizeBase):
    pass