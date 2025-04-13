from sqlalchemy import Integer, String, Float, Text, Boolean, ForeignKey
from sqlalchemy.orm import relationship, Mapped, mapped_column
from sqlalchemy.dialects.postgresql import UUID
from typing import List
from uuid import UUID as UUIDType
from .base_model import BaseModel

class Color(BaseModel):
    __tablename__ = "colors"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    code: Mapped[str] = mapped_column(String(255), nullable=True)  # Hex code or other color identifier
    
    # Relationships
    inventory_items: Mapped[List["Inventory"]] = relationship("Inventory", back_populates="color")

class Size(BaseModel):
    __tablename__ = "sizes"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    
    # Relationships
    inventory_items: Mapped[List["Inventory"]] = relationship("Inventory", back_populates="size")

class Inventory(BaseModel):
    __tablename__ = "inventory"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    product_id: Mapped[UUIDType] = mapped_column(UUID(as_uuid=True), ForeignKey("products.id"), nullable=False)    
    color_id: Mapped[int] = mapped_column(Integer, ForeignKey("colors.id"), nullable=True)
    size_id: Mapped[int] = mapped_column(Integer, ForeignKey("sizes.id"), nullable=True)
    amount: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    description: Mapped[str] = mapped_column(String(1024), nullable=True)

    # Relationships
    product: Mapped["Product"] = relationship("Product", back_populates="inventory_items")
    color: Mapped["Color"] = relationship("Color", back_populates="inventory_items")
    size: Mapped["Size"] = relationship("Size", back_populates="inventory_items")