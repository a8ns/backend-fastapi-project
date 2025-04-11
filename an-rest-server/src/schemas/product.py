from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime


class ProductBase(BaseModel):
    shop_id: int
    title: str
    description: Optional[str] = None
    price: float
    brand: Optional[str] = None
    article_number: Optional[str] = None
    barcode: Optional[str] = None
    image_url: Optional[str] = None
    additional_images: Optional[List[str]] = None
    in_stock: bool = True
    stock_quantity: Optional[int] = None
    category: Optional[str] = None
    tags: Optional[str] = None


class ProductCreate(ProductBase):
    pass


class ProductUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    price: Optional[float] = None
    brand: Optional[str] = None
    article_number: Optional[str] = None
    barcode: Optional[str] = None
    image_url: Optional[str] = None
    additional_images: Optional[List[str]] = None
    in_stock: Optional[bool] = None
    stock_quantity: Optional[int] = None
    category: Optional[str] = None
    tags: Optional[str] = None
    is_active: Optional[bool] = None


class ProductInDBBase(ProductBase):
    id: int
    is_active: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True


class ProductSimple(BaseModel):
    id: int
    title: str
    price: float
    image_url: Optional[str] = None
    
    class Config:
        orm_mode = True


class Product(ProductInDBBase):
    pass


class ProductWithShop(Product):
    shop_name: str
    shop_city: str


class ProductMetadataCreate(BaseModel):
    key: str
    value: str


class ProductMetadataUpdate(BaseModel):
    value: str


class ProductMetadata(BaseModel):
    id: int
    product_id: int
    key: str
    value: str
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True


class ProductWithMetadata(Product):
    metadata: Dict[str, str] = {}


from schemas.shop import ShopWithProducts
# Avoid circular import
ShopWithProducts.update_forward_refs()