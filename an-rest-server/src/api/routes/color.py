from fastapi import APIRouter, Depends, HTTPException, Query
from typing import List
from sqlalchemy.ext.asyncio import AsyncSession

from db.session import get_db
from crud.crud import crud_color
from schemas import (
    ColorSchema,
    ColorCreateSchema,
    ColorUpdateSchema
)

router = APIRouter()

@router.post("/", response_model=ColorSchema)
async def create_color(
    color_in: ColorCreateSchema,
    db: AsyncSession = Depends(get_db)
):
    """Create a new color"""
    return await crud_color.create(db, obj_in=color_in)

@router.get("/{color_id}", response_model=ColorSchema)
async def get_color(
    color_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Get a specific color by ID"""
    db_color = await crud_color.get(db, id=color_id)
    if not db_color:
        raise HTTPException(status_code=404, detail="Color not found")
    return db_color

@router.get("/", response_model=List[ColorSchema])
async def get_colors(
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db)
):
    """Get multiple colors with pagination"""
    return await crud_color.get_multi(db, skip=skip, limit=limit)

@router.put("/{color_id}", response_model=ColorSchema)
async def update_color(
    color_id: int,
    color_in: ColorUpdateSchema,
    db: AsyncSession = Depends(get_db)
):
    """Update a color"""
    db_color = await crud_color.get(db, id=color_id)
    if not db_color:
        raise HTTPException(status_code=404, detail="Color not found")
    return await crud_color.update(db, db_obj=db_color, obj_in=color_in)

@router.delete("/{color_id}", response_model=ColorSchema)
async def delete_color(
    color_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Delete a color"""
    db_color = await crud_color.get(db, id=color_id)
    if not db_color:
        raise HTTPException(status_code=404, detail="Color not found")
    return await crud_color.remove(db, id=color_id)