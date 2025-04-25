from fastapi import APIRouter, Depends, Query, HTTPException, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import sessionmaker 
from sqlalchemy import func, select
from db.session import AsyncSessionLocal

from typing import List, Optional, Dict, Any
import time
from core.logging import logger

from db.session import get_db
from api.search_modules import SearchConfig
from crud.crud_search import (
    crud_product_search, 
    crud_category_search,
    enable_vector_search
)
from schemas import (
    ProductSearchResult,
    CategorySearchResult,
    SearchResponse,
    VectorSearchConfig,
    BackfillStatus
)

# Initialize router
router = APIRouter(prefix="/search", tags=["search"])

async def get_records_without_embeddings_count(db: AsyncSession) -> int:
    from sqlalchemy import select, func
    from models import Product
    """Get count of products without embeddings."""
    query = select(func.count()).select_from(Product).filter(Product.embedding.is_(None))
    result = await db.execute(query)
    count = result.scalar_one()
    
    logger.info(f"{count} products without embeddings ...")
    return count

async def process_embeddings_batch(sessionmaker, batch_size: int):
    """Background task to process a batch of embeddings"""
    from api.search_modules import VectorSearchStrategy
    from models import Product  # Import the Product model here
    from sqlalchemy import update
    
    logger.info(f"Starting embedding batch process with batch size {batch_size}")
    
    # Get products without embeddings - using a dedicated session
    async with sessionmaker() as fetch_db:
        try:
            # Get product IDs only - to avoid session issues
            products = await crud_product_search.get_records_without_embeddings(fetch_db, batch_size)
            product_ids = [str(product.id) for product in products]
            logger.debug(f"Retrieved {len(product_ids)} product IDs for processing...")
            
            if not product_ids:
                logger.info("No products found without embeddings")
                return
        except Exception as e:
            logger.error(f"Error fetching products to process: {str(e)}")
            return
    
    # Create vector strategy for generating embeddings
    vector_strategy = VectorSearchStrategy(crud_product_search.model)
    
    processed_count = 0
    error_count = 0
    
    # Process each product ID
    for product_id in product_ids:
        # Use a completely fresh session for each product to avoid any potential issues
        try:
            # First session to get product data
            async with sessionmaker() as read_db:
                # Get product data needed for embedding
                product = await read_db.get(Product, product_id)
                if not product:
                    logger.warning(f"Product {product_id} not found in fresh session, skipping")
                    continue
                
                # Skip if it already has an embedding (race condition check)
                if product.embedding is not None:
                    logger.info(f"Product {product_id} already has embedding, skipping")
                    continue
                
                # Generate text for embedding - keeping it outside the session
                text = await crud_product_search.generate_product_embedding_text(product)
            
            # Generate embedding - completely outside any session
            embedding = await vector_strategy.generate_embedding(text)
            
            # Now use a third session just for the update
            async with sessionmaker() as update_db:
                # Use SQLAlchemy Core update instead of ORM to avoid sync/async issues
                stmt = (
                    update(Product)
                    .where(Product.id == product_id)
                    .values(embedding=embedding)
                )
                
                await update_db.execute(stmt)
                await update_db.commit()
                
                processed_count += 1
                logger.info(f"Updated embedding for product {product_id}")
                
        except Exception as e:
            error_count += 1
            logger.error(f"Error generating embedding for product {product_id}: {str(e)}")
            continue
            
            logger.info(f"Completed embedding generation batch: {processed_count} processed, {error_count} errors")
            
            # Get updated count of remaining products
            async with sessionmaker() as final_db:
                remaining = await get_records_without_embeddings_count(final_db)
                logger.info(f"Remaining products without embeddings: {remaining}")
                
                # If there are more products to process, start another batch
                if remaining > 0:
                    logger.info(f"Starting another batch for {min(remaining, batch_size)} products")
                    # Create a new background task here if needed
                    # Note: You'll need to integrate this with your task queue system
            
        except Exception as e:
            logger.error(f"Error in batch embedding process: {str(e)}")
            raise

@router.get("/products", response_model=SearchResponse)
async def search_products(
    q: str = Query(..., description="Search query"),
    method: str = Query("text", description="Search method: text, vector, or hybrid"),
    category_id: Optional[int] = Query(None, description="Filter by category ID"),
    brand: Optional[str] = Query(None, description="Filter by brand"),
    min_price: Optional[float] = Query(None, description="Minimum price"),
    max_price: Optional[float] = Query(None, description="Maximum price"),
    limit: int = Query(20, description="Maximum number of results"),
    db: AsyncSession = Depends(get_db)
):
    """
    Search products using text search, vector search, or a hybrid approach.
    Falls back to text search if vector/hybrid search fails.
    """
    try:
        start_time = time.time()
        
        # Validate search method
        if method not in ["text", "vector", "hybrid"]:
            raise HTTPException(status_code=400, detail=f"Invalid search method: {method}")
            
        # Check if vector/hybrid search is enabled when requested
        if (method in ["vector", "hybrid"]) and not SearchConfig.VECTOR_SEARCH_ENABLED:
            logger.warning(f"{method} search requested but not enabled, falling back to text search")
            method = "text"
        
        # Execute search
        results = await crud_product_search.search_products(
            db=db,
            query=q,
            method=method,
            category_id=category_id,
            brand=brand,
            min_price=min_price,
            max_price=max_price,
            limit=limit
        )
        
        # Calculate execution time
        execution_time_ms = (time.time() - start_time) * 1000
        
        # Get total count (could be optimized with a separate count query)
        total = len(results)
        
        return SearchResponse(
            results=results,
            total=total,
            query=q,
            method=method,
            execution_time_ms=execution_time_ms
        )
    
    except Exception as e:
        logger.error(f"Error in product search: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Search error: {str(e)}")


@router.get("/categories", response_model=SearchResponse)
async def search_categories(
    q: str = Query(..., description="Search query"),
    method: str = Query("text", description="Search method: text, vector, or hybrid"),
    limit: int = Query(20, description="Maximum number of results"),
    db: AsyncSession = Depends(get_db)
):
    """
    Search categories using text search, vector search, or a hybrid approach.
    Falls back to text search if vector/hybrid search fails.
    """
    try:
        start_time = time.time()
        
        # Validate search method
        if method not in ["text", "vector", "hybrid"]:
            raise HTTPException(status_code=400, detail=f"Invalid search method: {method}")
            
        # Check if vector/hybrid search is enabled when requested
        if (method in ["vector", "hybrid"]) and not SearchConfig.VECTOR_SEARCH_ENABLED:
            logger.warning(f"{method} search requested but not enabled, falling back to text search")
            method = "text"
        
        # Execute search
        results = await crud_category_search.search_categories(
            db=db,
            query=q,
            method=method,
            limit=limit
        )
        
        # Calculate execution time
        execution_time_ms = (time.time() - start_time) * 1000
        
        # Get total count
        total = len(results)
        
        return SearchResponse(
            results=results,
            total=total,
            query=q,
            method=method,
            execution_time_ms=execution_time_ms
        )
    
    except Exception as e:
        logger.error(f"Error in category search: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Search error: {str(e)}")


@router.post("/admin/enable-vector-search")
async def admin_enable_vector_search(
    config: VectorSearchConfig
):
    """
    Enable vector search functionality.
    This should be an admin-only endpoint with proper authentication.
    """
    try:
        result = await enable_vector_search(config.api_key)
        
        # Update config if needed
        if config.embedding_model:
            SearchConfig.EMBEDDING_MODEL = config.embedding_model
        if config.dimensions:
            SearchConfig.EMBEDDING_DIMENSIONS = config.dimensions
            
        return {
            "status": "success",
            "enabled": True,
            "has_api_key": bool(SearchConfig.OPENAI_API_KEY),
            "embedding_model": SearchConfig.EMBEDDING_MODEL,
            "dimensions": SearchConfig.EMBEDDING_DIMENSIONS
        }
    except Exception as e:
        logger.error(f"Error enabling vector search: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Configuration error: {str(e)}")


@router.post("/admin/backfill-embeddings", response_model=BackfillStatus)
async def admin_backfill_embeddings(
    background_tasks: BackgroundTasks,
    batch_size: int = Query(50, description="Number of products to process per batch"),
    db: AsyncSession = Depends(get_db)
):
    """
    Backfill embeddings for products without them.
    This should be an admin-only endpoint with proper authentication.
    """
    if not SearchConfig.VECTOR_SEARCH_ENABLED:
        raise HTTPException(status_code=400, detail="Vector search not enabled")
    
    if not SearchConfig.OPENAI_API_KEY:
        raise HTTPException(status_code=400, detail="OpenAI API key not configured")
    
    # Get count of remaining products without embeddings
    remaining_count = await get_records_without_embeddings_count(db)
    logger.info(f"Records without embeddings: {remaining_count}")    
    
    # Start background task for backfilling
    if remaining_count == 0:
        return BackfillStatus(
            status="nothing to backfill",
            processed=0,
            total_remaining=remaining_count
        )
        
    # Add task to background queue
    background_tasks.add_task(
        process_embeddings_batch,
        AsyncSessionLocal,
        batch_size
    )
    
    logger.info("Background tasks started")
    return BackfillStatus(
        status="started",
        processed=0,
        total_remaining=remaining_count
    )

@router.get("/admin/embedding-status", response_model=BackfillStatus)
async def get_embedding_status(
    db: AsyncSession = Depends(get_db)
):
    """
    Get the current status of embedding generation.
    """
    if not SearchConfig.VECTOR_SEARCH_ENABLED:
        return BackfillStatus(
            status="disabled",
            processed=0,
            total_remaining=0
        )
    
    # Get count of remaining products without embeddings
    remaining_count = await get_records_without_embeddings_count(db)
    
    # Get total count of products
    total_count = await crud_product_search.count(db)
    
    return BackfillStatus(
        status="in_progress" if remaining_count > 0 else "completed",
        processed=total_count - remaining_count,
        total_remaining=remaining_count
    )




