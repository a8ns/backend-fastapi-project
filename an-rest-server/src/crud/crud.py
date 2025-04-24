from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete, func
from sqlalchemy.orm import selectinload
from typing import Union, Dict, Any, Optional, List
from uuid import UUID
from .crud_base import CRUDBase
from models import (Shop, Product, Category, Color, Size, Inventory)
from schemas import (ShopCreateSchema, ShopUpdateSchema)
from schemas import (ProductCreateSchema, ProductUpdateSchema, ProductWithVariationsSchema)
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

    async def get_products_by_shop(
        self, 
        db_session: AsyncSession, 
        shop_id: UUID,
        *, 
        skip: int = 0, 
        limit: int = 100
    ) -> List[Product]:
        """Get all products for a specific shop"""
        
        query = (
            select(Product)
            .filter(Product.shop_id == shop_id)
            .offset(skip)
            .limit(limit)
        )
        
        result = await db_session.execute(query)
        return result.scalars().all()
    
    async def count_products_by_shop(
        self,
        db_session: AsyncSession,
        shop_id: UUID
    ) -> int:
        """Count products for a specific shop"""
        query = (
            select(func.count())
            .select_from(Product)
            .filter(Product.shop_id == shop_id)
        )
        
        result = await db_session.execute(query)
        return result.scalar_one()

    async def get_with_variations(
            self, 
            db_session: AsyncSession, 
            product_id: UUID
        ) -> Optional[ProductWithVariationsSchema]:
        """Get a product with all its variations (inventory items)"""
        query = (
            select(Product)
            .options(
                selectinload(Product.inventory_items).selectinload(Inventory.color),
                selectinload(Product.inventory_items).selectinload(Inventory.size)
            )
            .filter(Product.id == product_id)
        )
        
        result = await db_session.execute(query)
        product = result.scalar_one_or_none()
        
        if not product:
            return None
        
        # Map inventory items to variations
        variations = [
            {
                "inventory_id": inventory.id,  # Explicit field name
                "color": {
                    "color_id": inventory.color.id,
                    "name": inventory.color.name,
                    "code": inventory.color.code
                } if inventory.color else None,
                "size": {
                    "size_id": inventory.size.id,
                    "name": inventory.size.name
                } if inventory.size else None,
                "amount": inventory.amount,
                "description": inventory.description
            }
            for inventory in product.inventory_items
        ]
        
        return ProductWithVariationsSchema.model_validate({
            **product.__dict__,
            "variations": variations
        })
    
    async def get_all_with_variations(
        self, 
        db_session: AsyncSession, 
        *, 
        skip: int = 0, 
        limit: int = 100,
        filters: Optional[Dict[str, Any]] = None
    ) -> List[ProductWithVariationsSchema]:
        """Get all products with their variations, reusing get_with_variations logic"""
        # First get all products
        products = await self.get_multi(db_session, skip=skip, limit=limit, filters=filters)
        
        # Then get variations for each product
        products_with_variations = []
        for product in products:
            product_with_variations = await self.get_with_variations(db_session, product.id)
            if product_with_variations:
                products_with_variations.append(product_with_variations)
        
        return products_with_variations


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