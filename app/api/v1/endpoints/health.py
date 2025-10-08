"""
Health check endpoints
"""

from fastapi import APIRouter, status
from typing import Dict, Any
import logging

logger = logging.getLogger(__name__)

router = APIRouter()


@router.get("/", status_code=status.HTTP_200_OK)
async def health_check() -> Dict[str, Any]:
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "kubegenie-backend",
        "version": "1.0.0"
    }


@router.get("/ready", status_code=status.HTTP_200_OK)
async def readiness_check() -> Dict[str, Any]:
    """Readiness check endpoint"""
    # Add checks for dependencies (database, k8s, etc.)
    return {
        "status": "ready",
        "checks": {
            "database": "ok",
            "kubernetes": "ok",
            "redis": "ok"
        }
    }


@router.get("/live", status_code=status.HTTP_200_OK)
async def liveness_check() -> Dict[str, Any]:
    """Liveness check endpoint"""
    return {
        "status": "alive",
        "timestamp": "2024-01-01T00:00:00Z"
    }