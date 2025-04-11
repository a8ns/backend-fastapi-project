from fastapi import APIRouter
from .routes import shops, products, llm

# Main API router
api_router = APIRouter()

# Include all application routers
api_router.include_router(
    shops.router,
    prefix="/shops",
    tags=["Shops"]
)

api_router.include_router(
    products.router,
    prefix="/products",
    tags=["Products"]
)

api_router.include_router(
    llm.router,
    prefix="/llm",
    tags=["LLM Integration"]
)