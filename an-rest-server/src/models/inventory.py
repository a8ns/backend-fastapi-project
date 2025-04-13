from sqlalchemy import Column, Integer, String, Float, Text, Boolean, ForeignKey
from sqlalchemy.orm import relationship, backref
from db.base_model import BaseModel

class Color(BaseModel):
    __tablename__ = "colors"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    code = Column(String, nullable=True)  # Hex code or other color identifier
    
    # Relationships
    inventory_items = relationship("Inventory", back_populates="color")

class Size(BaseModel):
    __tablename__ = "sizes"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    
    # Relationships
    inventory_items = relationship("Inventory", back_populates="size")

class Category(BaseModel):
    __tablename__ = "categories"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    parent_id = Column(Integer, ForeignKey("categories.id"), nullable=True)
    
    # Relationships
    products = relationship("Product", back_populates="category")
    # subcategories = relationship("Category", 
    #                             backref=backref("parent", remote_side=[id]),
    #                             cascade="all, delete-orphan")

class Inventory(BaseModel):
    __tablename__ = "inventory"
    inventory_id = Column(Integer, primary_key=True, index=True)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False)
    color_id = Column(Integer, ForeignKey("colors.id"), nullable=True)
    size_id = Column(Integer, ForeignKey("sizes.id"), nullable=True)
    amount = Column(Integer, nullable=False, default=0)
    short_description = Column(String, nullable=True)
    
    # Relationships
    product = relationship("Product", back_populates="inventory_items")
    color = relationship("Color", back_populates="inventory_items")
    size = relationship("Size", back_populates="inventory_items")