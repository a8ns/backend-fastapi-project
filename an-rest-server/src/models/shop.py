from sqlalchemy import Column, Integer, String, Float, Text, Boolean, ForeignKey, JSON, text, Index, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID, JSONB

from typing import cast, Optional, List, Dict, Any
# from geoalchemy2 import Geography
from .base_model import BaseModel
from uuid import UUID as UUIDType

class Shop(BaseModel):
    __tablename__ = "shops"
    id: Mapped[UUIDType] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        unique=True,
        nullable=False,
        server_default=text("gen_random_uuid()"),  # PostgreSQL will generate the UUID
    )
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
    
    # Media
    image_url: Mapped[str] = mapped_column(String(512), nullable=True)
    additional_images: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSONB, nullable=True)  

    # Status
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    
    # Optional category/tags for filtering
    category: Mapped[str] = mapped_column(String(255), nullable=True)
    tags: Mapped[str] = mapped_column(String(255), nullable=True)  # Comma-separated tags
    
    # Relationships
    products: Mapped[List["Product"]] = relationship("Product", back_populates="shop")