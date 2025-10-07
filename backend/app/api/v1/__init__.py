"""
API v1 router
"""

from fastapi import APIRouter
from app.api.v1.endpoints import kubernetes, crossplane, health, chat

api_router = APIRouter()

# Include endpoint routers
api_router.include_router(health.router, prefix="/health", tags=["health"])
api_router.include_router(kubernetes.router, prefix="/k8s", tags=["kubernetes"])
api_router.include_router(crossplane.router, prefix="/crossplane", tags=["crossplane"])
api_router.include_router(chat.router, prefix="/chat", tags=["chat"])