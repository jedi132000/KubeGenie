"""
Mock Kubernetes client for development
"""

import asyncio
import logging
from typing import Dict, Any, List, Optional

logger = logging.getLogger(__name__)

class MockKubernetesClient:
    """Mock Kubernetes client for development"""
    
    def __init__(self):
        self.v1 = None
        self.apps_v1 = None
        self.extensions_v1beta1 = None
        
    async def initialize(self):
        """Initialize mock Kubernetes client"""
        logger.info("Using mock Kubernetes client for development")
        return
        
    async def get_namespaces(self) -> List[Dict[str, Any]]:
        """Get mock namespaces"""
        return [
            {"name": "default", "status": "Active", "created": "2023-01-01T00:00:00Z"},
            {"name": "kube-system", "status": "Active", "created": "2023-01-01T00:00:00Z"},
            {"name": "kubegenie", "status": "Active", "created": "2023-01-01T00:00:00Z"}
        ]
    
    async def get_pods(self, namespace: str = "default") -> List[Dict[str, Any]]:
        """Get mock pods"""
        return [
            {
                "name": f"nginx-{i}",
                "namespace": namespace,
                "status": "Running",
                "ready": "1/1",
                "restarts": 0,
                "age": "1d",
                "ip": f"10.244.0.{i+10}"
            }
            for i in range(3)
        ]
    
    async def get_deployments(self, namespace: str = "default") -> List[Dict[str, Any]]:
        """Get mock deployments"""
        return [
            {
                "name": "nginx-deployment",
                "namespace": namespace,
                "ready": "3/3",
                "up_to_date": 3,
                "available": 3,
                "age": "1d"
            },
            {
                "name": "redis-deployment",
                "namespace": namespace,
                "ready": "1/1",
                "up_to_date": 1,
                "available": 1,
                "age": "2d"
            }
        ]
    
    async def get_services(self, namespace: str = "default") -> List[Dict[str, Any]]:
        """Get mock services"""
        return [
            {
                "name": "nginx-service",
                "namespace": namespace,
                "type": "ClusterIP",
                "cluster_ip": "10.96.0.100",
                "external_ip": "<none>",
                "ports": ["80/TCP"],
                "age": "1d"
            }
        ]
    
    async def create_deployment(self, name: str, image: str, replicas: int = 1, namespace: str = "default", **kwargs) -> Dict[str, Any]:
        """Create mock deployment"""
        logger.info(f"Mock: Creating deployment {name} with image {image}")
        return {
            "name": name,
            "namespace": namespace,
            "status": "Created",
            "message": f"Deployment {name} created successfully"
        }
    
    async def delete_deployment(self, name: str, namespace: str = "default") -> Dict[str, Any]:
        """Delete mock deployment"""
        logger.info(f"Mock: Deleting deployment {name}")
        return {
            "name": name,
            "namespace": namespace,
            "status": "Deleted",
            "message": f"Deployment {name} deleted successfully"
        }
    
    async def scale_deployment(self, name: str, replicas: int, namespace: str = "default") -> Dict[str, Any]:
        """Scale mock deployment"""
        logger.info(f"Mock: Scaling deployment {name} to {replicas} replicas")
        return {
            "name": name,
            "namespace": namespace,
            "replicas": replicas,
            "status": "Scaled",
            "message": f"Deployment {name} scaled to {replicas} replicas"
        }
    
    async def get_cluster_info(self) -> Dict[str, Any]:
        """Get mock cluster info"""
        return {
            "version": "v1.28.0",
            "platform": "mock-kubernetes",
            "nodes": 3,
            "status": "Ready"
        }
    
    async def get_events(self, namespace: str = "default") -> List[Dict[str, Any]]:
        """Get mock events"""
        return [
            {
                "name": "nginx-event-1",
                "namespace": namespace,
                "type": "Normal",
                "reason": "Created",
                "message": "Created pod nginx-12345",
                "timestamp": "2023-01-01T12:00:00Z"
            }
        ]

# Global instance
k8s_client = MockKubernetesClient()