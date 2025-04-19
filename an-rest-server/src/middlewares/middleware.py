from fastapi import HTTPException, Request
from starlette.middleware.base import BaseHTTPMiddleware
from core.config import settings

class APIKeyMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        # Exclude certain routes from the API key check
        excluded_paths = [
            "/openapi.json", 
            "/api/redoc", 
            "/api/docs",       # Add this for Traefik forwarded routes
            "/api/openapi.json", # Add this for Traefik forwarded routes 
            "/metrics", 
            "/_stcore/metrics", 
            "/_stcore/health"
            ]
        
        if any(request.url.path.startswith(path) for path in excluded_paths):
            response = await call_next(request)
            return response

        api_key = request.headers.get("X_API_KEY")
        if not api_key or api_key != settings.rest_server_api_key:
            raise HTTPException(status_code=401, detail="Could not validate API Key")
        response = await call_next(request)
        return response