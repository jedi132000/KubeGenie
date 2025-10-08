"""
Real Kubernetes client for production use
"""

import asyncio
import logging
from typing import Dict, Any, List, Optional
from kubernetes import client, config
from kubernetes.client.rest import ApiException
from kubernetes.config.config_exception import ConfigException

logger = logging.getLogger(__name__)

class KubernetesClient:
    """Real Kubernetes client"""
    
    def __init__(self):
        self.v1 = None
        self.apps_v1 = None
        self.networking_v1 = None
        self.custom_objects = None
        self.initialized = False
        
    def initialize(self):
        logger.debug("[KubeGenie DEBUG] Entering KubernetesClient.initialize()")
        """Initialize Kubernetes client"""
        try:
            logger.debug("[KubeGenie DEBUG] Trying in-cluster config...")
            config.load_incluster_config()
            logger.info("Loaded in-cluster Kubernetes configuration")
        except ConfigException:
            try:
                logger.debug("[KubeGenie DEBUG] Trying kubeconfig from file...")
                config.load_kube_config()
                logger.info("Loaded kubeconfig from file")
            except ConfigException as e:
                logger.error(f"[KubeGenie DEBUG] Failed to initialize Kubernetes client: {e}")
                raise

        # Initialize API clients
        logger.debug("[KubeGenie DEBUG] Initializing API clients...")
        self.v1 = client.CoreV1Api()
        self.apps_v1 = client.AppsV1Api()
        self.networking_v1 = client.NetworkingV1Api()
        self.custom_objects = client.CustomObjectsApi()
        self.initialized = True
        logger.info("Kubernetes client initialized successfully")
        
    def get_namespaces(self) -> List[Dict[str, Any]]:
        """Get all namespaces"""
        if not self.initialized:
            self.initialize()
            
        try:
            response = self.v1.list_namespace()
            namespaces = []
            for item in response.items:
                namespaces.append({
                    "name": item.metadata.name,
                    "status": item.status.phase,
                    "created": item.metadata.creation_timestamp.isoformat() if item.metadata.creation_timestamp else None,
                    "labels": item.metadata.labels or {}
                })
            return namespaces
        except ApiException as e:
            logger.error(f"Error getting namespaces: {e}")
            raise
    
    def get_pods(self, namespace: str = "default") -> List[Dict[str, Any]]:
        """Get pods in namespace"""
        if not self.initialized:
            self.initialize()
            
        try:
            response = self.v1.list_namespaced_pod(namespace=namespace)
            pods = []
            for item in response.items:
                pod_status = "Unknown"
                if item.status.phase:
                    pod_status = item.status.phase
                    
                ready_containers = 0
                total_containers = len(item.spec.containers) if item.spec.containers else 0
                
                if item.status.container_statuses:
                    ready_containers = sum(1 for cs in item.status.container_statuses if cs.ready)
                
                pods.append({
                    "name": item.metadata.name,
                    "namespace": item.metadata.namespace,
                    "status": pod_status,
                    "ready": f"{ready_containers}/{total_containers}",
                    "restarts": sum(cs.restart_count for cs in (item.status.container_statuses or [])),
                    "age": item.metadata.creation_timestamp.isoformat() if item.metadata.creation_timestamp else None,
                    "ip": item.status.pod_ip,
                    "node": item.spec.node_name
                })
            return pods
        except ApiException as e:
            logger.error(f"Error getting pods in namespace {namespace}: {e}")
            raise
    
    def get_deployments(self, namespace: str = "default") -> List[Dict[str, Any]]:
        """Get deployments in namespace"""
        if not self.initialized:
            self.initialize()
            
        try:
            response = self.apps_v1.list_namespaced_deployment(namespace=namespace)
            deployments = []
            for item in response.items:
                deployments.append({
                    "name": item.metadata.name,
                    "namespace": item.metadata.namespace,
                    "ready": f"{item.status.ready_replicas or 0}/{item.status.replicas or 0}",
                    "up_to_date": item.status.updated_replicas or 0,
                    "available": item.status.available_replicas or 0,
                    "age": item.metadata.creation_timestamp.isoformat() if item.metadata.creation_timestamp else None,
                    "labels": item.metadata.labels or {},
                    "selector": item.spec.selector.match_labels if item.spec.selector else {}
                })
            return deployments
        except ApiException as e:
            logger.error(f"Error getting deployments in namespace {namespace}: {e}")
            raise
    
    def get_services(self, namespace: str = "default") -> List[Dict[str, Any]]:
        """Get services in namespace"""
        if not self.initialized:
            self.initialize()
            
        try:
            response = self.v1.list_namespaced_service(namespace=namespace)
            services = []
            for item in response.items:
                ports = []
                if item.spec.ports:
                    ports = [f"{port.port}:{port.target_port}/{port.protocol}" for port in item.spec.ports]
                    
                services.append({
                    "name": item.metadata.name,
                    "namespace": item.metadata.namespace,
                    "type": item.spec.type,
                    "cluster_ip": item.spec.cluster_ip,
                    "external_ip": item.status.load_balancer.ingress[0].ip if (
                        item.status.load_balancer and 
                        item.status.load_balancer.ingress
                    ) else "<none>",
                    "ports": ports,
                    "age": item.metadata.creation_timestamp.isoformat() if item.metadata.creation_timestamp else None
                })
            return services
        except ApiException as e:
            logger.error(f"Error getting services in namespace {namespace}: {e}")
            raise
    
    def create_deployment(self, name: str, image: str, replicas: int = 1, namespace: str = "default", **kwargs) -> Dict[str, Any]:
        """Create a deployment"""
        if not self.initialized:
            self.initialize()
            
        try:
            # Create deployment object
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
            
            # Create the deployment
            response = self.apps_v1.create_namespaced_deployment(
                namespace=namespace,
                body=deployment
            )
            
            logger.info(f"Created deployment {name} in namespace {namespace}")
            
            return {
                "name": response.metadata.name,
                "namespace": response.metadata.namespace,
                "status": "Created",
                "message": f"Deployment {name} created successfully",
                "replicas": response.spec.replicas,
                "created": response.metadata.creation_timestamp.isoformat() if response.metadata.creation_timestamp else None
            }
            
        except ApiException as e:
            logger.error(f"Error creating deployment {name}: {e}")
            raise
    
    def delete_deployment(self, name: str, namespace: str = "default") -> Dict[str, Any]:
        """Delete a deployment"""
        if not self.initialized:
            self.initialize()
            
        try:
            response = self.apps_v1.delete_namespaced_deployment(
                name=name,
                namespace=namespace,
                body=client.V1DeleteOptions()
            )
            
            logger.info(f"Deleted deployment {name} from namespace {namespace}")
            
            return {
                "name": name,
                "namespace": namespace,
                "status": "Deleted",
                "message": f"Deployment {name} deleted successfully"
            }
            
        except ApiException as e:
            logger.error(f"Error deleting deployment {name}: {e}")
            raise
    
    def scale_deployment(self, name: str, replicas: int, namespace: str = "default") -> Dict[str, Any]:
        """Scale a deployment"""
        if not self.initialized:
            self.initialize()
            
        try:
            # Get current deployment
            deployment = self.apps_v1.read_namespaced_deployment(name=name, namespace=namespace)
            
            # Update replica count
            deployment.spec.replicas = replicas
            
            # Patch the deployment
            response = self.apps_v1.patch_namespaced_deployment(
                name=name,
                namespace=namespace,
                body=deployment
            )
            
            logger.info(f"Scaled deployment {name} to {replicas} replicas")
            
            return {
                "name": response.metadata.name,
                "namespace": response.metadata.namespace,
                "replicas": response.spec.replicas,
                "status": "Scaled",
                "message": f"Deployment {name} scaled to {replicas} replicas"
            }
            
        except ApiException as e:
            logger.error(f"Error scaling deployment {name}: {e}")
            raise
    
    def get_events(self, namespace: str = "default") -> List[Dict[str, Any]]:
        """Get events in namespace"""
        if not self.initialized:
            self.initialize()
            
        try:
            response = self.v1.list_namespaced_event(namespace=namespace)
            events = []
            for item in response.items:
                events.append({
                    "name": item.metadata.name,
                    "namespace": item.metadata.namespace,
                    "type": item.type,
                    "reason": item.reason,
                    "message": item.message,
                    "object": f"{item.involved_object.kind}/{item.involved_object.name}",
                    "timestamp": item.first_timestamp.isoformat() if item.first_timestamp else None
                })
            return events
        except ApiException as e:
            logger.error(f"Error getting events in namespace {namespace}: {e}")
            raise
    
    def get_cluster_info(self) -> Dict[str, Any]:
        """Get cluster information"""
        if not self.initialized:
            self.initialize()
            
        try:
            # Get version info
            version_response = self.v1.api_client.call_api(
                '/version', 'GET',
                response_type='object'
            )
            version_info = version_response[0] if version_response else {}
            
            # Get nodes
            nodes_response = self.v1.list_node()
            node_count = len(nodes_response.items)
            
            return {
                "version": version_info.get("gitVersion", "unknown"),
                "platform": "kubernetes",
                "nodes": node_count,
                "status": "Ready"
            }
        except ApiException as e:
            logger.error(f"Error getting cluster info: {e}")
            raise

# Global instance
k8s_client = KubernetesClient()