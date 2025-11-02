"""
API Router Configuration
Main API router that includes all endpoint modules
"""

from fastapi import APIRouter
from app.api.endpoints import chat, prices, weather, schemes, users

# Create main API router
api_router = APIRouter()

# Include endpoint routers
api_router.include_router(chat.router, prefix="/chat", tags=["chat"])
api_router.include_router(prices.router, prefix="/prices", tags=["prices"])
api_router.include_router(weather.router, prefix="/weather", tags=["weather"])
api_router.include_router(schemes.router, prefix="/schemes", tags=["schemes"])
api_router.include_router(users.router, prefix="/users", tags=["users"])