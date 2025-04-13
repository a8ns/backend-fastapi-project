from fastapi import APIRouter, Depends, HTTPException, Query
from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID

from db.session import get_db
from crud.crud import crud_product
from schemas import (
    ProductSchema,
    ProductCreateSchema,
    ProductUpdateSchema
)

router = APIRouter()

@router.post("/", response_model=ProductSchema)
async def create_product(
    product_in: ProductCreateSchema,
    db: AsyncSession = Depends(get_db)
):
    """Create a new product"""
    return await crud_product.create(db, obj_in=product_in)

@router.get("/{product_id}", response_model=ProductSchema)
async def get_product(
    product_id: UUID,
    db: AsyncSession = Depends(get_db)
):
    """Get a specific product by ID"""
    db_product = await crud_product.get(db, id=product_id)
    if not db_product:
        raise HTTPException(status_code=404, detail="Product not found")
    return db_product

@router.get("/", response_model=List[ProductSchema])
async def get_products(
    skip: int = 0,
    limit: int = 100,
    shop_id: Optional[UUID] = None,
    category_id: Optional[int] = None,
    db: AsyncSession = Depends(get_db)
):
    """Get multiple products with optional filtering"""
    filters = {}
    if shop_id:
        filters["shop_id"] = shop_id
    if category_id:
        filters["category_id"] = category_id
        
    return await crud_product.get_multi(
        db, skip=skip, limit=limit, filters=filters
    )

@router.put("/{product_id}", response_model=ProductSchema)
async def update_product(
    product_id: UUID,
    product_in: ProductUpdateSchema,
    db: AsyncSession = Depends(get_db)
):
    """Update a product"""
    db_product = await crud_product.get(db, id=product_id)
    if not db_product:
        raise HTTPException(status_code=404, detail="Product not found")
    return await crud_product.update(db, db_obj=db_product, obj_in=product_in)

@router.delete("/{product_id}", response_model=ProductSchema)
async def delete_product(
    product_id: UUID,
    db: AsyncSession = Depends(get_db)
):
    """Delete a product"""
    db_product = await crud_product.get(db, id=product_id)
    if not db_product:
        raise HTTPException(status_code=404, detail="Product not found")
    return await crud_product.remove(db, id=product_id)