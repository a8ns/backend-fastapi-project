from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from sqlalchemy.orm import joinedload
from geoalchemy2 import Geography
from geoalchemy2.functions import ST_DWithin, ST_Point, ST_AsText, ST_SetSRID, ST_MakePoint

from db.session import get_db
from models.shop import Shop
from models.product import Product
from schemas.shop import (
    Shop as ShopSchema,
    ShopCreate,
    ShopUpdate,
    ShopWithProducts,
    NearbyShopParams
)
from schemas.base import ProductSimpleBase

router = APIRouter()


@router.post("/", response_model=ShopSchema)
async def create_shop(
    shop_in: ShopCreate,
    db: AsyncSession = Depends(get_db)
):
    """Create a new shop"""
    shop = Shop(**shop_in.dict())
    db.add(shop)
    await db.commit()
    await db.refresh(shop)
    return shop


@router.get("/", response_model=List[ShopSchema])
async def read_shops(
    db: AsyncSession = Depends(get_db),
    skip: int = 0,
    limit: int = 100,
    name: Optional[str] = None,
    city: Optional[str] = None,
    country: Optional[str] = None,
    category: Optional[str] = None,
    is_active: bool = True
):
    """List shops with optional filtering"""
    query = select(Shop).where(Shop.is_active == is_active)
    
    if name:
        query = query.where(Shop.name.ilike(f"%{name}%"))
    if city:
        query = query.where(Shop.city.ilike(f"%{city}%"))
    if country:
        query = query.where(Shop.country.ilike(f"%{country}%"))
    if category:
        query = query.where(Shop.category == category)
    
    query = query.offset(skip).limit(limit)
    result = await db.execute(query)
    return result.scalars().all()


@router.get("/with-products", response_model=List[ShopWithProducts])
async def read_shops_with_products(
    db: AsyncSession = Depends(get_db),
    skip: int = 0,
    limit: int = 100,
    is_active: bool = True
):
    """Get shops with their products"""
    query = select(Shop).options(
        joinedload(Shop.products)
    ).where(Shop.is_active == is_active)
    
    query = query.offset(skip).limit(limit)
    result = await db.execute(query)
    shops = result.scalars().all()
    
    # Format response
    shop_list = []
    for shop in shops:
        shop_dict = ShopSchema.from_orm(shop).dict()
        shop_with_products = ShopWithProducts(**shop_dict)
        
        # Convert products to ProductSimpleBase
        products_simple = []
        for product in shop.products:
            if product.is_active:
                product_simple = ProductSimpleBase(
                    id=product.id,
                    title=product.title,
                    price=product.price,
                    image_url=product.image_url
                )
                products_simple.append(product_simple)
        
        shop_with_products.products = products_simple
        shop_list.append(shop_with_products)
    
    return shop_list


@router.get("/nearby", response_model=List[ShopSchema])
async def get_nearby_shops(
    params: NearbyShopParams = Depends(),
    db: AsyncSession = Depends(get_db)
):
    """Get shops within a specified radius from a location"""
    # Create a point from the provided coordinates
    point = ST_Point(params.longitude, params.latitude, srid=4326)
    
    # Query shops within the radius
    query = select(Shop).where(
        Shop.is_active == True,
        ST_DWithin(
            func.cast(
                ST_SetSRID(
                    ST_MakePoint(Shop.longitude, Shop.latitude), 
                    4326
                ),
                Geography
            ),
            func.cast(
                ST_SetSRID(point, 4326),
                Geography
            ),
            params.radius
        )
    ).limit(params.limit)
    
    result = await db.execute(query)
    return result.scalars().all()


@router.get("/{shop_id}", response_model=ShopSchema)
async def read_shop(
    shop_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Get shop details"""
    query = select(Shop).where(Shop.id == shop_id)
    result = await db.execute(query)
    shop = result.scalars().first()
    
    if not shop:
        raise HTTPException(status_code=404, detail="Shop not found")
    
    return shop


@router.get("/{shop_id}/products", response_model=ShopWithProducts)
async def read_shop_products(
    shop_id: int,
    db: AsyncSession = Depends(get_db),
    in_stock: Optional[bool] = None
):
    """Get shop with all its products"""
    # Get shop
    shop_query = select(Shop).where(Shop.id == shop_id)
    shop_result = await db.execute(shop_query)
    shop = shop_result.scalars().first()
    
    if not shop:
        raise HTTPException(status_code=404, detail="Shop not found")
    
    # Query products
    product_query = select(Product).where(
        Product.shop_id == shop_id,
        Product.is_active == True
    )
    
    if in_stock is not None:
        product_query = product_query.where(Product.in_stock == in_stock)
    
    product_result = await db.execute(product_query)
    products = product_result.scalars().all()
    
    # Format response
    shop_dict = ShopSchema.from_orm(shop).dict()
    shop_with_products = ShopWithProducts(**shop_dict)
    
    # Convert products to ProductSimpleBase
    products_simple = []
    for product in products:
        product_simple = ProductSimpleBase(
            id=product.id,
            title=product.title,
            price=product.price,
            image_url=product.image_url
        )
        products_simple.append(product_simple)
    
    shop_with_products.products = products_simple
    return shop_with_products


@router.put("/{shop_id}", response_model=ShopSchema)
async def update_shop(
    shop_id: int,
    shop_in: ShopUpdate,
    db: AsyncSession = Depends(get_db)
):
    """Update shop details"""
    query = select(Shop).where(Shop.id == shop_id)
    result = await db.execute(query)
    shop = result.scalars().first()
    
    if not shop:
        raise HTTPException(status_code=404, detail="Shop not found")
    
    update_data = shop_in.dict(exclude_unset=True)
    
    # Update shop attributes
    for field, value in update_data.items():
        setattr(shop, field, value)
    
    db.add(shop)
    await db.commit()
    await db.refresh(shop)
    return shop


@router.delete("/{shop_id}", response_model=ShopSchema)
async def delete_shop(
    shop_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Delete a shop (soft delete)"""
    query = select(Shop).where(Shop.id == shop_id)
    result = await db.execute(query)
    shop = result.scalars().first()
    
    if not shop:
        raise HTTPException(status_code=404, detail="Shop not found")
    
    # Soft delete
    shop.is_active = False
    db.add(shop)
    await db.commit()
    await db.refresh(shop)
    return shop