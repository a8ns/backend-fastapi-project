# schemas/__init__.py
from .base import ProductSimpleBase, ShopSimpleBase
from .shop import (
    ShopBase, ShopCreate, ShopUpdate, Shop, ShopWithProducts,
    ShopMetadata, ShopMetadataCreate, ShopMetadataUpdate,
    ShopWithMetadata, NearbyShopParams
)
from .product import (
    ProductBase, ProductCreate, ProductUpdate, Product, ProductSimple,
    ProductMetadata, ProductMetadataCreate, ProductMetadataUpdate,
    ProductWithMetadata, ProductWithShop
)
from .llm import (
    LLMRequest, LLMResponse, 
    ProductDescriptionRequest, ProductNameGenerationRequest
)