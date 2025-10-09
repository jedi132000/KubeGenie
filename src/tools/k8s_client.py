"""
Kubernetes Client for KubeGenie
Handles cluster connections and basic operations

Step 3: Kubernetes client setup with kubeconfig support
"""

import os
import yaml
from typing import Dict, List, Optional, Any, Tuple
from kubernetes import client, config
from kubernetes.client.rest import ApiException
from dataclasses import dataclass
from datetime import datetime


@dataclass
class ClusterInfo:
    """Information about a Kubernetes cluster"""
    name: str
    server: str
    version: str
    nodes: int
    namespaces: int
    connected: bool
    context: str


@dataclass 
class PodInfo:
    """Information about a Kubernetes pod"""
    name: str
    namespace: str
    status: str
    ready: str
    restarts: int
    age: str
    node: str


@dataclass
class NodeInfo:
    """Information about a Kubernetes node"""
    name: str
    status: str
    roles: List[str]
    age: str
    version: str
    internal_ip: str
    os_image: str


class KubernetesClient:
    """Main Kubernetes client for cluster operations"""
    
    def __init__(self):
        self.core_v1 = None
        self.apps_v1 = None
        self.current_context = None
        self.cluster_info = None
        self._connected = False
        
    def connect(self, kubeconfig_path: Optional[str] = None, context: Optional[str] = None) -> Tuple[bool, str]:
        """
        Connect to a Kubernetes cluster
        
        Args:
            kubeconfig_path: Path to kubeconfig file (optional)
            context: Specific context to use (optional)
            
        Returns:
            Tuple of (success: bool, message: str)
        """
        try:
            # Load kubeconfig
            if kubeconfig_path:
                config.load_kube_config(config_file=kubeconfig_path, context=context)
            else:
                # Try in-cluster config first, then default kubeconfig
                try:
                    config.load_incluster_config()
                except config.ConfigException:
                    config.load_kube_config(context=context)
            
            # Initialize API clients
            self.core_v1 = client.CoreV1Api()
            self.apps_v1 = client.AppsV1Api()
            
            # Get current context
            contexts, active_context = config.list_kube_config_contexts()
            self.current_context = active_context['name'] if active_context else "unknown"
            
            # Test connection and get cluster info
            version_api = client.VersionApi()
            version_info = version_api.get_code()
            nodes = self.core_v1.list_node()
            namespaces = self.core_v1.list_namespace()
            
            # Get cluster server info
            configuration = client.Configuration().get_default_copy()
            server_url = configuration.host
            
            self.cluster_info = ClusterInfo(
                name=self.current_context,
                server=server_url,
                version=f"{version_info.major}.{version_info.minor}",
                nodes=len(nodes.items),
                namespaces=len(namespaces.items),
                connected=True,
                context=self.current_context
            )
            
            self._connected = True
            return True, f"✅ Connected to cluster '{self.current_context}' (v{self.cluster_info.version})"
            
        except Exception as e:
            self._connected = False
            return False, f"❌ Connection failed: {str(e)}"
    
    def is_connected(self) -> bool:
        """Check if client is connected to a cluster"""
        return self._connected
    
    def get_cluster_info(self) -> Optional[ClusterInfo]:
        """Get current cluster information"""
        return self.cluster_info
    
    def list_nodes(self) -> Tuple[bool, List[NodeInfo], str]:
        """
        List all nodes in the cluster
        
        Returns:
            Tuple of (success: bool, nodes: List[NodeInfo], message: str)
        """
        if not self.is_connected():
            return False, [], "❌ Not connected to cluster"
        
        try:
            nodes_response = self.core_v1.list_node()
            nodes = []
            
            for node in nodes_response.items:
                # Get node status
                status = "Unknown"
                for condition in node.status.conditions:
                    if condition.type == "Ready":
                        status = "Ready" if condition.status == "True" else "NotReady"
                        break
                
                # Get node roles
                roles = []
                if node.metadata.labels:
                    for label, value in node.metadata.labels.items():
                        if label.startswith("node-role.kubernetes.io/"):
                            role = label.split("/")[-1]
                            if role:
                                roles.append(role)
                
                if not roles:
                    roles = ["worker"]
                
                # Get internal IP
                internal_ip = "Unknown"
                if node.status.addresses:
                    for address in node.status.addresses:
                        if address.type == "InternalIP":
                            internal_ip = address.address
                            break
                
                # Calculate age
                age = self._calculate_age(node.metadata.creation_timestamp)
                
                node_info = NodeInfo(
                    name=node.metadata.name,
                    status=status,
                    roles=roles,
                    age=age,
                    version=node.status.node_info.kubelet_version,
                    internal_ip=internal_ip,
                    os_image=node.status.node_info.os_image
                )
                nodes.append(node_info)
            
            return True, nodes, f"✅ Found {len(nodes)} nodes"
            
        except ApiException as e:
            return False, [], f"❌ API error: {e.reason}"
        except Exception as e:
            return False, [], f"❌ Error listing nodes: {str(e)}"
    
    def list_pods(self, namespace: str = "default", all_namespaces: bool = False) -> Tuple[bool, List[PodInfo], str]:
        """
        List pods in a namespace or all namespaces
        
        Args:
            namespace: Namespace to list pods from
            all_namespaces: If True, list pods from all namespaces
            
        Returns:
            Tuple of (success: bool, pods: List[PodInfo], message: str)
        """
        if not self.is_connected():
            return False, [], "❌ Not connected to cluster"
        
        try:
            if all_namespaces:
                pods_response = self.core_v1.list_pod_for_all_namespaces()
            else:
                pods_response = self.core_v1.list_namespaced_pod(namespace=namespace)
            
            pods = []
            
            for pod in pods_response.items:
                # Calculate ready containers
                ready_containers = 0
                total_containers = len(pod.spec.containers)
                
                if pod.status.container_statuses:
                    for container_status in pod.status.container_statuses:
                        if container_status.ready:
                            ready_containers += 1
                
                ready_str = f"{ready_containers}/{total_containers}"
                
                # Calculate restart count
                restart_count = 0
                if pod.status.container_statuses:
                    for container_status in pod.status.container_statuses:
                        restart_count += container_status.restart_count
                
                # Calculate age
                age = self._calculate_age(pod.metadata.creation_timestamp)
                
                pod_info = PodInfo(
                    name=pod.metadata.name,
                    namespace=pod.metadata.namespace,
                    status=pod.status.phase,
                    ready=ready_str,
                    restarts=restart_count,
                    age=age,
                    node=pod.spec.node_name or "Unknown"
                )
                pods.append(pod_info)
            
            namespace_msg = "all namespaces" if all_namespaces else f"namespace '{namespace}'"
            return True, pods, f"✅ Found {len(pods)} pods in {namespace_msg}"
            
        except ApiException as e:
            return False, [], f"❌ API error: {e.reason}"
        except Exception as e:
            return False, [], f"❌ Error listing pods: {str(e)}"
    
    def list_namespaces(self) -> Tuple[bool, List[str], str]:
        """
        List all namespaces in the cluster
        
        Returns:
            Tuple of (success: bool, namespaces: List[str], message: str)
        """
        if not self.is_connected():
            return False, [], "❌ Not connected to cluster"
        
        try:
            namespaces_response = self.core_v1.list_namespace()
            namespaces = [ns.metadata.name for ns in namespaces_response.items]
            namespaces.sort()
            
            return True, namespaces, f"✅ Found {len(namespaces)} namespaces"
            
        except ApiException as e:
            return False, [], f"❌ API error: {e.reason}"
        except Exception as e:
            return False, [], f"❌ Error listing namespaces: {str(e)}"
    
    def get_cluster_status(self) -> Tuple[bool, Dict[str, Any], str]:
        """
        Get comprehensive cluster status
        
        Returns:
            Tuple of (success: bool, status: Dict, message: str)
        """
        if not self.is_connected():
            return False, {}, "❌ Not connected to cluster"
        
        try:
            # Get nodes status
            success_nodes, nodes, _ = self.list_nodes()
            ready_nodes = len([n for n in nodes if n.status == "Ready"]) if success_nodes else 0
            total_nodes = len(nodes) if success_nodes else 0
            
            # Get pods status
            success_pods, pods, _ = self.list_pods(all_namespaces=True)
            running_pods = len([p for p in pods if p.status == "Running"]) if success_pods else 0
            total_pods = len(pods) if success_pods else 0
            
            # Get namespaces count
            success_ns, namespaces, _ = self.list_namespaces()
            namespace_count = len(namespaces) if success_ns else 0
            
            status = {
                "cluster_name": self.cluster_info.name if self.cluster_info else "unknown",
                "cluster_version": self.cluster_info.version if self.cluster_info else "unknown",
                "nodes": {
                    "ready": ready_nodes,
                    "total": total_nodes,
                    "status": f"{ready_nodes}/{total_nodes} Ready"
                },
                "pods": {
                    "running": running_pods,
                    "total": total_pods,
                    "status": f"{running_pods}/{total_pods} Running"
                },
                "namespaces": namespace_count,
                "connected": True
            }
            
            return True, status, "✅ Cluster status retrieved"
            
        except Exception as e:
            return False, {}, f"❌ Error getting cluster status: {str(e)}"
    
    def _calculate_age(self, creation_timestamp) -> str:
        """Calculate age string from creation timestamp"""
        if not creation_timestamp:
            return "Unknown"
        
        now = datetime.now(creation_timestamp.tzinfo)
        age = now - creation_timestamp
        
        days = age.days
        hours = age.seconds // 3600
        minutes = (age.seconds % 3600) // 60
        
        if days > 0:
            return f"{days}d"
        elif hours > 0:
            return f"{hours}h"
        elif minutes > 0:
            return f"{minutes}m"
        else:
            return "<1m"


def get_available_contexts() -> List[str]:
    """Get list of available kubectl contexts"""
    try:
        contexts, active_context = config.list_kube_config_contexts()
        return [context['name'] for context in contexts]
    except Exception:
        return []


def get_current_context() -> Optional[str]:
    """Get current kubectl context"""
    try:
        contexts, active_context = config.list_kube_config_contexts()
        return active_context['name'] if active_context else None
    except Exception:
        return None