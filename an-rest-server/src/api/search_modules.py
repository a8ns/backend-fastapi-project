from typing import List, Optional, Dict, Any, TypeVar, Generic, Union
from pydantic import BaseModel as PydanticBaseModel
from sqlalchemy import text, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from models.base_model import BaseModel
from core.config import settings
from core.logging import logger
import os
import httpx
from fastapi import HTTPException

ModelType = TypeVar("ModelType", bound=BaseModel)
ResultSchemaType = TypeVar("ResultSchemaType", bound=PydanticBaseModel)


class SearchResult(PydanticBaseModel):
    """Base search result model"""
    id: str
    relevance: float

class SearchConfig:
    """Global search configuration that reads from application settings"""
    
    # Vector search toggle
    VECTOR_SEARCH_ENABLED = settings.vector_search_enabled
    
    # API keys
    OPENAI_API_KEY = settings.openai_api_key
    
    # Embedding settings
    EMBEDDING_MODEL = settings.embedding_model
    EMBEDDING_DIMENSIONS = settings.embedding_dimensions
    
    # Hybrid search weights
    TEXT_WEIGHT = settings.hybrid_search_text_weight
    VECTOR_WEIGHT = settings.hybrid_search_vector_weight
    
    # Performance settings
    EMBEDDING_BATCH_SIZE = settings.embedding_batch_size
    MAX_SEARCH_RESULTS = settings.max_search_results
    
    @classmethod
    def enable_vector_search(cls, api_key=None):
        """Enable vector search and optionally set API key"""
        cls.VECTOR_SEARCH_ENABLED = True
        if api_key:
            cls.OPENAI_API_KEY = api_key

# Base class for all search strategies
class SearchStrategy(Generic[ModelType, ResultSchemaType]):
    """Base class for search strategies"""
    def __init__(self, model: ModelType):
        self.model = model
    
    async def search(
        self,
        db: AsyncSession,
        query: str,
        filters: Optional[Dict[str, Any]] = None,
        limit: int = 20,
        **kwargs
    ) -> List[ResultSchemaType]:
        """
        Execute search and return results
        Must be implemented by subclasses
        """
        raise NotImplementedError
    
    def _apply_filters(self, query_obj, filters: Optional[Dict[str, Any]] = None):
        """Apply filters to the query"""
        if not filters:
            return query_obj
            
        for field, value in filters.items():
            if hasattr(self.model, field):
                if isinstance(value, list):
                    query_obj = query_obj.filter(getattr(self.model, field).in_(value))
                else:
                    query_obj = query_obj.filter(getattr(self.model, field) == value)
        
        return query_obj
    
    def _apply_range_filters(self, query_obj, range_filters: Optional[Dict[str, Dict[str, Any]]] = None):
        """Apply range filters (min/max) to the query"""
        if not range_filters:
            return query_obj
            
        for field, conditions in range_filters.items():
            if hasattr(self.model, field):
                if 'min' in conditions and conditions['min'] is not None:
                    query_obj = query_obj.filter(getattr(self.model, field) >= conditions['min'])
                if 'max' in conditions and conditions['max'] is not None:
                    query_obj = query_obj.filter(getattr(self.model, field) <= conditions['max'])
        
        return query_obj


class TextSearchStrategy(SearchStrategy[ModelType, ResultSchemaType]):
    """Text search using PostgreSQL's full-text search capabilities"""
    
    def __init__(self, model: ModelType, search_vector_field: str = 'search_vector', result_type: ResultSchemaType = None):
        super().__init__(model)
        self.search_vector_field = search_vector_field
        self.result_type = result_type
    
    async def search(
        self,
        db: AsyncSession,
        query: str,
        filters: Optional[Dict[str, Any]] = None,
        range_filters: Optional[Dict[str, Dict[str, Any]]] = None,
        limit: int = 20,
        **kwargs
    ) -> List[ResultSchemaType]:
        """Execute text search"""
        logger.info(f"Executing text search for '{query}' on {self.model.__tablename__}")
        
        # Format query for tsquery
        search_terms = ' & '.join(query.split())
        
        # Create base query
        search_vector = getattr(self.model, self.search_vector_field)
        db_query = select(self.model)
        
        # Add relevance calculation
        db_query = db_query.add_columns(
            func.ts_rank(search_vector, func.to_tsquery('english', search_terms)).label("relevance")
        )
        
        # Filter by search query
        db_query = db_query.filter(search_vector.op('@@')(func.to_tsquery('english', search_terms)))
        
        # Apply additional filters
        db_query = self._apply_filters(db_query, filters)
        db_query = self._apply_range_filters(db_query, range_filters)
        
        # Sort by relevance and limit results
        db_query = db_query.order_by(text("relevance DESC")).limit(limit)
        
        # Execute query
        result = await db.execute(db_query)
        rows = result.all()
        
        # Convert to result schema
        if not self.result_type:
            raise ValueError("Result type not specified")
            
        return [self._to_schema(row) for row in rows]
    
    def _to_schema(self, row):
        """Convert SQL result to schema"""
        # Extract model data as dict, excluding SQLAlchemy attributes
        model_data = {c.name: getattr(row[0], c.name) 
                     for c in row[0].__table__.columns}
        
        # Add relevance score
        model_data['relevance'] = row.relevance
        
        # Return as schema
        return self.result_type(**model_data)


class VectorSearchStrategy(SearchStrategy):
    """Vector-based semantic search using pgvector"""
    
    def __init__(
        self, 
        model, 
        embedding_field: str = 'embedding',
        result_type = None
    ):
        super().__init__(model)
        self.embedding_field = embedding_field
        self.result_type = result_type
    
    async def generate_embedding(self, text: str) -> List[float]:
        """Generate embedding using OpenAI API"""
        if not SearchConfig.OPENAI_API_KEY:
            raise ValueError("OpenAI API key is not set")
        
        async with httpx.AsyncClient() as client:
            try:
                response = await client.post(
                    "https://api.openai.com/v1/embeddings",
                    headers={"Authorization": f"Bearer {SearchConfig.OPENAI_API_KEY}"},
                    json={
                        "model": SearchConfig.EMBEDDING_MODEL,
                        "input": text
                    },
                    timeout=30.0
                )
                response.raise_for_status()
                data = response.json()
                return data["data"][0]["embedding"]
            except httpx.HTTPError as e:
                logger.error(f"Error generating embedding: {str(e)}")
                raise HTTPException(status_code=500, detail=f"Embedding service error: {str(e)}")
    
    async def search(
        self,
        db: AsyncSession,
        query: str,
        filters: Optional[Dict[str, Any]] = None,
        range_filters: Optional[Dict[str, Dict[str, Any]]] = None,
        limit: int = 20,
        **kwargs
    ) -> List:
        """Execute vector search"""
        if not SearchConfig.VECTOR_SEARCH_ENABLED:
            logger.warning("Vector search requested but not enabled")
            raise ValueError("Vector search is not enabled")
            
        logger.info(f"Executing vector search for '{query}' on {self.model.__tablename__}")
        
        # Generate embedding for query
        embedding = await self.generate_embedding(query)
        
        # Create base query
        db_query = select(self.model)
        
        # Add similarity calculation (1 - cosine distance for relevance score)
        embedding_field = getattr(self.model, self.embedding_field)
        db_query = db_query.add_columns(
            (1 - text(f"{self.model.__tablename__}.{self.embedding_field} <=> :embedding")).label("relevance")
        )
        
        # Filter to include only records with embeddings
        db_query = db_query.filter(embedding_field.is_not(None))
        
        # Apply additional filters
        db_query = self._apply_filters(db_query, filters)
        db_query = self._apply_range_filters(db_query, range_filters)
        
        # Sort by similarity and limit results
        db_query = db_query.order_by(text("relevance DESC")).limit(limit)
        
        # Set parameters for the embedding
        db_query = db_query.params(embedding=embedding)
        
        # Execute query
        result = await db.execute(db_query)
        rows = result.all()
        
        # Convert to result schema
        if not self.result_type:
            raise ValueError("Result type not specified")
            
        return [self._to_schema(row) for row in rows]
    
    def _to_schema(self, row):
        """Convert SQL result to schema"""
        # Extract model data as dict, excluding SQLAlchemy attributes
        model_data = {c.name: getattr(row[0], c.name) 
                     for c in row[0].__table__.columns}
        
        # Add relevance score
        model_data['relevance'] = row.relevance
        
        # Return as schema
        return self.result_type(**model_data)


class HybridSearchStrategy(SearchStrategy[ModelType, ResultSchemaType]):
    """Combine text and vector search for better results"""
    
    def __init__(
        self, 
        model: ModelType, 
        text_search_vector_field: str = 'search_vector',
        vector_embedding_field: str = 'embedding',
        result_type: ResultSchemaType = None,
        text_weight: float = 0.4,
        vector_weight: float = 0.6
    ):
        super().__init__(model)
        self.text_search_vector_field = text_search_vector_field
        self.vector_embedding_field = vector_embedding_field
        self.result_type = result_type
        self.text_weight = text_weight
        self.vector_weight = vector_weight
        self.vector_strategy = VectorSearchStrategy(model, vector_embedding_field, result_type)
    
    async def search(
        self,
        db: AsyncSession,
        query: str,
        filters: Optional[Dict[str, Any]] = None,
        range_filters: Optional[Dict[str, Dict[str, Any]]] = None,
        limit: int = 20,
        **kwargs
    ) -> List[ResultSchemaType]:
        """Execute hybrid search (text + vector)"""
        if not SearchConfig.VECTOR_SEARCH_ENABLED:
            logger.warning("Hybrid search requested but vector search not enabled, falling back to text search")
            text_strategy = TextSearchStrategy(self.model, self.text_search_vector_field, self.result_type)
            return await text_strategy.search(db, query, filters, range_filters, limit, **kwargs)
            
        logger.info(f"Executing hybrid search for '{query}' on {self.model.__tablename__}")
        
        try:
            # Generate embedding for query
            embedding = await self.vector_strategy.generate_embedding(query)
            
            # Format query for tsquery
            search_terms = ' & '.join(query.split())
            
            # Create base query
            search_vector = getattr(self.model, self.text_search_vector_field)
            embedding_field = getattr(self.model, self.vector_embedding_field)
            
            db_query = select(self.model)
            
            # Add weighted relevance calculation
            db_query = db_query.add_columns(
                (
                    self.text_weight * func.ts_rank(search_vector, func.to_tsquery('english', search_terms)) +
                    self.vector_weight * (1 - text(f"{self.model.__tablename__}.{self.vector_embedding_field} <=> :embedding"))
                ).label("relevance")
            )
            
            # Filter to include records that match either text or have embeddings
            db_query = db_query.filter(
                (search_vector.op('@@')(func.to_tsquery('english', search_terms))) |
                (embedding_field.is_not(None))
            )
            
            # Apply additional filters
            db_query = self._apply_filters(db_query, filters)
            db_query = self._apply_range_filters(db_query, range_filters)
            
            # Sort by combined relevance and limit results
            db_query = db_query.order_by(text("relevance DESC")).limit(limit)
            
            # Set parameters for the embedding
            db_query = db_query.params(embedding=embedding)
            
            # Execute query
            result = await db.execute(db_query)
            rows = result.all()
            
            # Convert to result schema
            if not self.result_type:
                raise ValueError("Result type not specified")
                
            return [self._to_schema(row) for row in rows]
            
        except Exception as e:
            logger.error(f"Hybrid search error: {str(e)}")
            logger.info("Falling back to text search")
            
            # Fall back to text search
            text_strategy = TextSearchStrategy(self.model, self.text_search_vector_field, self.result_type)
            return await text_strategy.search(db, query, filters, range_filters, limit, **kwargs)
    
    def _to_schema(self, row):
        """Convert SQL result to schema"""
        # Extract model data as dict, excluding SQLAlchemy attributes
        model_data = {c.name: getattr(row[0], c.name) 
                     for c in row[0].__table__.columns}
        
        # Add relevance score
        model_data['relevance'] = row.relevance
        
        # Return as schema
        return self.result_type(**model_data)