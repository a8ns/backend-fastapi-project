from fastapi import APIRouter, Depends, HTTPException, Query
from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID

from db.session import get_db
from crud.crud import crud_shop, crud_product
from schemas import (
    ShopSchema,
    ShopCreateSchema,
    ShopUpdateSchema,
    ShopProductsSchema,
    ProductWithVariationsSchema
)

router = APIRouter()

@router.post("/", response_model=ShopSchema)
async def create_shop(
    shop_in: ShopCreateSchema,
    db: AsyncSession = Depends(get_db)
):
    """Create a new shop"""
    return await crud_shop.create(db, obj_in=shop_in)

@router.get("/{shop_id}", response_model=ShopSchema)
async def get_shop(
    shop_id: UUID,
    db: AsyncSession = Depends(get_db)
):
    """Get a specific shop by ID"""
    db_shop = await crud_shop.get(db, id=shop_id)
    if not db_shop:
        raise HTTPException(status_code=404, detail="Shop not found")
    return db_shop


@router.get("/{shop_id}/products", response_model=ShopProductsSchema)
async def get_shop_products(
    shop_id: UUID,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: AsyncSession = Depends(get_db)
):
    """Get all products for a specific shop"""
    # First check if the shop exists
    db_shop = await crud_shop.get(db, id=shop_id)
    if not db_shop:
        raise HTTPException(status_code=404, detail="Shop not found")
    
    # Get products for this shop
    products = await crud_product.get_products_by_shop(
        db_session=db, 
        shop_id=shop_id,
        skip=skip,
        limit=limit
    )
    
    # Get total count for pagination
    total_products = await crud_product.count_products_by_shop(
        db_session=db,
        shop_id=shop_id
    )
    
    return ShopProductsSchema(
        shop_id=shop_id,
        total_products=total_products,
        products=products
    )

@router.get("/{shop_id}/products/with_variations", response_model=List[ProductWithVariationsSchema])
async def get_shop_products_with_variations(
    shop_id: UUID,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: AsyncSession = Depends(get_db)
):
    """Get all products for a specific shop with their variations"""
    # First check if the shop exists
    db_shop = await crud_shop.get(db, id=shop_id)
    if not db_shop:
        raise HTTPException(status_code=404, detail="Shop not found")
    
    # Get products for this shop
    products = await crud_product.get_products_by_shop(
        db_session=db, 
        shop_id=shop_id,
        skip=skip,
        limit=limit
    )
    
    # Get variations for each product
    products_with_variations = []
    for product in products:
        product_with_variations = await crud_product.get_with_variations(db, product.id)
        if product_with_variations:
            products_with_variations.append(product_with_variations)
    
    return products_with_variations

@router.get("/", response_model=List[ShopSchema])
async def get_shops(
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db)
):
    """Get multiple shops with pagination"""
    return await crud_shop.get_multi(db, skip=skip, limit=limit)

@router.put("/{shop_id}", response_model=ShopSchema)
async def update_shop(
    shop_id: UUID,
    shop_in: ShopUpdateSchema,
    db: AsyncSession = Depends(get_db)
):
    """Update a shop"""
    db_shop = await crud_shop.get(db, id=shop_id)
    if not db_shop:
        raise HTTPException(status_code=404, detail="Shop not found")
    return await crud_shop.update(db, db_obj=db_shop, obj_in=shop_in)

@router.delete("/{shop_id}", response_model=ShopSchema)
async def delete_shop(
    shop_id: UUID,
    db: AsyncSession = Depends(get_db)
):
    """Delete a shop"""
    db_shop = await crud_shop.get(db, id=shop_id)
    if not db_shop:
        raise HTTPException(status_code=404, detail="Shop not found")
    return await crud_shop.remove(db, id=shop_id)