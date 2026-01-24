"""
API Routes
"""

from fastapi import APIRouter
from api.routes import strategies

# Create main router
api_router = APIRouter()

# Include sub-routers
api_router.include_router(strategies.router)

__all__ = ["api_router"]