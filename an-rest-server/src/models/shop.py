from sqlalchemy import Integer, String, Float, Text, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
from sqlalchemy.dialects.postgresql import UUID, JSONB
# from geoalchemy2 import Geography
from db.base_model import BaseModel
from uuid import UUID as UUIDType

class Shop(BaseModel):
    __tablename__ = "shops"
    id: Mapped[UUIDType] = mapped_column(UUID(as_uuid=True),primary_key=True, unique=True, nullable=False)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str] = mapped_column(String(2048), nullable=True)
    
    # Address information
    address: Mapped[str] = mapped_column(String(255), nullable=True)
    city: Mapped[str] = mapped_column(String(255), nullable=True)
    state_or_province: Mapped[str] = mapped_column(String(255), nullable=True)
    postal_code: Mapped[str] = mapped_column(String(50), nullable=True)
    country: Mapped[str] = mapped_column(String(255), nullable=True)
    
    # GPS coordinates
    latitude: Mapped[float] = mapped_column(Float, nullable=False)
    longitude: Mapped[float] = mapped_column(Float, nullable=False)
    # location = Column(Geography(geometry_type='POINT', srid=4326), nullable=True)
    
    # Metadata
    phone: Mapped[str] = mapped_column(String(20), nullable=True)
    email: Mapped[str] = mapped_column(String(255), nullable=False)
    website: Mapped[str] = mapped_column(String(512), nullable=True)
    opening_hours: Mapped[str] = mapped_column(String(255), nullable=False)
    
    # Status
    is_active: Mapped[bool] = mapped_column(Boolean, default=False)
    
    # Optional category/tags for filtering
    category: Mapped[str] = mapped_column(String(255), nullable=True)
    tags: Mapped[str] = mapped_column(String(255), nullable=True)  # Comma-separated tags
    
    # Relationships
    products = relationship("Product", back_populates="shop")