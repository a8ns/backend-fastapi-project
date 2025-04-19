from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import update, func
from typing import Union, Dict, Any
from .crud_base import CRUDBase
from models import (Shop, Product, Category, Color, Size, Inventory)
from schemas import (ShopCreateSchema, ShopUpdateSchema)
from schemas import (ProductCreateSchema, ProductUpdateSchema)
from schemas import (InventoryCreateSchema, InventoryUpdateSchema)
from schemas import (CategoryCreateSchema, CategoryUpdateSchema)
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
    
    async def update_search_vector(self, db_session: AsyncSession, obj: Product) -> Product:
        """Update product search vector"""
        search_text = f"{obj.title} {obj.description or ''} {obj.brand or ''} {obj.tags or ''}"
        query = update(Product).where(Product.id == obj.id).values(
            search_vector=func.to_tsvector('english', search_text)
        )
        await db_session.execute(query)
        await db_session.refresh(obj)
        return obj
        
    async def create(self, db_session: AsyncSession, *, obj_in: Union[ProductCreateSchema, Dict[str, Any]]) -> Product:
        db_obj = await super().create(db_session, obj_in=obj_in)
        return await self.update_search_vector(db_session, db_obj)
    
    async def update(self, db_session: AsyncSession, *, db_obj: Product, obj_in: Union[ProductUpdateSchema, Dict[str, Any]]) -> Product:
        db_obj = await super().update(db_session, db_obj=db_obj, obj_in=obj_in)
        return await self.update_search_vector(db_session, db_obj)

# -------------- INVENTORY CRUD -------------------- #
class CRUDInventory(CRUDBase[Inventory, InventoryCreateSchema, InventoryUpdateSchema]):
    def __init__(self):
        super().__init__(Inventory)

# -------------- CATEGORY CRUD -------------------- #
class CRUDCategory(CRUDBase[Category, CategoryCreateSchema, CategoryUpdateSchema]):
    def __init__(self):
        super().__init__(Category)
    
    async def update_search_vector(self, db_session: AsyncSession, obj: Category) -> Category:
        """Update category search vector"""
        search_text = f"{obj.name} {obj.description or ''}"
        query = update(Category).where(Category.id == obj.id).values(
            search_vector=func.to_tsvector('english', search_text)
        )
        await db_session.execute(query)
        await db_session.refresh(obj)
        return obj
        
    async def create(self, db_session: AsyncSession, *, obj_in: Union[CategoryCreateSchema, Dict[str, Any]]) -> Category:
        db_obj = await super().create(db_session, obj_in=obj_in)
        return await self.update_search_vector(db_session, db_obj)
    
    async def update(self, db_session: AsyncSession, *, db_obj: Category, obj_in: Union[CategoryUpdateSchema, Dict[str, Any]]) -> Category:
        db_obj = await super().update(db_session, db_obj=db_obj, obj_in=obj_in)
        return await self.update_search_vector(db_session, db_obj)

# -------------- COLOR CRUD -------------------- #
class CRUDColor(CRUDBase[Color, ColorCreateSchema, ColorUpdateSchema]):
    def __init__(self):
        super().__init__(Color)
    
    async def update_search_vector(self, db_session: AsyncSession, obj: Color) -> Color:
        """Update color search vector"""
        search_text = f"{obj.name} {obj.code or ''}"
        query = update(Color).where(Color.id == obj.id).values(
            search_vector=func.to_tsvector('english', search_text)
        )
        await db_session.execute(query)
        await db_session.refresh(obj)
        return obj
        
    async def create(self, db_session: AsyncSession, *, obj_in: Union[ColorCreateSchema, Dict[str, Any]]) -> Color:
        db_obj = await super().create(db_session, obj_in=obj_in)
        return await self.update_search_vector(db_session, db_obj)
    
    async def update(self, db_session: AsyncSession, *, db_obj: Color, obj_in: Union[ColorUpdateSchema, Dict[str, Any]]) -> Color:
        db_obj = await super().update(db_session, db_obj=db_obj, obj_in=obj_in)
        return await self.update_search_vector(db_session, db_obj)

# -------------- SIZE CRUD -------------------- #
class CRUDSize(CRUDBase[Size, SizeCreateSchema, SizeUpdateSchema]):
    def __init__(self):
        super().__init__(Size)
    
    async def update_search_vector(self, db_session: AsyncSession, obj: Size) -> Size:
        """Update size search vector"""
        search_text = f"{obj.name}"
        query = update(Size).where(Size.id == obj.id).values(
            search_vector=func.to_tsvector('english', search_text)
        )
        await db_session.execute(query)
        await db_session.refresh(obj)
        return obj
        
    async def create(self, db_session: AsyncSession, *, obj_in: Union[SizeCreateSchema, Dict[str, Any]]) -> Size:
        db_obj = await super().create(db_session, obj_in=obj_in)
        return await self.update_search_vector(db_session, db_obj)
    
    async def update(self, db_session: AsyncSession, *, db_obj: Size, obj_in: Union[SizeUpdateSchema, Dict[str, Any]]) -> Size:
        db_obj = await super().update(db_session, db_obj=db_obj, obj_in=obj_in)
        return await self.update_search_vector(db_session, db_obj)

# Create instances
crud_shop = CRUDShop()
crud_product = CRUDProduct()
crud_inventory = CRUDInventory()
crud_category = CRUDCategory()
crud_color = CRUDColor()
crud_size = CRUDSize()