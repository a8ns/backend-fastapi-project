from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import joinedload

from db.session import get_db
from models.product import Product
from models.shop import Shop
from models.inventory import Inventory, Color, Size, Category
from schemas.product import (
    Product as ProductSchema,
    ProductCreate,
    ProductUpdate,
    ProductSimple,
    ProductWithShop,
    ProductWithInventory
)
from schemas.inventory import (
    Inventory as InventorySchema,
    InventoryCreate,
    InventoryUpdate,
    InventoryWithDetails
)

router = APIRouter()


@router.post("/", response_model=ProductSchema)
async def create_product(
    product_in: ProductCreate,
    db: AsyncSession = Depends(get_db)
):
    """Create a new product"""
    # Check if shop exists
    shop_query = select(Shop).where(Shop.id == product_in.shop_id)
    shop_result = await db.execute(shop_query)
    shop = shop_result.scalars().first()
    
    if not shop:
        raise HTTPException(status_code=404, detail=f"Shop with id {product_in.shop_id} not found")
    
    # Check if category exists if provided
    if product_in.category_id:
        category_query = select(Category).where(Category.id == product_in.category_id)
        category_result = await db.execute(category_query)
        category = category_result.scalars().first()
        
        if not category:
            raise HTTPException(status_code=404, detail=f"Category with id {product_in.category_id} not found")
    
    # Create product object
    product = Product(**product_in.dict())
    db.add(product)
    await db.commit()
    await db.refresh(product)
    return product


@router.get("/", response_model=List[ProductSchema])
async def read_products(
    db: AsyncSession = Depends(get_db),
    skip: int = 0,
    limit: int = 100,
    shop_id: Optional[int] = None,
    title: Optional[str] = None,
    brand: Optional[str] = None,
    category_id: Optional[int] = None,
    min_price: Optional[float] = None,
    max_price: Optional[float] = None,
    in_stock: Optional[bool] = None,
    is_active: bool = True
):
    """List products with optional filtering"""
    query = select(Product).where(Product.is_active == is_active)
    
    if shop_id:
        query = query.where(Product.shop_id == shop_id)
    if title:
        query = query.where(Product.title.ilike(f"%{title}%"))
    if brand:
        query = query.where(Product.brand.ilike(f"%{brand}%"))
    if category_id:
        query = query.where(Product.category_id == category_id)
    if min_price is not None:
        query = query.where(Product.price >= min_price)
    if max_price is not None:
        query = query.where(Product.price <= max_price)
    if in_stock is not None:
        query = query.where(Product.in_stock == in_stock)
    
    query = query.offset(skip).limit(limit)
    result = await db.execute(query)
    return result.scalars().all()


@router.get("/with-shop", response_model=List[ProductWithShop])
async def read_products_with_shop(
    db: AsyncSession = Depends(get_db),
    skip: int = 0,
    limit: int = 100,
    category_id: Optional[int] = None,
    min_price: Optional[float] = None,
    max_price: Optional[float] = None
):
    """Get products with shop information"""
    # Use joinedload for more efficient querying
    query = select(Product).options(
        joinedload(Product.shop)
    ).where(Product.is_active == True)
    
    if category_id:
        query = query.where(Product.category_id == category_id)
    if min_price is not None:
        query = query.where(Product.price >= min_price)
    if max_price is not None:
        query = query.where(Product.price <= max_price)
    
    query = query.offset(skip).limit(limit)
    result = await db.execute(query)
    products = result.scalars().all()
    
    # Format the response
    result_list = []
    for product in products:
        product_dict = ProductSchema.from_orm(product).dict()
        product_with_shop = ProductWithShop(**product_dict)
        product_with_shop.shop = {
            "id": product.shop.id,
            "name": product.shop.name,
            "city": product.shop.city
        }
        result_list.append(product_with_shop)
    
    return result_list


@router.get("/with-inventory", response_model=List[ProductWithInventory])
async def read_products_with_inventory(
    db: AsyncSession = Depends(get_db),
    skip: int = 0,
    limit: int = 100,
    shop_id: Optional[int] = None,
    category_id: Optional[int] = None
):
    """Get products with inventory information"""
    query = select(Product).options(
        joinedload(Product.inventory_items).joinedload(Inventory.color),
        joinedload(Product.inventory_items).joinedload(Inventory.size)
    ).where(Product.is_active == True)
    
    if shop_id:
        query = query.where(Product.shop_id == shop_id)
    if category_id:
        query = query.where(Product.category_id == category_id)
    
    query = query.offset(skip).limit(limit)
    result = await db.execute(query)
    products = result.scalars().all()
    
    return products


@router.get("/{product_id}", response_model=ProductSchema)
async def read_product(
    product_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Get detailed product information"""
    query = select(Product).where(Product.id == product_id)
    result = await db.execute(query)
    product = result.scalars().first()
    
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    
    return product


@router.get("/{product_id}/inventory", response_model=List[InventoryWithDetails])
async def read_product_inventory(
    product_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Get all inventory items for a product"""
    # Verify product exists
    product_query = select(Product).where(Product.id == product_id)
    product_result = await db.execute(product_query)
    product = product_result.scalars().first()
    
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    
    # Get inventory with related color and size info
    query = select(Inventory).options(
        joinedload(Inventory.color),
        joinedload(Inventory.size)
    ).where(Inventory.product_id == product_id)
    
    result = await db.execute(query)
    inventory_items = result.scalars().all()
    
    return inventory_items


@router.put("/{product_id}", response_model=ProductSchema)
async def update_product(
    product_id: int,
    product_in: ProductUpdate,
    db: AsyncSession = Depends(get_db)
):
    """Update a product"""
    query = select(Product).where(Product.id == product_id)
    result = await db.execute(query)
    product = result.scalars().first()
    
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    
    update_data = product_in.dict(exclude_unset=True)
    
    # Update product attributes
    for field, value in update_data.items():
        setattr(product, field, value)
    
    db.add(product)
    await db.commit()
    await db.refresh(product)
    return product


@router.delete("/{product_id}", response_model=ProductSchema)
async def delete_product(
    product_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Delete a product (soft delete)"""
    query = select(Product).where(Product.id == product_id)
    result = await db.execute(query)
    product = result.scalars().first()
    
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    
    # Soft delete
    product.is_active = False
    db.add(product)
    await db.commit()
    await db.refresh(product)
    return product


# Inventory endpoints
@router.post("/{product_id}/inventory", response_model=InventorySchema)
async def create_inventory_item(
    product_id: int,
    inventory_in: InventoryCreate,
    db: AsyncSession = Depends(get_db)
):
    """Add inventory item to a product"""
    # Check if product exists
    product_query = select(Product).where(Product.id == product_id)
    product_result = await db.execute(product_query)
    product = product_result.scalars().first()
    
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    
    # Check if color exists if provided
    if inventory_in.color_id:
        color_query = select(Color).where(Color.id == inventory_in.color_id)
        color_result = await db.execute(color_query)
        color = color_result.scalars().first()
        
        if not color:
            raise HTTPException(status_code=404, detail=f"Color with id {inventory_in.color_id} not found")
    
    # Check if size exists if provided
    if inventory_in.size_id:
        size_query = select(Size).where(Size.id == inventory_in.size_id)
        size_result = await db.execute(size_query)
        size = size_result.scalars().first()
        
        if not size:
            raise HTTPException(status_code=404, detail=f"Size with id {inventory_in.size_id} not found")
    
    # Create inventory item
    inventory = Inventory(product_id=product_id, **inventory_in.dict())
    db.add(inventory)
    await db.commit()
    await db.refresh(inventory)
    
    # Update product stock status if necessary
    if inventory.amount > 0 and not product.in_stock:
        product.in_stock = True
        db.add(product)
        await db.commit()
    
    return inventory


@router.put("/inventory/{inventory_id}", response_model=InventorySchema)
async def update_inventory_item(
    inventory_id: int,
    inventory_in: InventoryUpdate,
    db: AsyncSession = Depends(get_db)
):
    """Update inventory item"""
    query = select(Inventory).where(Inventory.inventory_id == inventory_id)
    result = await db.execute(query)
    inventory = result.scalars().first()
    
    if not inventory:
        raise HTTPException(status_code=404, detail="Inventory item not found")
    
    update_data = inventory_in.dict(exclude_unset=True)
    
    # Update inventory attributes
    for field, value in update_data.items():
        setattr(inventory, field, value)
    
    db.add(inventory)
    await db.commit()
    await db.refresh(inventory)
    
    # Update product stock status if necessary
    if inventory.amount == 0:
        # Check if any inventory items still have stock
        product_id = inventory.product_id
        stock_query = select(Inventory).where(
            Inventory.product_id == product_id,
            Inventory.amount > 0
        )
        stock_result = await db.execute(stock_query)
        has_stock = stock_result.scalars().first() is not None
        
        # Update product stock status if needed
        product_query = select(Product).where(Product.id == product_id)
        product_result = await db.execute(product_query)
        product = product_result.scalars().first()
        
        if product and product.in_stock != has_stock:
            product.in_stock = has_stock
            db.add(product)
            await db.commit()
    
    return inventory


@router.delete("/inventory/{inventory_id}", response_model=InventorySchema)
async def delete_inventory_item(
    inventory_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Delete inventory item"""
    query = select(Inventory).where(Inventory.inventory_id == inventory_id)
    result = await db.execute(query)
    inventory = result.scalars().first()
    
    if not inventory:
        raise HTTPException(status_code=404, detail="Inventory item not found")
    
    product_id = inventory.product_id
    
    # Delete inventory item
    await db.delete(inventory)
    await db.commit()
    
    # Update product stock status if necessary
    stock_query = select(Inventory).where(
        Inventory.product_id == product_id,
        Inventory.amount > 0
    )
    stock_result = await db.execute(stock_query)
    has_stock = stock_result.scalars().first() is not None
    
    product_query = select(Product).where(Product.id == product_id)
    product_result = await db.execute(product_query)
    product = product_result.scalars().first()
    
    if product and product.in_stock != has_stock:
        product.in_stock = has_stock
        db.add(product)
        await db.commit()
    
    return inventory