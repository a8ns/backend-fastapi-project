from typing import Type, TypeVar, Generic, Optional, List, Union, Dict, Any, Tuple
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, text
from models.base_model import BaseModel
from models.product import Product, Category
from schemas.search import ProductSearchResult, CategorySearchResult
from crud.crud_base import CRUDBase
from api.search_modules import (
    SearchConfig, 
    TextSearchStrategy, 
    VectorSearchStrategy, 
    HybridSearchStrategy
)
from core.logging import logger

ModelType = TypeVar("ModelType", bound=BaseModel)



class SearchableCRUD(CRUDBase[ModelType, Any, Any]):
    """Base CRUD class with search capabilities"""
    
    def __init__(
        self, 
        model: Type[ModelType],
        search_vector_field: str = 'search_vector',
        embedding_field: str = 'embedding'
    ):
        super().__init__(model)
        self.search_vector_field = search_vector_field
        self.embedding_field = embedding_field
    
    async def text_search(
        self,
        db: AsyncSession,
        query: str,
        result_type: Any,
        filters: Optional[Dict[str, Any]] = None,
        range_filters: Optional[Dict[str, Dict[str, Any]]] = None,
        limit: int = 20
    ) -> List[Any]:
        """Perform text-based search"""
        strategy = TextSearchStrategy(self.model, self.search_vector_field, result_type)
        return await strategy.search(db, query, filters, range_filters, limit)
    
    async def vector_search(
        self,
        db: AsyncSession,
        query: str,
        result_type: Any,
        filters: Optional[Dict[str, Any]] = None,
        range_filters: Optional[Dict[str, Dict[str, Any]]] = None,
        limit: int = 20
    ) -> List[Any]:
        """Perform vector-based semantic search"""
        if not SearchConfig.VECTOR_SEARCH_ENABLED:
            raise ValueError("Vector search is not enabled")
            
        strategy = VectorSearchStrategy(self.model, self.embedding_field, result_type)
        return await strategy.search(db, query, filters, range_filters, limit)
    
    async def hybrid_search(
        self,
        db: AsyncSession,
        query: str,
        result_type: Any,
        filters: Optional[Dict[str, Any]] = None,
        range_filters: Optional[Dict[str, Dict[str, Any]]] = None,
        limit: int = 20,
        text_weight: float = 0.4,
        vector_weight: float = 0.6
    ) -> List[Any]:
        """Perform hybrid search (text + vector)"""
        strategy = HybridSearchStrategy(
            self.model, 
            self.search_vector_field, 
            self.embedding_field, 
            result_type,
            text_weight,
            vector_weight
        )
        return await strategy.search(db, query, filters, range_filters, limit)
    
    async def search(
        self,
        db: AsyncSession,
        query: str,
        result_type: Any,
        method: str = "text",
        filters: Optional[Dict[str, Any]] = None,
        range_filters: Optional[Dict[str, Dict[str, Any]]] = None,
        limit: int = 20
    ) -> List[Any]:
        """
        Unified search method that delegates to the appropriate strategy
        """
        if method == "vector":
            try:
                return await self.vector_search(db, query, result_type, filters, range_filters, limit)
            except Exception as e:
                logger.error(f"Vector search failed: {str(e)}")
                logger.info("Falling back to text search")
                return await self.text_search(db, query, result_type, filters, range_filters, limit)
        elif method == "hybrid":
            try:
                return await self.hybrid_search(db, query, result_type, filters, range_filters, limit)
            except Exception as e:
                logger.error(f"Hybrid search failed: {str(e)}")
                logger.info("Falling back to text search")
                return await self.text_search(db, query, result_type, filters, range_filters, limit)
        else:  # Default to text search
            return await self.text_search(db, query, result_type, filters, range_filters, limit)
    
    async def update_embedding(
        self,
        db: AsyncSession,
        id: Any,
        embedding: List[float]
    ) -> Optional[ModelType]:
        """Update the embedding for a record"""
        if not SearchConfig.VECTOR_SEARCH_ENABLED:
            logger.warning(f"Vector search not enabled, skipping embedding update for {self.model.__name__} {id}")
            return None
            
        obj = await self.get(db, id=id)
        if not obj:
            return None
            
        setattr(obj, self.embedding_field, embedding)
        
        try:
            await db.commit()
            await db.refresh(obj)
        except Exception as e:
            await db.rollback()
            logger.error(f"Error updating embedding for {self.model.__name__} {id}: {e}")
            raise
            
        return obj
    
    async def get_records_without_embeddings(
        self,
        db: AsyncSession,
        limit: int = 100
    ) -> List[ModelType]:
        """Get records that don't have embeddings yet"""
        if not hasattr(self.model, self.embedding_field):
            raise ValueError(f"Model {self.model.__name__} does not have embedding field {self.embedding_field}")
            
        query = select(self.model).filter(
            getattr(self.model, self.embedding_field).is_(None)
        ).limit(limit)
        
        result = await db.execute(query)
        return result.scalars().all()


# Specific CRUD classes with search capabilities

class CRUDProductSearch(SearchableCRUD):
    """CRUD for Product with search capabilities"""
    
    def __init__(self):
        super().__init__(model=Product)
    
    async def search_products(
        self,
        db: AsyncSession,
        query: str,
        method: str = "text",
        category_id: Optional[int] = None,
        brand: Optional[str] = None,
        min_price: Optional[float] = None,
        max_price: Optional[float] = None,
        limit: int = 20
    ) -> List[ProductSearchResult]:
        """
        Search products with specific product filters
        """
        # Build filters
        filters = {}
        if category_id is not None:
            filters["category_id"] = category_id
        if brand is not None:
            filters["brand"] = brand
            
        # Build range filters
        range_filters = {}
        if min_price is not None or max_price is not None:
            range_filters["price"] = {}
            if min_price is not None:
                range_filters["price"]["min"] = min_price
            if max_price is not None:
                range_filters["price"]["max"] = max_price
        
        # Execute search with appropriate strategy
        return await self.search(
            db=db,
            query=query,
            result_type=ProductSearchResult,
            method=method,
            filters=filters,
            range_filters=range_filters,
            limit=limit
        )
    
    async def generate_product_embedding_text(self, product: Product) -> str:
        """
        Generate the text that will be used for the embedding
        This combines multiple fields for richer semantic representation
        """
        # Combine relevant product fields
        text_parts = [
            product.title,
            product.description or "",
            product.brand or "",
            product.tags or ""
        ]
        
        # Add category name if available
        if product.category:
            text_parts.append(product.category.name)
            
        return " ".join(text_parts).strip()


class CRUDCategorySearch(SearchableCRUD):
    """CRUD for Category with search capabilities"""
    
    def __init__(self):
        super().__init__(model=Category)
    
    async def search_categories(
        self,
        db: AsyncSession,
        query: str,
        method: str = "text",
        limit: int = 20
    ) -> List[CategorySearchResult]:
        """
        Search categories
        """
        return await self.search(
            db=db,
            query=query,
            result_type=CategorySearchResult,
            method=method,
            limit=limit
        )


async def update_search_vector(self, db_session: AsyncSession, obj: ModelType) -> ModelType:
    """Update the search vector for a model instance"""
    if isinstance(obj, Category):
        # For categories
        search_text = f"{obj.name} {obj.description or ''}"
        query = update(self.model).where(self.model.id == obj.id).values(
            search_vector=func.to_tsvector('english', search_text)
        )
    elif isinstance(obj, Product):
        # For products
        search_text = f"{obj.title} {obj.description or ''} {obj.brand or ''} {obj.tags or ''}"
        query = update(self.model).where(self.model.id == obj.id).values(
            search_vector=func.to_tsvector('english', search_text)
        )
    # Add similar clauses for other models
    
    await db_session.execute(query)
    await db_session.commit()
    return obj




# Create instances
crud_product_search = CRUDProductSearch()
crud_category_search = CRUDCategorySearch()

# Helper function to enable vector search
async def enable_vector_search(api_key: Optional[str] = None) -> Dict[str, Any]:
    """Enable vector search functionality"""
    SearchConfig.VECTOR_SEARCH_ENABLED = True
    
    if api_key:
        SearchConfig.OPENAI_API_KEY = api_key
    
    return {
        "status": "success",
        "enabled": True,
        "has_api_key": bool(SearchConfig.OPENAI_API_KEY)
    }