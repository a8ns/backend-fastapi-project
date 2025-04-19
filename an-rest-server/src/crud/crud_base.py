from typing import Type, TypeVar, Generic, Optional, List, Union, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete
from sqlalchemy.future import select
from models.base_model import BaseModel
from uuid import UUID
from core.logging import logger
from pydantic import BaseModel as PydanticBaseModel



ModelType = TypeVar("ModelType", bound=BaseModel)
CreateSchemaType = TypeVar("CreateSchemaType", bound=PydanticBaseModel)
UpdateSchemaType = TypeVar("UpdateSchemaType", bound=PydanticBaseModel)
IdType = TypeVar("IdType", UUID, int, str)

class CRUDBase(Generic[ModelType, CreateSchemaType, UpdateSchemaType]):
    def __init__(self, model: Type[ModelType]):
        """
        CRUD object with model & schema information
        """
        self.model = model
    
    async def get(self, db_session: AsyncSession, id: IdType) -> Optional[ModelType]:
        """Get a record by id"""
        logging.info(f"GET crud get is being called for {self.model.__name__} with id {id}")
        result = await db_session.execute(select(self.model).filter(self.model.id == id))
        return result.scalars().first()
    
    async def get_by_field(self, db_session: AsyncSession, field: str, value: Any) -> Optional[ModelType]:
        """Get a record by a specific field"""
        logging.info(f"GET crud get_by_field is being called for {self.model.__name__} with {field}={value}")
        result = await db_session.execute(
            select(self.model).filter(getattr(self.model, field) == value)
        )
        return result.scalars().first()
    
    async def get_multi(
        self, 
        db_session: AsyncSession, 
        *, 
        skip: int = 0, 
        limit: int = 100,
        filters: Optional[Dict[str, Any]] = None
    ) -> List[ModelType]:
        """Get multiple records with optional filtering"""
        query = select(self.model)
        
        # Apply filters if provided
        if filters:
            for field, value in filters.items():
                if hasattr(self.model, field):
                    query = query.filter(getattr(self.model, field) == value)
        
        query = query.offset(skip).limit(limit)
        result = await db_session.execute(query)
        return result.scalars().all()
    
    async def create(self, db_session: AsyncSession, *, obj_in: Union[CreateSchemaType, Dict[str, Any]]) -> ModelType:
        """Create a new record"""
        logging.info(f"POST crud create is being called for {self.model.__name__}")
        
        if isinstance(obj_in, dict):
            obj_in_data = obj_in
        else:
            obj_in_data = obj_in.model_dump()
        
        db_obj = self.model(**obj_in_data)
        db_session.add(db_obj)
        try:
            await db_session.commit()
            await db_session.refresh(db_obj)
        except Exception as e:
            await db_session.rollback()
            logging.error(f"Error creating {self.model.__name__}: {e}")
            raise
        return db_obj
    
    async def update(
        self, 
        db_session: AsyncSession, 
        *, 
        db_obj: ModelType, 
        obj_in: Union[UpdateSchemaType, Dict[str, Any]]
    ) -> ModelType:
        """Update an existing record"""
        if isinstance(obj_in, dict):
            update_data = obj_in
        else:
            update_data = obj_in.model_dump(exclude_unset=True)
        
        for field, value in update_data.items():
            if hasattr(db_obj, field) and value is not None:
                setattr(db_obj, field, value)
        
        try:
            await db_session.commit()
            await db_session.refresh(db_obj)
        except Exception as e:
            await db_session.rollback()
            logging.error(f"Error updating {self.model.__name__} {db_obj.id}: {e}")
            raise
        return db_obj
    
    async def remove(self, db_session: AsyncSession, *, id: IdType) -> Optional[ModelType]:
        """Delete a record"""
        obj = await self.get(db_session, id=id)
        if not obj:
            return None
        
        try:
            await db_session.delete(obj)
            await db_session.commit()
        except Exception as e:
            await db_session.rollback()
            logging.error(f"Error deleting {self.model.__name__} {id}: {e}")
            raise
        return obj
    
    async def bulk_create(
        self, 
        db_session: AsyncSession, 
        *, 
        objs_in: List[Union[CreateSchemaType, Dict[str, Any]]]
    ) -> List[ModelType]:
        """Create multiple records at once"""
        db_objs = []
        for obj_in in objs_in:
            if isinstance(obj_in, dict):
                obj_data = obj_in
            else:
                obj_data = obj_in.model_dump()
            db_obj = self.model(**obj_data)
            db_objs.append(db_obj)
        
        db_session.add_all(db_objs)
        try:
            await db_session.commit()
            for obj in db_objs:
                await db_session.refresh(obj)
        except Exception as e:
            await db_session.rollback()
            logging.error(f"Error bulk creating {self.model.__name__}: {e}")
            raise
        return db_objs
    
    async def count(
        self, 
        db_session: AsyncSession, 
        *, 
        filters: Optional[Dict[str, Any]] = None
    ) -> int:
        """Count records with optional filtering"""
        from sqlalchemy import func
        
        query = select(func.count()).select_from(self.model)
        
        # Apply filters if provided
        if filters:
            for field, value in filters.items():
                if hasattr(self.model, field):
                    query = query.filter(getattr(self.model, field) == value)
        
        result = await db_session.execute(query)
        return result.scalar_one()