from sqlalchemy import Column, Integer, String, Float, Text, Boolean, ForeignKey, JSON, text, Index, func
from sqlalchemy.orm import relationship, Mapped, mapped_column
from pgvector.sqlalchemy import Vector
from sqlalchemy.dialects.postgresql import UUID, JSONB, TSVECTOR, ARRAY
from typing import List, Any
from uuid import UUID as UUIDType
from .base_model import BaseModel

class Color(BaseModel):
    __tablename__ = "colors"
    id: Mapped[int] = mapped_column(
        Integer, 
        primary_key=True, 
        index=True,
        autoincrement=True
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    code: Mapped[str] = mapped_column(String(255), nullable=True)
    
    # Add search field
    search_vector: Mapped[Any] = mapped_column(
        TSVECTOR,
        nullable=True
    )
    
    # Relationships
    inventory_items: Mapped[List["Inventory"]] = relationship("Inventory", back_populates="color")
    
    __table_args__ = (
        Index('idx_color_search_vector', 'search_vector', postgresql_using='gin'),
    )

class Size(BaseModel):
    __tablename__ = "sizes"
    id: Mapped[int] = mapped_column(
        Integer, 
        primary_key=True, 
        index=True,
        autoincrement=True
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    
    # Add search field
    search_vector: Mapped[Any] = mapped_column(
        TSVECTOR,
        nullable=True
    )
    
    # Relationships
    inventory_items: Mapped[List["Inventory"]] = relationship("Inventory", back_populates="size")
    
    __table_args__ = (
        Index('idx_size_search_vector', 'search_vector', postgresql_using='gin'),
    )


class Inventory(BaseModel):
    __tablename__ = "inventory"
    id: Mapped[int] = mapped_column(
        Integer, 
        primary_key=True, 
        index=True,
        autoincrement=True
    )
    product_id: Mapped[UUIDType] = mapped_column(UUID(as_uuid=True), ForeignKey("products.id"), nullable=False)    
    color_id: Mapped[int] = mapped_column(Integer, ForeignKey("colors.id"), nullable=True)
    size_id: Mapped[int] = mapped_column(Integer, ForeignKey("sizes.id"), nullable=True)
    amount: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    description: Mapped[str] = mapped_column(String(1024), nullable=True)
    
    # Add search field for inventory descriptions
    search_vector: Mapped[Any] = mapped_column(
        TSVECTOR,
        nullable=True
    )
    
    # Relationships
    product: Mapped["Product"] = relationship("Product", back_populates="inventory_items")
    color: Mapped["Color"] = relationship("Color", back_populates="inventory_items")
    size: Mapped["Size"] = relationship("Size", back_populates="inventory_items")
    
    __table_args__ = (
        Index('idx_inventory_search_vector', 'search_vector', postgresql_using='gin'),
    )