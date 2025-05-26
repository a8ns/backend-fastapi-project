from sqlalchemy import Column, Integer, String, Float, Text, Boolean, ForeignKey, JSON, text, Index
from pgvector.sqlalchemy import Vector
from typing import cast, Optional, List, Dict, Any
from .base_model import BaseModel
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID, JSONB, TSVECTOR, ARRAY
from uuid import UUID as UUIDType

class Category(BaseModel):
    __tablename__ = "categories"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str] = mapped_column(String(1024), nullable=True)
    
    # Add search fields - removed server_default
    search_vector: Mapped[Any] = mapped_column(
        TSVECTOR,
        nullable=True
    )
    
    # Relationships
    products: Mapped[List["Product"]] = relationship("Product", back_populates="category")
    
    __table_args__ = (
        Index('idx_category_search_vector', 'search_vector', postgresql_using='gin'),
    )

class Product(BaseModel):
    __tablename__ = "products"
    id: Mapped[UUIDType] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        unique=True,
        nullable=False,
        server_default=text("gen_random_uuid()"),
    )
    shop_id: Mapped[UUIDType] = mapped_column(UUID(as_uuid=True), ForeignKey("shops.id"), nullable=False)
    
    # Basic product information
    title: Mapped[str] = mapped_column(String(256), nullable=False)
    description: Mapped[str] = mapped_column(String(4096), nullable=True)
    price: Mapped[float] = mapped_column(Float, nullable=False)
    
    # Product details
    brand: Mapped[str] = mapped_column(String(256), nullable=True)
    article_number: Mapped[str] = mapped_column(String(256), nullable=True)
    barcode: Mapped[str] = mapped_column(String(256), nullable=True)

    in_store_validation: Mapped[bool] = mapped_column(Boolean, default=False)
    original_offer_url: Mapped[str] = mapped_column(String(1024), nullable=True)

    # Media
    image_url: Mapped[str] = mapped_column(String(1024), nullable=True)
    additional_images: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSONB, nullable=True)
    
    # Categorization
    category_id: Mapped[int] = mapped_column(Integer, ForeignKey("categories.id"), nullable=True)
    tags: Mapped[str] = mapped_column(String(255), nullable=True)  # Comma-separated tags
    
    # Search capabilities - removed server_default
    search_vector: Mapped[Any] = mapped_column(
        TSVECTOR,
        nullable=True
    )
    
    # Vector embeddings for semantic search - initially NULL
    embedding: Mapped[Optional[list]] = mapped_column(
        Vector(1536), # Assuming OpenAI text-embedding-3-small
        nullable=True
    ) 
    
    # Relationships
    shop: Mapped["Shop"] = relationship("Shop", back_populates="products")
    category: Mapped["Category"] = relationship("Category", back_populates="products")
    inventory_items: Mapped[List["Inventory"]] = relationship("Inventory", back_populates="product")
    
    __table_args__ = (
        Index('idx_product_search_vector', 'search_vector', postgresql_using='gin'),
        # Comment out until ready to activate vector search
        # Index('idx_product_embedding', 'embedding', postgresql_using='hnsw', postgresql_with={'cosine': True}),
    )