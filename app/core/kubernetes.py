"""
Kubernetes client and operations
"""

import asyncio
import logging
from typing import Dict, Any, List, Optional

try:
    from kubernetes import client, config
    from kubernetes.client.rest import ApiException
    from kubernetes.config.config_exception import ConfigException
    KUBERNETES_AVAILABLE = True
except ImportError:
    # Kubernetes not available, use mocks
    KUBERNETES_AVAILABLE = False
    class MockCoreV1Api:
        def list_namespaced_pod(self, namespace):
            class Pod:
                def __init__(self, name):
                    self.metadata = type('obj', (), {'name': name, 'namespace': namespace, 'creation_timestamp': '2024-01-01T00:00:00Z'})
                    self.status = type('obj', (), {'phase': 'Running', 'container_statuses': [], 'pod_ip': '127.0.0.1'})
                # Add more fields as needed
            return type('obj', (), {'items': [Pod('mock-pod')]})

        def list_namespaced_event(self, namespace):
            class Event:
                def __init__(self):
                    self.type = 'Normal'
                    self.reason = 'Mocked'
                    self.message = 'This is a mock event.'
                    self.involved_object = type('obj', (), {'kind': 'Pod', 'name': 'mock-pod'})
                    self.first_timestamp = '2024-01-01T00:00:00Z'
                    self.event_time = '2024-01-01T00:00:00Z'
                    self.metadata = type('obj', (), {'name': 'mock-event', 'namespace': namespace})
            return type('obj', (), {'items': [Event()]})

        def list_namespace(self):
            class Namespace:
                def __init__(self, name):
                    self.metadata = type('obj', (), {'name': name, 'creation_timestamp': '2024-01-01T00:00:00Z', 'labels': {}})
                    self.status = type('obj', (), {'phase': 'Active'})
            return type('obj', (), {'items': [Namespace('default')]})

        def list_namespaced_service(self, namespace):
            class Service:
                def __init__(self, name):
                    self.metadata = type('obj', (), {'name': name, 'namespace': namespace, 'creation_timestamp': '2024-01-01T00:00:00Z'})
                    self.spec = type('obj', (), {'type': 'ClusterIP', 'cluster_ip': '127.0.0.1', 'ports': []})
                    self.status = type('obj', (), {'load_balancer': None})
            return type('obj', (), {'items': [Service('mock-service')]})

    class MockAppsV1Api:
        def create_namespaced_deployment(self, namespace, body):
            return type('obj', (), {'metadata': type('obj', (), {'name': body.metadata.name, 'namespace': namespace, 'creation_timestamp': '2024-01-01T00:00:00Z'}), 'spec': type('obj', (), {'replicas': body.spec.replicas})})
        def read_namespaced_deployment(self, name, namespace):
            return type('obj', (), {'metadata': type('obj', (), {'name': name, 'namespace': namespace}), 'spec': type('obj', (), {'replicas': 1})})
        def patch_namespaced_deployment(self, name, namespace, body):
            return type('obj', (), {'metadata': type('obj', (), {'name': name, 'namespace': namespace}), 'spec': type('obj', (), {'replicas': body.spec.replicas})})
        def delete_namespaced_deployment(self, name, namespace, body):
            return None
        def list_namespaced_deployment(self, namespace):
            class Deployment:
                def __init__(self, name):
                    self.metadata = type('obj', (), {'name': name, 'namespace': namespace, 'creation_timestamp': '2024-01-01T00:00:00Z', 'labels': {}})
                    self.status = type('obj', (), {'ready_replicas': 1, 'replicas': 1, 'updated_replicas': 1, 'available_replicas': 1})
                    self.spec = type('obj', (), {'selector': type('obj', (), {'match_labels': {}})})
            return type('obj', (), {'items': [Deployment('mock-deployment')]})

    class MockClient:
        CoreV1Api = MockCoreV1Api
        AppsV1Api = MockAppsV1Api
        def load_incluster_config(self): pass
        def load_kube_config(self): pass
        ExtensionsV1beta1Api = lambda self: None
        V1Deployment = lambda *a, **kw: type('obj', (), {'metadata': type('obj', (), {'name': kw.get('name', 'mock-deployment'), 'namespace': kw.get('namespace', 'default')}), 'spec': type('obj', (), {'replicas': kw.get('replicas', 1), 'selector': type('obj', (), {'match_labels': {}}), 'template': type('obj', (), {'metadata': type('obj', (), {'labels': {'app': kw.get('name', 'mock-deployment')}}), 'spec': type('obj', (), {'containers': []})})})})
        V1ObjectMeta = lambda *a, **kw: type('obj', (), {'name': kw.get('name', 'mock'), 'namespace': kw.get('namespace', 'default'), 'labels': kw.get('labels', {})})
        V1DeploymentSpec = lambda *a, **kw: type('obj', (), {'replicas': kw.get('replicas', 1), 'selector': kw.get('selector'), 'template': kw.get('template')})
        V1LabelSelector = lambda *a, **kw: type('obj', (), {'match_labels': kw.get('match_labels', {})})
        V1PodTemplateSpec = lambda *a, **kw: type('obj', (), {'metadata': kw.get('metadata'), 'spec': kw.get('spec')})
        V1PodSpec = lambda *a, **kw: type('obj', (), {'containers': kw.get('containers', [])})
        V1Container = lambda *a, **kw: type('obj', (), {'name': kw.get('name', 'mock-container'), 'image': kw.get('image', 'mock-image'), 'ports': kw.get('ports', [])})
        V1ContainerPort = lambda *a, **kw: type('obj', (), {'container_port': kw.get('container_port', 80)})
        V1DeleteOptions = lambda *a, **kw: None

    client = MockClient()
    config = MockClient()
    class ApiException(Exception):
        pass
    class ConfigException(Exception):
        pass

logger = logging.getLogger(__name__)


class KubernetesClient:
    """Kubernetes client wrapper"""
    
    def __init__(self):
        self.api_client: Optional[client.ApiClient] = None
        self.v1: Optional[client.CoreV1Api] = None
        self.apps_v1: Optional[client.AppsV1Api] = None
        self.networking_v1: Optional[client.NetworkingV1Api] = None
        self.custom_objects: Optional[client.CustomObjectsApi] = None
        
    async def initialize(self):
        """Initialize Kubernetes client (mock for development)"""
        try:
            # Try in-cluster config first (for pods running in K8s)
            config.load_incluster_config()
            logger.info("Loaded in-cluster Kubernetes configuration")
        except ConfigException:
            try:
                # Fall back to kubeconfig file
                config.load_kube_config()
                logger.info("Loaded kubeconfig from file")
            except ConfigException as e:
                logger.warning(f"No Kubernetes config found: {e}")
                logger.info("Using mock Kubernetes client for development")
                # Create mock clients for development
                self.v1 = None
                self.apps_v1 = None
                self.extensions_v1beta1 = None
                return
        
        # Initialize API clients only if config was successful
        self.v1 = client.CoreV1Api()
        self.apps_v1 = client.AppsV1Api()
        self.extensions_v1beta1 = client.ExtensionsV1beta1Api()
        
        logger.info("Kubernetes client initialized successfully")
    
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


## No global client instance; use via agent abstraction