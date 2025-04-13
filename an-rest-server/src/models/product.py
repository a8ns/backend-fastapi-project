from sqlalchemy import Column, Integer, String, Float, Text, Boolean, ForeignKey, JSON
from sqlalchemy.orm import relationship
from db.base_model import BaseModel
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
from sqlalchemy.dialects.postgresql import UUID, JSONB
from uuid import UUID as UUIDType


class Product(BaseModel):
    __tablename__ = "products"
    id: Mapped[UUIDType] = mapped_column(UUID(as_uuid=True),primary_key=True, unique=True, nullable=False)
    shop_id = Column(Integer, ForeignKey("shops.id"), nullable=False)
    
    # Basic product information
    title = Column(String, index=True, nullable=False)
    description = Column(Text, nullable=True)
    price = Column(Float, nullable=False)
    
    # Product details
    brand = Column(String, index=True, nullable=True)
    article_number = Column(String, index=True, nullable=True)
    barcode = Column(String, index=True, nullable=True)
    
    # Media
    image_url = Column(String, nullable=True)
    additional_images = Column(JSON, nullable=True)  # JSON array of image URLs
    
    # Inventory
    in_stock = Column(Boolean, default=True)
    stock_quantity = Column(Integer, nullable=True)
    
    # Categorization
    category_id = Column(Integer, ForeignKey("categories.id"), nullable=True)
    tags = Column(String, nullable=True)  # Comma-separated tags
    
    # Status
    is_active = Column(Boolean, default=True)
    
    # Relationships
    shop = relationship("Shop", back_populates="products")
    category = relationship("Category", back_populates="products")
    inventory_items = relationship("Inventory", back_populates="product")