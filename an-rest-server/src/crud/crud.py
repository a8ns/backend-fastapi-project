from sqlalchemy.ext.asyncio import AsyncSession
from .crud_base import CRUDBase
from models import (Shop, Product, Category, Color, Size, Inventory)

from schemas import (ShopCreateSchema, ShopUpdateSchema)
from schemas import (ProductCreateSchema, ProductUpdateSchema)
from schemas import (InventoryCreateSchema, InventoryUpdateSchema)
from schemas import (CategoryCreateSchema,CategoryUpdateSchema)
from schemas import (ColorCreateSchema, ColorUpdateSchema)
from schemas import (SizeCreateSchema, SizeUpdateSchema)


# -------------- SHOP CRUD -------------------- #
class CRUDShop(CRUDBase[Shop, ShopCreateSchema, ShopUpdateSchema]):
    def __init__(self):
        super().__init__(Shop)

# -------------- PRODUCT CRUD -------------------- #
class CRUDProduct(CRUDBase[Product, ProductCreateSchema, ProductUpdateSchema]):
    def __init__(self):
        super().__init__(Product)

# -------------- INVENTORY CRUD -------------------- #
class CRUDInventory(CRUDBase[Inventory, InventoryCreateSchema, InventoryUpdateSchema]):
    def __init__(self):
        super().__init__(Inventory)

# -------------- CATEGORY CRUD -------------------- #
class CRUDCategory(CRUDBase[Category, CategoryCreateSchema, CategoryUpdateSchema]):
    def __init__(self):
        super().__init__(Category)

# -------------- COLOR CRUD -------------------- #
class CRUDColor(CRUDBase[Color, ColorCreateSchema, ColorUpdateSchema]):
    def __init__(self):
        super().__init__(Color)

# -------------- SIZE CRUD -------------------- #
class CRUDSize(CRUDBase[Size, SizeCreateSchema, SizeUpdateSchema]):
    def __init__(self):
        super().__init__(Size)


crud_shop = CRUDShop()
crud_product = CRUDProduct()
crud_inventory = CRUDInventory()
crud_category = CRUDCategory()
crud_color = CRUDColor()
crud_size = CRUDSize()