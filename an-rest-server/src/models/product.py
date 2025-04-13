from sqlalchemy import Column, Integer, String, Float, Text, Boolean, ForeignKey, JSON
from typing import cast, Optional, List
from sqlalchemy.orm import relationship
from .base_model import BaseModel
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
from sqlalchemy.dialects.postgresql import UUID, JSONB
from uuid import UUID as UUIDType

class Category(BaseModel):
    __tablename__ = "categories"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str] = mapped_column(String(1024), nullable=True)    
    # Relationships
    products: Mapped[List["Product"]] = relationship("Product", back_populates="category")

class Product(BaseModel):
    __tablename__ = "products"
    id: Mapped[UUIDType] = mapped_column(UUID(as_uuid=True),primary_key=True, unique=True, nullable=False)
    shop_id: Mapped[UUIDType] = mapped_column(UUID(as_uuid=True), ForeignKey("shops.id"), nullable=False)
    
    # Basic product information
    title: Mapped[str] = mapped_column(String(256), nullable=False)
    description: Mapped[str] = mapped_column(String(1024), nullable=True)
    price: Mapped[float] = mapped_column(Float, nullable=False)
    
    # Product details
    brand: Mapped[str] = mapped_column(String(256), nullable=True)
    article_number: Mapped[str] = mapped_column(String(256), nullable=True)
    barcode: Mapped[str] = mapped_column(String(256), nullable=True)
    
    # Media
    image_url: Mapped[str] = mapped_column(String(512), nullable=True)
    additional_images: Mapped[Optional[dict|list]] = mapped_column(JSONB, nullable=True) # JSON array of image URLs
    
    # Categorization
    category_id: Mapped[int] = mapped_column(Integer, ForeignKey("categories.id"), nullable=True)
    tags: Mapped[str] = mapped_column(String(255), nullable=True)  # Comma-separated tags
    
    # Relationships
    shop: Mapped["Shop"] = relationship("Shop", back_populates="products")
    category: Mapped["Category"] = relationship("Category", back_populates="products")
    inventory_items: Mapped["Inventory"] = relationship("Inventory", back_populates="product")
