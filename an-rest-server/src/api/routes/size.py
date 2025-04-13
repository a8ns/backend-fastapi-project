from fastapi import APIRouter, Depends, HTTPException, Query
from typing import List
from sqlalchemy.ext.asyncio import AsyncSession

from db.session import get_db
from crud.crud import crud_size
from schemas import (
    SizeSchema,
    SizeCreateSchema,
    SizeUpdateSchema
)

router = APIRouter()

@router.post("/", response_model=SizeSchema)
async def create_size(
    size_in: SizeCreateSchema,
    db: AsyncSession = Depends(get_db)
):
    """Create a new size"""
    return await crud_size.create(db, obj_in=size_in)

@router.get("/{size_id}", response_model=SizeSchema)
async def get_size(
    size_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Get a specific size by ID"""
    db_size = await crud_size.get(db, id=size_id)
    if not db_size:
        raise HTTPException(status_code=404, detail="Size not found")
    return db_size

@router.get("/", response_model=List[SizeSchema])
async def get_sizes(
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db)
):
    """Get multiple sizes with pagination"""
    return await crud_size.get_multi(db, skip=skip, limit=limit)

@router.put("/{size_id}", response_model=SizeSchema)
async def update_size(
    size_id: int,
    size_in: SizeUpdateSchema,
    db: AsyncSession = Depends(get_db)
):
    """Update a size"""
    db_size = await crud_size.get(db, id=size_id)
    if not db_size:
        raise HTTPException(status_code=404, detail="Size not found")
    return await crud_size.update(db, db_obj=db_size, obj_in=size_in)

@router.delete("/{size_id}", response_model=SizeSchema)
async def delete_size(
    size_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Delete a size"""
    db_size = await crud_size.get(db, id=size_id)
    if not db_size:
        raise HTTPException(status_code=404, detail="Size not found")
    return await crud_size.remove(db, id=size_id)