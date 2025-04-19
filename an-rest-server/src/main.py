import logging
from fastapi import FastAPI, Depends, Security
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from middlewares.middleware import APIKeyMiddleware
from api.routers import api_router
from core.config import settings
from db.db_utils import init_db, close_db
from starlette.middleware.sessions import SessionMiddleware
from prometheus_fastapi_instrumentator import Instrumentator
from core.logging import logger 
from fastapi.security import APIKeyHeader


# Define API key security scheme for Swagger UI
api_key_header = APIKeyHeader(name="X_API_KEY", auto_error=False)

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: Initialize database
    logger.info("Initializing database...")
    await init_db()
    logger.info("Database initialized successfully")
    
    yield
    
    # Shutdown: Close database connections
    logger.info("Shutting down...")
    await close_db()

async def get_api_key(api_key: str = Security(api_key_header)):
    if api_key != settings.rest_server_api_key:
        raise HTTPException(
            status_code=401,
            detail="Invalid API Key",
        )
    return api_key

# Create FastAPI app
app = FastAPI(
    title=settings.project_name,
    description="API for shop and product management with map integration",
    version="0.1.0",
    lifespan=lifespan,
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    openapi_url="/api/openapi.json",
    dependencies=[Depends(get_api_key)]
)
app.add_middleware(APIKeyMiddleware)
# Set up CORS middleware

origins = [origin.strip() for origin in settings.cors_origins.split(",")]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API router
app.include_router(api_router, prefix=settings.api_v1_str)

Instrumentator().instrument(app).expose(app)

@app.get("/")
async def root():
    """
    Root endpoint - health check.
    """
    return {
        "message": f"Welcome to {settings.project_name}",
        "version": "0.1.0",
        "status": "operational"
    }


@app.get("/health")
async def health_check():
    """
    Health check endpoint.
    """
    return {"status": "healthy"}