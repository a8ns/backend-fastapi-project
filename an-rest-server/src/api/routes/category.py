from fastapi import APIRouter, Depends, HTTPException, Query
from typing import List
from sqlalchemy.ext.asyncio import AsyncSession

from db.session import get_db
from crud.crud import crud_category
from schemas import (
    CategorySchema,
    CategoryCreateSchema,
    CategoryUpdateSchema
)

router = APIRouter()

@router.post("/", response_model=CategorySchema)
async def create_category(
    category_in: CategoryCreateSchema,
    db: AsyncSession = Depends(get_db)
):
    """Create a new category"""
    return await crud_category.create(db, obj_in=category_in)

@router.get("/{category_id}", response_model=CategorySchema)
async def get_category(
    category_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Get a specific category by ID"""
    db_category = await crud_category.get(db, id=category_id)
    if not db_category:
        raise HTTPException(status_code=404, detail="Category not found")
    return db_category

@router.get("/", response_model=List[CategorySchema])
async def get_categories(
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db)
):
    """Get multiple categories with pagination"""
    return await crud_category.get_multi(db, skip=skip, limit=limit)

@router.put("/{category_id}", response_model=CategorySchema)
async def update_category(
    category_id: int,
    category_in: CategoryUpdateSchema,
    db: AsyncSession = Depends(get_db)
):
    """Update a category"""
    db_category = await crud_category.get(db, id=category_id)
    if not db_category:
        raise HTTPException(status_code=404, detail="Category not found")
    return await crud_category.update(db, db_obj=db_category, obj_in=category_in)

@router.delete("/{category_id}", response_model=CategorySchema)
async def delete_category(
    category_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Delete a category"""
    db_category = await crud_category.get(db, id=category_id)
    if not db_category:
        raise HTTPException(status_code=404, detail="Category not found")
    return await crud_category.remove(db, id=category_id)