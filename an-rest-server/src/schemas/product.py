from pydantic import BaseModel, Field
from schemas.color import ColorSchema
from schemas.size import SizeSchema
from typing import Optional, List, Dict, Any
from datetime import datetime
from uuid import UUID

class ProductBase(BaseModel):
    title: str
    description: Optional[str] = None
    price: float
    brand: Optional[str] = None
    article_number: Optional[str] = None
    barcode: Optional[str] = None
    image_url: Optional[str] = None
    additional_images: Optional[Dict[str, Any] | List[Any]] = None
    category_id: Optional[int] = None
    tags: Optional[str] = None

class ProductCreateSchema(ProductBase):
    shop_id: UUID

class ProductUpdateSchema(BaseModel):
    product_id: UUID = Field(alias="id", serialization_alias="product_id")
    shop_id: Optional[UUID] = None
    title: Optional[str] = None
    description: Optional[str] = None
    price: Optional[float] = None
    brand: Optional[str] = None
    article_number: Optional[str] = None
    barcode: Optional[str] = None
    image_url: Optional[str] = None
    additional_images: Optional[Dict[str, Any] | List[Any]] = None
    category_id: Optional[int] = None
    tags: Optional[str] = None

class ProductSchema(ProductBase):
    product_id: UUID = Field(alias="id", serialization_alias="product_id")
    shop_id: UUID
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True
        
class ProductWithShopNamesSchema(ProductSchema):
    """Schema for product with shop name information"""
    shop_name: str
    
    class Config:
        from_attributes = True

class ProductsWithShopNamesResponseSchema(BaseModel):
    """Response schema for multiple products with shop names"""
    total: int
    items: List[ProductWithShopNamesSchema]
    
    class Config:
        from_attributes = True

class ProductVariation(BaseModel):
    inventory_id: int
    color: Optional[ColorSchema] = None
    size: Optional[SizeSchema] = None
    amount: int
    description: Optional[str] = None
    
    class Config:
        from_attributes = True

class ProductWithVariationsSchema(ProductSchema):
    variations: List[ProductVariation] = []
    
    class Config:
        from_attributes = True

class ShopProductsSchema(BaseModel):
    shop_id: UUID
    total_products: int
    products: List[ProductSchema]
    
    class Config:
        from_attributes = True