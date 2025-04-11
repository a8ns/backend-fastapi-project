from sqlalchemy import Column, Integer, String, Float, Text, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from geoalchemy2 import Geography
from db.base_model import BaseModel

class Shop(BaseModel):
    __tablename__ = "shops"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True, nullable=False)
    description = Column(Text, nullable=True)
    
    # Address information
    address = Column(String, nullable=False)
    city = Column(String, nullable=False)
    state = Column(String, nullable=True)
    postal_code = Column(String, nullable=False)
    country = Column(String, nullable=False)
    
    # GPS coordinates
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    # location = Column(Geography(geometry_type='POINT', srid=4326), nullable=True)
    
    # Metadata
    phone = Column(String, nullable=True)
    email = Column(String, nullable=True)
    website = Column(String, nullable=True)
    opening_hours = Column(String, nullable=True)
    
    # Status
    is_active = Column(Boolean, default=True)
    
    # Optional category/tags for filtering
    category = Column(String, nullable=True)
    tags = Column(String, nullable=True)  # Comma-separated tags
    
    # Relationships
    products = relationship("Product", back_populates="shop")


class ShopMetadata(BaseModel):
    __tablename__ = "shop_metadata"

    id = Column(Integer, primary_key=True, index=True)
    shop_id = Column(Integer, ForeignKey("shops.id"), nullable=False)
    key = Column(String, nullable=False)
    value = Column(String, nullable=False)

    shop = relationship("Shop", back_populates="shop_metadata")
