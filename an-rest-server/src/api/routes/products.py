from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from db.session import get_db
from models.product import Product, ProductMetadata
from models.shop import Shop
from schemas.product import (
    Product as ProductSchema,
    ProductCreate,
    ProductUpdate,
    ProductSimple,
    ProductMetadata as ProductMetadataSchema,
    ProductMetadataCreate,
    ProductMetadataUpdate,
    ProductWithMetadata,
    ProductWithShop
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
    category: Optional[str] = None,
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
    if category:
        query = query.where(Product.category == category)
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
    category: Optional[str] = None,
    min_price: Optional[float] = None,
    max_price: Optional[float] = None
):
    """Get products with shop information"""
    # First query products
    product_query = select(Product).where(Product.is_active == True)
    
    if category:
        product_query = product_query.where(Product.category == category)
    if min_price is not None:
        product_query = product_query.where(Product.price >= min_price)
    if max_price is not None:
        product_query = product_query.where(Product.price <= max_price)
    
    product_query = product_query.offset(skip).limit(limit)
    product_result = await db.execute(product_query)
    products = product_result.scalars().all()
    
    # Now enrich with shop data
    result = []
    for product in products:
        shop_query = select(Shop).where(Shop.id == product.shop_id)
        shop_result = await db.execute(shop_query)
        shop = shop_result.scalars().first()
        
        if shop:
            product_dict = ProductSchema.from_orm(product).dict()
            product_with_shop = ProductWithShop(**product_dict)
            product_with_shop.shop_name = shop.name
            product_with_shop.shop_city = shop.city
            result.append(product_with_shop)
    
    return result


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


# Product metadata endpoints
@router.post("/{product_id}/metadata", response_model=ProductMetadataSchema)
async def create_product_metadata(
    product_id: int,
    metadata: ProductMetadataCreate,
    db: AsyncSession = Depends(get_db)
):
    """Add metadata to a product"""
    # Check if product exists
    product_query = select(Product).where(Product.id == product_id)
    product_result = await db.execute(product_query)
    product = product_result.scalars().first()
    
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    
    # Check if metadata key already exists
    existing_query = select(ProductMetadata).where(
        ProductMetadata.product_id == product_id,
        ProductMetadata.key == metadata.key
    )
    existing_result = await db.execute(existing_query)
    existing = existing_result.scalars().first()
    
    if existing:
        raise HTTPException(status_code=400, detail=f"Metadata key '{metadata.key}' already exists")
    
    # Create metadata
    product_metadata = ProductMetadata(product_id=product_id, **metadata.dict())
    db.add(product_metadata)
    await db.commit()
    await db.refresh(product_metadata)
    return product_metadata


@router.get("/{product_id}/metadata", response_model=ProductWithMetadata)
async def get_product_with_metadata(
    product_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Get product with all metadata as key-value dictionary"""
    # Get product
    product_query = select(Product).where(Product.id == product_id)
    product_result = await db.execute(product_query)
    product = product_result.scalars().first()
    
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    
    # Get all metadata for product
    metadata_query = select(ProductMetadata).where(ProductMetadata.product_id == product_id)
    metadata_result = await db.execute(metadata_query)
    metadata_items = metadata_result.scalars().all()
    
    # Convert to dictionary
    metadata_dict = {item.key: item.value for item in metadata_items}
    
    # Combine product and metadata
    result = ProductWithMetadata.from_orm(product)
    result.metadata = metadata_dict
    
    return result


@router.put("/{product_id}/metadata/{key}", response_model=ProductMetadataSchema)
async def update_product_metadata(
    product_id: int,
    key: str,
    metadata: ProductMetadataUpdate,
    db: AsyncSession = Depends(get_db)
):
    """Update product metadata value"""
    # Check if metadata exists
    query = select(ProductMetadata).where(
        ProductMetadata.product_id == product_id,
        ProductMetadata.key == key
    )
    result = await db.execute(query)
    product_metadata = result.scalars().first()
    
    if not product_metadata:
        raise HTTPException(status_code=404, detail=f"Metadata key '{key}' not found")
    
    # Update value
    product_metadata.value = metadata.value
    db.add(product_metadata)
    await db.commit()
    await db.refresh(product_metadata)
    return product_metadata


@router.delete("/{product_id}/metadata/{key}", response_model=ProductMetadataSchema)
async def delete_product_metadata(
    product_id: int,
    key: str,
    db: AsyncSession = Depends(get_db)
):
    """Delete product metadata"""
    # Check if metadata exists
    query = select(ProductMetadata).where(
        ProductMetadata.product_id == product_id,
        ProductMetadata.key == key
    )
    result = await db.execute(query)
    product_metadata = result.scalars().first()
    
    if not product_metadata:
        raise HTTPException(status_code=404, detail=f"Metadata key '{key}' not found")
    
    # Delete metadata
    await db.delete(product_metadata)
    await db.commit()
    return product_metadata