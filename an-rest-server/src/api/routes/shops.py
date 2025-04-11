from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from geoalchemy2.functions import ST_DWithin, ST_MakePoint
from geoalchemy2.elements import WKTElement

from db.session import get_db
from models.shop import Shop, ShopMetadata
from models.product import Product
from schemas.shop import (
    Shop as ShopSchema,
    ShopCreate,
    ShopUpdate,
    ShopWithProducts,
    ShopMetadata as ShopMetadataSchema,
    ShopMetadataCreate,
    ShopMetadataUpdate,
    ShopWithMetadata,
    NearbyShopParams
)
from schemas.product import ProductSimple

router = APIRouter()


@router.post("/", response_model=ShopSchema)
async def create_shop(
    shop_in: ShopCreate,
    db: AsyncSession = Depends(get_db)
):
    """Create a new shop"""
    # Create shop object
    shop = Shop(**shop_in.dict())
    
    # Create point geometry for location
    point_wkt = f'POINT({shop.longitude} {shop.latitude})'
    shop.location = WKTElement(point_wkt, srid=4326)
    
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
    category: Optional[str] = None,
    is_active: bool = True
):
    """List shops with optional filtering"""
    query = select(Shop).where(Shop.is_active == is_active)
    
    if name:
        query = query.where(Shop.name.ilike(f"%{name}%"))
    if city:
        query = query.where(Shop.city.ilike(f"%{city}%"))
    if category:
        query = query.where(Shop.category == category)
    
    query = query.offset(skip).limit(limit)
    result = await db.execute(query)
    return result.scalars().all()


@router.get("/nearby", response_model=List[ShopSchema])
async def get_nearby_shops(
    params: NearbyShopParams = Depends(),
    db: AsyncSession = Depends(get_db)
):
    """Find shops within specified radius from given coordinates"""
    # Create a point from the provided coordinates
    point = WKTElement(f'POINT({params.longitude} {params.latitude})', srid=4326)
    
    # Query for shops within the radius
    query = select(Shop).where(
        Shop.is_active == True,
        ST_DWithin(
            Shop.location, 
            point,
            params.radius  # Distance in meters
        )
    ).limit(params.limit)
    
    result = await db.execute(query)
    return result.scalars().all()


@router.get("/{shop_id}", response_model=ShopWithProducts)
async def read_shop(
    shop_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Get detailed shop information with its products"""
    # Get shop
    query = select(Shop).where(Shop.id == shop_id)
    result = await db.execute(query)
    shop = result.scalars().first()
    
    if not shop:
        raise HTTPException(status_code=404, detail="Shop not found")
    
    # Get shop's products
    products_query = select(Product).where(
        Product.shop_id == shop_id,
        Product.is_active == True
    )
    products_result = await db.execute(products_query)
    products = products_result.scalars().all()
    
    # Convert to ShopWithProducts
    shop_dict = ShopSchema.from_orm(shop).dict()
    shop_with_products = ShopWithProducts(**shop_dict)
    shop_with_products.products = [ProductSimple.from_orm(p) for p in products]
    
    return shop_with_products


@router.put("/{shop_id}", response_model=ShopSchema)
async def update_shop(
    shop_id: int,
    shop_in: ShopUpdate,
    db: AsyncSession = Depends(get_db)
):
    """Update a shop"""
    # Get shop
    query = select(Shop).where(Shop.id == shop_id)
    result = await db.execute(query)
    shop = result.scalars().first()
    
    if not shop:
        raise HTTPException(status_code=404, detail="Shop not found")
    
    update_data = shop_in.dict(exclude_unset=True)
    
    # Update location if coordinates are provided
    if "latitude" in update_data or "longitude" in update_data:
        # Use either the new values or existing ones
        lat = update_data.get("latitude", shop.latitude)
        lng = update_data.get("longitude", shop.longitude)
        point_wkt = f'POINT({lng} {lat})'
        update_data["location"] = WKTElement(point_wkt, srid=4326)
    
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
    # Get shop
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


# Shop metadata endpoints
@router.post("/{shop_id}/metadata", response_model=ShopMetadataSchema)
async def create_shop_metadata(
    shop_id: int,
    metadata: ShopMetadataCreate,
    db: AsyncSession = Depends(get_db)
):
    """Add metadata to a shop"""
    # Check if shop exists
    shop_query = select(Shop).where(Shop.id == shop_id)
    shop_result = await db.execute(shop_query)
    shop = shop_result.scalars().first()
    
    if not shop:
        raise HTTPException(status_code=404, detail="Shop not found")
    
    # Check if metadata key already exists
    existing_query = select(ShopMetadata).where(
        ShopMetadata.shop_id == shop_id,
        ShopMetadata.key == metadata.key
    )
    existing_result = await db.execute(existing_query)
    existing = existing_result.scalars().first()
    
    if existing:
        raise HTTPException(status_code=400, detail=f"Metadata key '{metadata.key}' already exists")
    
    # Create metadata
    shop_metadata = ShopMetadata(shop_id=shop_id, **metadata.dict())
    db.add(shop_metadata)
    await db.commit()
    await db.refresh(shop_metadata)
    return shop_metadata


@router.get("/{shop_id}/metadata", response_model=ShopWithMetadata)
async def get_shop_with_metadata(
    shop_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Get shop with all metadata as key-value dictionary"""
    # Get shop
    shop_query = select(Shop).where(Shop.id == shop_id)
    shop_result = await db.execute(shop_query)
    shop = shop_result.scalars().first()
    
    if not shop:
        raise HTTPException(status_code=404, detail="Shop not found")
    
    # Get all metadata for shop
    metadata_query = select(ShopMetadata).where(ShopMetadata.shop_id == shop_id)
    metadata_result = await db.execute(metadata_query)
    metadata_items = metadata_result.scalars().all()
    
    # Convert to dictionary
    metadata_dict = {item.key: item.value for item in metadata_items}
    
    # Combine shop and metadata
    result = ShopWithMetadata.from_orm(shop)
    result.metadata = metadata_dict
    
    return result


@router.put("/{shop_id}/metadata/{key}", response_model=ShopMetadataSchema)
async def update_shop_metadata(
    shop_id: int,
    key: str,
    metadata: ShopMetadataUpdate,
    db: AsyncSession = Depends(get_db)
):
    """Update shop metadata value"""
    # Check if metadata exists
    query = select(ShopMetadata).where(
        ShopMetadata.shop_id == shop_id,
        ShopMetadata.key == key
    )
    result = await db.execute(query)
    shop_metadata = result.scalars().first()
    
    if not shop_metadata:
        raise HTTPException(status_code=404, detail=f"Metadata key '{key}' not found")
    
    # Update value
    shop_metadata.value = metadata.value
    db.add(shop_metadata)
    await db.commit()
    await db.refresh(shop_metadata)
    return shop_metadata


@router.delete("/{shop_id}/metadata/{key}", response_model=ShopMetadataSchema)
async def delete_shop_metadata(
    shop_id: int,
    key: str,
    db: AsyncSession = Depends(get_db)
):
    """Delete shop metadata"""
    # Check if metadata exists
    query = select(ShopMetadata).where(
        ShopMetadata.shop_id == shop_id,
        ShopMetadata.key == key
    )
    result = await db.execute(query)
    shop_metadata = result.scalars().first()
    
    if not shop_metadata:
        raise HTTPException(status_code=404, detail=f"Metadata key '{key}' not found")
    
    # Delete metadata
    await db.delete(shop_metadata)
    await db.commit()
    return shop_metadata