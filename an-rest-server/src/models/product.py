from sqlalchemy import Column, Integer, String, Float, Text, Boolean, ForeignKey, JSON
from sqlalchemy.orm import relationship
from db.base_model import BaseModel

class Product(BaseModel):
    __tablename__ = "products"

    id = Column(Integer, primary_key=True, index=True)
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
    category = Column(String, index=True, nullable=True)
    tags = Column(String, nullable=True)  # Comma-separated tags
    
    # Status
    is_active = Column(Boolean, default=True)
    
    # Relationships
    shop = relationship("Shop", back_populates="products")
    product_metadata = relationship("ProductMetadata", back_populates="product")


class ProductMetadata(BaseModel):
    __tablename__ = "product_metadata"

    id = Column(Integer, primary_key=True, index=True)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False)
    key = Column(String, nullable=False)
    value = Column(String, nullable=False)
    
    # Relationships
    product = relationship("Product", back_populates="product_metadata")
