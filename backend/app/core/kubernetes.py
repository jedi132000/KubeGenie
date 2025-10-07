"""
Kubernetes client and operations
"""

import asyncio
import logging
from typing import Dict, Any, List, Optional
from kubernetes import client, config
from kubernetes.client.rest import ApiException

logger = logging.getLogger(__name__)


class KubernetesClient:
    """Kubernetes client wrapper"""
    
    def __init__(self):
        self.api_client: Optional[client.ApiClient] = None
        self.v1: Optional[client.CoreV1Api] = None
        self.apps_v1: Optional[client.AppsV1Api] = None
        self.networking_v1: Optional[client.NetworkingV1Api] = None
        self.custom_objects: Optional[client.CustomObjectsApi] = None
        
    async def initialize(self) -> None:
        """Initialize Kubernetes client"""
        try:
            # Try to load in-cluster config first
            try:
                config.load_incluster_config()
                logger.info("Loaded in-cluster Kubernetes configuration")
            except config.ConfigException:
                # Fallback to local kubeconfig
                config.load_kube_config()
                logger.info("Loaded local Kubernetes configuration")
                
            # Initialize API clients
            self.api_client = client.ApiClient()
            self.v1 = client.CoreV1Api()
            self.apps_v1 = client.AppsV1Api()
            self.networking_v1 = client.NetworkingV1Api()
            self.custom_objects = client.CustomObjectsApi()
            
            logger.info("Kubernetes client initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize Kubernetes client: {e}")
            raise
    
    async def get_pods(self, namespace: str = "default") -> List[Dict[str, Any]]:
        """Get pods in namespace"""
        if not self.v1:
            raise RuntimeError("Kubernetes client not initialized")
            
        try:
            pods = self.v1.list_namespaced_pod(namespace=namespace)
            return [
                {
                    "name": pod.metadata.name,
                    "namespace": pod.metadata.namespace,
                    "status": pod.status.phase,
                    "ready": sum(1 for c in pod.status.container_statuses or [] if c.ready),
                    "restarts": sum(c.restart_count for c in pod.status.container_statuses or []),
                    "age": pod.metadata.creation_timestamp,
                }
                for pod in pods.items
            ]
        except ApiException as e:
            logger.error(f"Failed to get pods in namespace {namespace}: {e}")
            raise
    
    async def create_deployment(self, name: str, image: str, replicas: int = 1, 
                              namespace: str = "default") -> Dict[str, Any]:
        """Create a deployment"""
        if not self.apps_v1:
            raise RuntimeError("Kubernetes client not initialized")
            
        try:
            deployment = client.V1Deployment(
                api_version="apps/v1",
                kind="Deployment",
                metadata=client.V1ObjectMeta(name=name, namespace=namespace),
                spec=client.V1DeploymentSpec(
                    replicas=replicas,
                    selector=client.V1LabelSelector(
                        match_labels={"app": name}
                    ),
                    template=client.V1PodTemplateSpec(
                        metadata=client.V1ObjectMeta(labels={"app": name}),
                        spec=client.V1PodSpec(
                            containers=[
                                client.V1Container(
                                    name=name,
                                    image=image,
                                    ports=[client.V1ContainerPort(container_port=80)]
                                )
                            ]
                        )
                    )
                )
            )
            
            result = self.apps_v1.create_namespaced_deployment(
                namespace=namespace,
                body=deployment
            )
            
            logger.info(f"Created deployment {name} in namespace {namespace}")
            return {
                "name": result.metadata.name,
                "namespace": result.metadata.namespace,
                "replicas": result.spec.replicas,
                "status": "created"
            }
            
        except ApiException as e:
            logger.error(f"Failed to create deployment {name}: {e}")
            raise
    
    async def scale_deployment(self, name: str, replicas: int, 
                             namespace: str = "default") -> Dict[str, Any]:
        """Scale a deployment"""
        if not self.apps_v1:
            raise RuntimeError("Kubernetes client not initialized")
            
        try:
            # Get current deployment
            deployment = self.apps_v1.read_namespaced_deployment(
                name=name, namespace=namespace
            )
            
            # Update replicas
            deployment.spec.replicas = replicas
            
            # Patch deployment
            result = self.apps_v1.patch_namespaced_deployment(
                name=name,
                namespace=namespace,
                body=deployment
            )
            
            logger.info(f"Scaled deployment {name} to {replicas} replicas")
            return {
                "name": result.metadata.name,
                "namespace": result.metadata.namespace,
                "replicas": result.spec.replicas,
                "status": "scaled"
            }
            
        except ApiException as e:
            logger.error(f"Failed to scale deployment {name}: {e}")
            raise
    
    async def delete_deployment(self, name: str, namespace: str = "default") -> Dict[str, Any]:
        """Delete a deployment"""
        if not self.apps_v1:
            raise RuntimeError("Kubernetes client not initialized")
            
        try:
            self.apps_v1.delete_namespaced_deployment(
                name=name,
                namespace=namespace,
                body=client.V1DeleteOptions()
            )
            
            logger.info(f"Deleted deployment {name} in namespace {namespace}")
            return {
                "name": name,
                "namespace": namespace,
                "status": "deleted"
            }
            
        except ApiException as e:
            logger.error(f"Failed to delete deployment {name}: {e}")
            raise
    
    async def get_events(self, namespace: str = "default") -> List[Dict[str, Any]]:
        """Get events in namespace"""
        if not self.v1:
            raise RuntimeError("Kubernetes client not initialized")
            
        try:
            events = self.v1.list_namespaced_event(namespace=namespace)
            return [
                {
                    "type": event.type,
                    "reason": event.reason,
                    "message": event.message,
                    "object": f"{event.involved_object.kind}/{event.involved_object.name}",
                    "timestamp": event.first_timestamp or event.event_time,
                }
                for event in events.items
            ]
        except ApiException as e:
            logger.error(f"Failed to get events in namespace {namespace}: {e}")
            raise


# Global Kubernetes client instance
k8s_client = KubernetesClient()