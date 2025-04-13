# schemas/__init__.py
from .base import ProductSimpleBase, ShopSimpleBase
from .shop import (
    ShopBase, ShopCreate, ShopUpdate, Shop, ShopWithProducts,
    NearbyShopParams
)
from .product import (
    ProductBase, ProductCreate, ProductUpdate, Product, ProductSimple,
    ProductWithShop, ProductWithInventory
)
from .inventory import (
    Color, ColorCreate, Size, SizeCreate,
    Category, CategoryCreate, CategoryWithChildren,
    Inventory, InventoryCreate, InventoryUpdate, InventoryWithDetails
)
from .llm import (
    LLMRequest, LLMResponse, 
    ProductDescriptionRequest, ProductNameGenerationRequest
)