from fastapi import APIRouter
from .routes import shop, product, inventory, category, color, size, llm, search

# Main API router
api_router = APIRouter()

# Include all application routers
api_router.include_router(shop.router, prefix="/shops", tags=["shops"])
api_router.include_router(product.router, prefix="/products", tags=["products"])
api_router.include_router(inventory.router, prefix="/inventory", tags=["inventory"])
api_router.include_router(category.router, prefix="/categories", tags=["categories"])
api_router.include_router(color.router, prefix="/colors", tags=["colors"])
api_router.include_router(size.router, prefix="/sizes", tags=["sizes"])
api_router.include_router(search.router, prefix="/search", tags=["search"])

api_router.include_router(
    llm.router,
    prefix="/llm",
    tags=["LLM Integration"]
)