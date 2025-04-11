from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, DateTime, func, MetaData


metadata = MetaData()
Base = declarative_base(metadata=metadata)

class BaseModel(Base):
    __abstract__ = True  # Indicates that this class shouldn't be mapped to a database table
    # __table_args__ = {'schema': 'test_schema'}
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())