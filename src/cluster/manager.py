"""
Kubernetes Cluster Manager for KubeGenie

Manages connections and operations for Kubernetes clusters,
including Kind, EKS, GKE, and AKS clusters.
"""

import asyncio
import logging
from typing import Dict, List, Any, Optional
from datetime import datetime
import yaml
import os
from pathlib import Path

try:
    from kubernetes import client, config
    from kubernetes.client.rest import ApiException
    KUBERNETES_AVAILABLE = True
except ImportError:
    KUBERNETES_AVAILABLE = False
    client = None
    config = None
    print("Warning: kubernetes library not installed. Run: pip install kubernetes")

logger = logging.getLogger(__name__)

class ClusterConfig:
    """Configuration for a Kubernetes cluster"""
    
    def __init__(self, name: str, cluster_type: str, context: str, 
                 endpoint: Optional[str] = None, namespace: str = "default"):
        self.name = name
        self.cluster_type = cluster_type  # 'kind', 'eks', 'gke', 'aks', 'custom'
        self.context = context
        self.endpoint = endpoint
        self.namespace = namespace
        self.connected = False
        self.last_health_check: Optional[datetime] = None
        
    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "cluster_type": self.cluster_type,
            "context": self.context,
            "endpoint": self.endpoint,
            "namespace": self.namespace,
            "connected": self.connected,
            "last_health_check": self.last_health_check.isoformat() if self.last_health_check else None
        }

class KubernetesClusterManager:
    """Manages Kubernetes cluster connections and operations"""
    
    def __init__(self):
        self.clusters: Dict[str, ClusterConfig] = {}
        self.active_cluster: Optional[str] = None
        self.k8s_client = None
        
    async def discover_clusters(self) -> List[ClusterConfig]:
        """Discover available Kubernetes clusters from kubeconfig"""
        
        if not KUBERNETES_AVAILABLE:
            logger.error("Kubernetes library not available")
            return []
            
        try:
            # Load kubeconfig
            contexts, active_context = config.list_kube_config_contexts()
            
            discovered_clusters = []
            
            for context_info in contexts:
                context_name = context_info['name']
                cluster_info = context_info['context']
                
                # Determine cluster type based on context name
                cluster_type = self._determine_cluster_type(context_name)
                
                # Get cluster endpoint
                cluster_config = context_info.get('context', {}).get('cluster', '')
                
                cluster_config_obj = ClusterConfig(
                    name=context_name,
                    cluster_type=cluster_type,
                    context=context_name,
                    endpoint=cluster_config
                )
                
                discovered_clusters.append(cluster_config_obj)
                self.clusters[context_name] = cluster_config_obj
                
            logger.info(f"Discovered {len(discovered_clusters)} clusters")
            return discovered_clusters
            
        except Exception as e:
            logger.error(f"Failed to discover clusters: {e}")
            return []
    
    def _determine_cluster_type(self, context_name: str) -> str:
        """Determine cluster type from context name"""
        context_lower = context_name.lower()
        
        if 'kind' in context_lower:
            return 'kind'
        elif 'eks' in context_lower or 'aws' in context_lower:
            return 'eks'
        elif 'gke' in context_lower or 'gcp' in context_lower:
            return 'gke'
        elif 'aks' in context_lower or 'azure' in context_lower:
            return 'aks'
        elif 'minikube' in context_lower:
            return 'minikube'
        else:
            return 'custom'
    
    async def connect_to_cluster(self, cluster_name: str) -> bool:
        """Connect to a specific cluster"""
        
        if not KUBERNETES_AVAILABLE:
            logger.error("Kubernetes library not available")
            return False
            
        if cluster_name not in self.clusters:
            logger.error(f"Cluster {cluster_name} not found")
            return False
            
        try:
            cluster_config = self.clusters[cluster_name]
            
            # Load kubeconfig for specific context
            config.load_kube_config(context=cluster_config.context)
            
            # Create API client
            self.k8s_client = client.ApiClient()
            
            # Test connection
            v1 = client.CoreV1Api(self.k8s_client)
            nodes = v1.list_node()
            
            # Update cluster status
            cluster_config.connected = True
            cluster_config.last_health_check = datetime.now()
            self.active_cluster = cluster_name
            
            logger.info(f"Successfully connected to cluster {cluster_name}")
            logger.info(f"Cluster has {len(nodes.items)} nodes")
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to connect to cluster {cluster_name}: {e}")
            if cluster_name in self.clusters:
                self.clusters[cluster_name].connected = False
            return False
    
    async def get_cluster_health(self, cluster_name: Optional[str] = None) -> Dict[str, Any]:
        """Get health status of cluster"""
        
        target_cluster = cluster_name or self.active_cluster
        
        if not target_cluster or target_cluster not in self.clusters:
            return {"error": "No active cluster"}
            
        if not KUBERNETES_AVAILABLE or not self.k8s_client:
            return {"error": "Not connected to cluster"}
            
        try:
            v1 = client.CoreV1Api(self.k8s_client)
            
            # Get nodes
            nodes = v1.list_node()
            node_status = []
            ready_nodes = 0
            
            for node in nodes.items:
                node_info = {
                    "name": node.metadata.name,
                    "status": "Unknown",
                    "roles": [],
                    "version": node.status.node_info.kubelet_version,
                    "os": node.status.node_info.os_image
                }
                
                # Check node status
                for condition in node.status.conditions:
                    if condition.type == "Ready":
                        node_info["status"] = "Ready" if condition.status == "True" else "NotReady"
                        if node_info["status"] == "Ready":
                            ready_nodes += 1
                        break
                
                # Get node roles
                if node.metadata.labels:
                    for label, value in node.metadata.labels.items():
                        if "node-role.kubernetes.io" in label:
                            role = label.split("/")[-1]
                            node_info["roles"].append(role)
                
                node_status.append(node_info)
            
            # Get pods
            pods = v1.list_pod_for_all_namespaces()
            pod_stats = {
                "total": len(pods.items),
                "running": 0,
                "pending": 0,
                "failed": 0,
                "succeeded": 0
            }
            
            for pod in pods.items:
                phase = pod.status.phase.lower()
                if phase in pod_stats:
                    pod_stats[phase] += 1
                else:
                    pod_stats["running"] += 1 if phase == "running" else 0
            
            # Get namespaces
            namespaces = v1.list_namespace()
            
            cluster_health = {
                "cluster_name": target_cluster,
                "status": "healthy" if ready_nodes == len(nodes.items) else "degraded",
                "connected": True,
                "last_check": datetime.now().isoformat(),
                "nodes": {
                    "total": len(nodes.items),
                    "ready": ready_nodes,
                    "details": node_status
                },
                "pods": pod_stats,
                "namespaces": len(namespaces.items),
                "cluster_version": nodes.items[0].status.node_info.kubelet_version if nodes.items else "unknown"
            }
            
            # Update cluster config
            self.clusters[target_cluster].last_health_check = datetime.now()
            
            return cluster_health
            
        except Exception as e:
            logger.error(f"Failed to get cluster health: {e}")
            return {
                "cluster_name": target_cluster,
                "status": "error",
                "connected": False,
                "error": str(e),
                "last_check": datetime.now().isoformat()
            }
    
    async def get_cluster_metrics(self, cluster_name: Optional[str] = None) -> Dict[str, Any]:
        """Get basic metrics from cluster"""
        
        target_cluster = cluster_name or self.active_cluster
        
        if not target_cluster or not KUBERNETES_AVAILABLE or not self.k8s_client:
            return {"error": "Not connected to cluster"}
            
        try:
            v1 = client.CoreV1Api(self.k8s_client)
            
            # Get resource usage (basic metrics)
            nodes = v1.list_node()
            pods = v1.list_pod_for_all_namespaces()
            
            metrics = {
                "cluster_name": target_cluster,
                "timestamp": datetime.now().isoformat(),
                "metrics": []
            }
            
            # Node metrics
            for node in nodes.items:
                node_name = node.metadata.name
                
                # Basic node info (we'd need metrics-server for actual CPU/memory usage)
                metrics["metrics"].extend([
                    {
                        "name": "node_count",
                        "value": 1,
                        "labels": {
                            "node": node_name,
                            "cluster": target_cluster
                        },
                        "timestamp": datetime.now().isoformat()
                    }
                ])
            
            # Pod metrics
            pod_count_by_namespace = {}
            for pod in pods.items:
                namespace = pod.metadata.namespace
                pod_count_by_namespace[namespace] = pod_count_by_namespace.get(namespace, 0) + 1
            
            for namespace, count in pod_count_by_namespace.items():
                metrics["metrics"].append({
                    "name": "pod_count",
                    "value": count,
                    "labels": {
                        "namespace": namespace,
                        "cluster": target_cluster
                    },
                    "timestamp": datetime.now().isoformat()
                })
            
            return metrics
            
        except Exception as e:
            logger.error(f"Failed to get cluster metrics: {e}")
            return {"error": str(e)}
    
    async def execute_kubectl_command(self, command: List[str], namespace: Optional[str] = None) -> Dict[str, Any]:
        """Execute kubectl command on active cluster"""
        
        if not self.active_cluster:
            return {"error": "No active cluster"}
            
        try:
            # For now, we'll use basic Kubernetes API calls
            # In a full implementation, you might want to use subprocess for kubectl
            
            if not KUBERNETES_AVAILABLE or not self.k8s_client:
                return {"error": "Not connected to cluster"}
            
            # Handle common commands
            if len(command) >= 2 and command[0] == "get":
                return await self._handle_get_command(command[1], namespace)
            elif len(command) >= 2 and command[0] == "describe":
                return await self._handle_describe_command(command[1], namespace)
            else:
                return {"error": f"Command not supported: {' '.join(command)}"}
                
        except Exception as e:
            logger.error(f"Failed to execute command: {e}")
            return {"error": str(e)}
    
    async def _handle_get_command(self, resource: str, namespace: Optional[str] = None) -> Dict[str, Any]:
        """Handle 'kubectl get' commands"""
        
        v1 = client.CoreV1Api(self.k8s_client)
        
        try:
            if resource in ["nodes", "node"]:
                nodes = v1.list_node()
                return {
                    "command": f"get {resource}",
                    "items": [
                        {
                            "name": node.metadata.name,
                            "status": next((condition.status for condition in node.status.conditions 
                                          if condition.type == "Ready"), "Unknown"),
                            "roles": [label.split("/")[-1] for label in node.metadata.labels.keys() 
                                    if "node-role.kubernetes.io" in label],
                            "age": node.metadata.creation_timestamp.isoformat(),
                            "version": node.status.node_info.kubelet_version
                        }
                        for node in nodes.items
                    ]
                }
            
            elif resource in ["pods", "pod"]:
                if namespace:
                    pods = v1.list_namespaced_pod(namespace)
                else:
                    pods = v1.list_pod_for_all_namespaces()
                
                return {
                    "command": f"get {resource}",
                    "items": [
                        {
                            "name": pod.metadata.name,
                            "namespace": pod.metadata.namespace,
                            "status": pod.status.phase,
                            "restarts": sum(container.restart_count for container in pod.status.container_statuses or []),
                            "age": pod.metadata.creation_timestamp.isoformat()
                        }
                        for pod in pods.items
                    ]
                }
            
            elif resource in ["services", "service", "svc"]:
                if namespace:
                    services = v1.list_namespaced_service(namespace)
                else:
                    services = v1.list_service_for_all_namespaces()
                
                return {
                    "command": f"get {resource}",
                    "items": [
                        {
                            "name": svc.metadata.name,
                            "namespace": svc.metadata.namespace,
                            "type": svc.spec.type,
                            "cluster_ip": svc.spec.cluster_ip,
                            "ports": [f"{port.port}:{port.target_port}" for port in svc.spec.ports or []]
                        }
                        for svc in services.items
                    ]
                }
            
            else:
                return {"error": f"Resource type '{resource}' not supported"}
                
        except Exception as e:
            return {"error": str(e)}
    
    async def _handle_describe_command(self, resource: str, namespace: Optional[str] = None) -> Dict[str, Any]:
        """Handle 'kubectl describe' commands"""
        return {"error": "Describe command not yet implemented"}
    
    def get_cluster_list(self) -> List[Dict[str, Any]]:
        """Get list of all configured clusters"""
        return [cluster.to_dict() for cluster in self.clusters.values()]
    
    def get_active_cluster(self) -> Optional[Dict[str, Any]]:
        """Get active cluster information"""
        if self.active_cluster and self.active_cluster in self.clusters:
            return self.clusters[self.active_cluster].to_dict()
        return None

# Global cluster manager instance
cluster_manager = KubernetesClusterManager()