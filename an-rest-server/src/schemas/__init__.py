# Import all schemas to make them available from the package
from .shop import (
    Shop, ShopCreate, ShopUpdate, ShopWithProducts, 
    ShopMetadata, ShopMetadataCreate, ShopMetadataUpdate,
    ShopWithMetadata, NearbyShopParams
)
from .product import (
    Product, ProductCreate, ProductUpdate, ProductSimple,
    ProductMetadata, ProductMetadataCreate, ProductMetadataUpdate,
    ProductWithMetadata, ProductWithShop
)
from .llm import (
    LLMRequest, LLMResponse, 
    ProductDescriptionRequest, ProductNameGenerationRequest
)