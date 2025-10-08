"""
Kubernetes API endpoints
"""

from fastapi import APIRouter, HTTPException, status, Depends, Query
from typing import Dict, Any, List, Optional
import logging
from app.core.cluster_manager import ClusterManager

# Initialize cluster manager and register a default cluster (for demo; replace config as needed)
cluster_manager = ClusterManager()
default_config = {}  # TODO: Fill with real kubeconfig or connection info
cluster_manager.register_cluster("default", default_config)
from pydantic import BaseModel

logger = logging.getLogger(__name__)

router = APIRouter()


class DeploymentRequest(BaseModel):
    """Deployment creation request"""
    name: str
    image: str
    replicas: int = 1
    namespace: str = "default"


class ScaleRequest(BaseModel):
    """Deployment scaling request"""
    replicas: int


@router.get("/pods")
async def get_pods(
    namespace: str = Query(default="default", description="Kubernetes namespace")
) -> List[Dict[str, Any]]:
    """Get pods in namespace"""
    try:
        agent = cluster_manager.get_active_agent()
        pods = agent.get_pods(namespace=namespace)
        return pods
    except Exception as e:
        logger.error(f"Failed to get pods: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get pods: {str(e)}"
        )


@router.post("/deployments")
async def create_deployment(request: DeploymentRequest) -> Dict[str, Any]:
    """Create a new deployment"""
    try:
        agent = cluster_manager.get_active_agent()
        result = agent.create_deployment(
            name=request.name,
            image=request.image,
            replicas=request.replicas,
            namespace=request.namespace
        )
        return result
    except Exception as e:
        logger.error(f"Failed to create deployment: {e}")
        if hasattr(e, 'status') and getattr(e, 'status', None) == 422:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=f"Validation error: {str(e)}"
            )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create deployment: {str(e)}"
        )


@router.patch("/deployments/{name}/scale")
async def scale_deployment(
    name: str,
    request: ScaleRequest,
    namespace: str = Query(default="default", description="Kubernetes namespace")
) -> Dict[str, Any]:
    """Scale a deployment"""
    try:
        agent = cluster_manager.get_active_agent()
        result = agent.scale_deployment(
            name=name,
            replicas=request.replicas,
            namespace=namespace
        )
        return result
    except Exception as e:
        logger.error(f"Failed to scale deployment: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to scale deployment: {str(e)}"
        )


@router.delete("/deployments/{name}")
async def delete_deployment(
    name: str,
    namespace: str = Query(default="default", description="Kubernetes namespace")
) -> Dict[str, Any]:
    """Delete a deployment"""
    try:
        agent = cluster_manager.get_active_agent()
        result = agent.delete_deployment(name=name, namespace=namespace)
        return result
    except Exception as e:
        logger.error(f"Failed to delete deployment: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete deployment: {str(e)}"
        )


@router.get("/events")
async def get_events(
    namespace: str = Query(default="default", description="Kubernetes namespace")
) -> List[Dict[str, Any]]:
    """Get events in namespace"""
    try:
        agent = cluster_manager.get_active_agent()
        events = agent.get_events(namespace=namespace)
        return events
    except Exception as e:
        logger.error(f"Failed to get events: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get events: {str(e)}"
        )


@router.get("/namespaces")
async def list_namespaces() -> List[Dict[str, Any]]:
    """List all namespaces"""
    try:
        agent = cluster_manager.get_active_agent()
        return agent.get_namespaces()
    except Exception as e:
        logger.error(f"Failed to list namespaces: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to list namespaces: {str(e)}"
        )


@router.get("/cluster-info")
async def get_cluster_info() -> Dict[str, Any]:
    """Get cluster information"""
    try:
        agent = cluster_manager.get_active_agent()
        return agent.get_cluster_info()
    except Exception as e:
        logger.error(f"Failed to get cluster info: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get cluster info: {str(e)}"
        )