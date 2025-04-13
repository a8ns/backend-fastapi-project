from fastapi import APIRouter, Depends, HTTPException, Query
from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID

from db.session import get_db
from crud.crud import crud_inventory
from schemas import (
    InventorySchema,
    InventoryCreateSchema,
    InventoryUpdateSchema
)

router = APIRouter()

@router.post("/", response_model=InventorySchema)
async def create_inventory(
    inventory_in: InventoryCreateSchema,
    db: AsyncSession = Depends(get_db)
):
    """Create a new inventory item"""
    return await crud_inventory.create(db, obj_in=inventory_in)

@router.get("/{inventory_id}", response_model=InventorySchema)
async def get_inventory(
    inventory_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Get a specific inventory item by ID"""
    db_inventory = await crud_inventory.get(db, id=inventory_id)
    if not db_inventory:
        raise HTTPException(status_code=404, detail="Inventory item not found")
    return db_inventory

@router.get("/", response_model=List[InventorySchema])
async def get_inventories(
    skip: int = 0,
    limit: int = 100,
    product_id: Optional[UUID] = None,
    color_id: Optional[int] = None,
    size_id: Optional[int] = None,
    db: AsyncSession = Depends(get_db)
):
    """Get multiple inventory items with optional filtering"""
    filters = {}
    if product_id:
        filters["product_id"] = product_id
    if color_id:
        filters["color_id"] = color_id
    if size_id:
        filters["size_id"] = size_id
        
    return await crud_inventory.get_multi(
        db, skip=skip, limit=limit, filters=filters
    )

@router.put("/{inventory_id}", response_model=InventorySchema)
async def update_inventory(
    inventory_id: int,
    inventory_in: InventoryUpdateSchema,
    db: AsyncSession = Depends(get_db)
):
    """Update an inventory item"""
    db_inventory = await crud_inventory.get(db, id=inventory_id)
    if not db_inventory:
        raise HTTPException(status_code=404, detail="Inventory item not found")
    return await crud_inventory.update(db, db_obj=db_inventory, obj_in=inventory_in)

@router.delete("/{inventory_id}", response_model=InventorySchema)
async def delete_inventory(
    inventory_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Delete an inventory item"""
    db_inventory = await crud_inventory.get(db, id=inventory_id)
    if not db_inventory:
        raise HTTPException(status_code=404, detail="Inventory item not found")
    return await crud_inventory.remove(db, id=inventory_id)