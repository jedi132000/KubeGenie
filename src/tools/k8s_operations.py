"""
High-level Kubernetes Operations for KubeGenie
Provides user-friendly cluster management functions

Step 3: Kubernetes operations with error handling and formatting
"""

from typing import Dict, List, Optional, Tuple
from .k8s_client import KubernetesClient, ClusterInfo, PodInfo, NodeInfo


class KubernetesOperations:
    """High-level Kubernetes operations for KubeGenie"""
    
    def __init__(self):
        self.client = KubernetesClient()
        self._connected = False
    
    def connect_to_cluster(self, kubeconfig_path: Optional[str] = None, context: Optional[str] = None) -> str:
        """
        Connect to a Kubernetes cluster and return status message
        
        Args:
            kubeconfig_path: Path to kubeconfig file
            context: Specific context to use
            
        Returns:
            Formatted status message
        """
        success, message = self.client.connect(kubeconfig_path, context)
        self._connected = success
        
        if success:
            cluster_info = self.client.get_cluster_info()
            return f"""🎯 **Cluster Connection Successful**

**Cluster Details:**
- 📋 Name: `{cluster_info.name}`
- 🔢 Version: `{cluster_info.version}`
- 🖥️ Nodes: `{cluster_info.nodes}`
- 📁 Namespaces: `{cluster_info.namespaces}`
- 🌐 Context: `{cluster_info.context}`

✅ Ready for Kubernetes operations!"""
        else:
            return f"""❌ **Cluster Connection Failed**

{message}

**Troubleshooting Tips:**
- Check if kubectl is configured: `kubectl cluster-info`
- Verify kubeconfig path: `~/.kube/config`
- Ensure cluster is accessible and running
- Try specifying a different context"""
    
    def get_cluster_overview(self) -> str:
        """Get comprehensive cluster overview"""
        if not self._connected:
            return "❌ Not connected to cluster. Use 'connect to cluster' first."
        
        success, status, message = self.client.get_cluster_status()
        
        if not success:
            return f"❌ Failed to get cluster status: {message}"
        
        return f"""📊 **Cluster Status Overview**

**Cluster Information:**
- 🏷️ Name: `{status['cluster_name']}`
- 🔢 Version: `{status['cluster_version']}`

**Resource Summary:**
- 🖥️ Nodes: {status['nodes']['status']} ({status['nodes']['ready']} ready)
- 🚀 Pods: {status['pods']['status']} ({status['pods']['running']} running)
- 📁 Namespaces: {status['namespaces']}

**Health Status:** {'🟢 Healthy' if status['nodes']['ready'] > 0 else '🔴 Issues Detected'}"""
    
    def list_cluster_nodes(self) -> str:
        """List all nodes in the cluster with details"""
        if not self._connected:
            return "❌ Not connected to cluster. Use 'connect to cluster' first."
        
        success, nodes, message = self.client.list_nodes()
        
        if not success:
            return f"❌ Failed to list nodes: {message}"
        
        if not nodes:
            return "📋 No nodes found in cluster."
        
        result = "🖥️ **Cluster Nodes**\n\n"
        
        for node in nodes:
            status_icon = "🟢" if node.status == "Ready" else "🔴"
            roles_str = ", ".join(node.roles)
            
            result += f"""**{node.name}**
- {status_icon} Status: `{node.status}`
- 🏷️ Roles: `{roles_str}`
- 🔢 Version: `{node.version}`
- 🌐 IP: `{node.internal_ip}`
- ⏰ Age: `{node.age}`
- 💻 OS: `{node.os_image}`

"""
        
        return result.strip()
    
    def list_pods_in_namespace(self, namespace: str = "default") -> str:
        """List pods in a specific namespace"""
        if not self._connected:
            return "❌ Not connected to cluster. Use 'connect to cluster' first."
        
        success, pods, message = self.client.list_pods(namespace=namespace)
        
        if not success:
            return f"❌ Failed to list pods: {message}"
        
        if not pods:
            return f"📋 No pods found in namespace `{namespace}`."
        
        result = f"🚀 **Pods in Namespace `{namespace}`**\n\n"
        
        # Group pods by status
        running_pods = [p for p in pods if p.status == "Running"]
        pending_pods = [p for p in pods if p.status == "Pending"]
        failed_pods = [p for p in pods if p.status == "Failed"]
        other_pods = [p for p in pods if p.status not in ["Running", "Pending", "Failed"]]
        
        # Summary
        result += f"**Summary:** {len(pods)} total pods\n"
        result += f"- 🟢 Running: {len(running_pods)}\n"
        result += f"- 🟡 Pending: {len(pending_pods)}\n"
        result += f"- 🔴 Failed: {len(failed_pods)}\n"
        if other_pods:
            result += f"- ⚪ Other: {len(other_pods)}\n"
        result += "\n"
        
        # List all pods
        for pod in pods:
            status_icon = {
                "Running": "🟢",
                "Pending": "🟡", 
                "Failed": "🔴",
                "Succeeded": "✅"
            }.get(pod.status, "⚪")
            
            restart_warning = " ⚠️" if pod.restarts > 5 else ""
            
            result += f"""**{pod.name}**
- {status_icon} Status: `{pod.status}`
- 📊 Ready: `{pod.ready}`
- 🔄 Restarts: `{pod.restarts}`{restart_warning}
- 🖥️ Node: `{pod.node}`
- ⏰ Age: `{pod.age}`

"""
        
        return result.strip()
    
    def list_all_pods(self) -> str:
        """List pods from all namespaces"""
        if not self._connected:
            return "❌ Not connected to cluster. Use 'connect to cluster' first."
        
        success, pods, message = self.client.list_pods(all_namespaces=True)
        
        if not success:
            return f"❌ Failed to list pods: {message}"
        
        if not pods:
            return "📋 No pods found in cluster."
        
        # Group pods by namespace
        pods_by_namespace = {}
        for pod in pods:
            if pod.namespace not in pods_by_namespace:
                pods_by_namespace[pod.namespace] = []
            pods_by_namespace[pod.namespace].append(pod)
        
        result = f"🚀 **All Pods in Cluster** ({len(pods)} total)\n\n"
        
        for namespace in sorted(pods_by_namespace.keys()):
            namespace_pods = pods_by_namespace[namespace]
            running_count = len([p for p in namespace_pods if p.status == "Running"])
            
            result += f"**📁 Namespace: `{namespace}`** ({len(namespace_pods)} pods, {running_count} running)\n"
            
            for pod in namespace_pods[:5]:  # Show first 5 pods per namespace
                status_icon = {
                    "Running": "🟢",
                    "Pending": "🟡",
                    "Failed": "🔴"
                }.get(pod.status, "⚪")
                
                result += f"  - {status_icon} `{pod.name}` ({pod.status}, {pod.age})\n"
            
            if len(namespace_pods) > 5:
                result += f"  - ... and {len(namespace_pods) - 5} more pods\n"
            
            result += "\n"
        
        return result.strip()
    
    def list_namespaces(self) -> str:
        """List all namespaces in the cluster"""
        if not self._connected:
            return "❌ Not connected to cluster. Use 'connect to cluster' first."
        
        success, namespaces, message = self.client.list_namespaces()
        
        if not success:
            return f"❌ Failed to list namespaces: {message}"
        
        if not namespaces:
            return "📋 No namespaces found in cluster."
        
        result = f"📁 **Cluster Namespaces** ({len(namespaces)} total)\n\n"
        
        # Separate system and user namespaces
        system_namespaces = [ns for ns in namespaces if ns.startswith(('kube-', 'default'))]
        user_namespaces = [ns for ns in namespaces if not ns.startswith(('kube-', 'default'))]
        
        if system_namespaces:
            result += "**System Namespaces:**\n"
            for ns in system_namespaces:
                result += f"- `{ns}`\n"
            result += "\n"
        
        if user_namespaces:
            result += "**User Namespaces:**\n"
            for ns in user_namespaces:
                result += f"- `{ns}`\n"
        
        return result.strip()
    
    def get_connection_status(self) -> str:
        """Get current connection status"""
        if not self._connected:
            return """🔴 **Not Connected to Cluster**

To connect to a cluster, ask:
- "Connect to my cluster"
- "Connect to cluster using context [name]"
- "Show me available contexts" """
        
        cluster_info = self.client.get_cluster_info()
        if cluster_info:
            return f"""🟢 **Connected to Cluster**

- 📋 Cluster: `{cluster_info.name}`
- 🔢 Version: `{cluster_info.version}`
- 🌐 Context: `{cluster_info.context}`
- 🖥️ Nodes: `{cluster_info.nodes}`
- 📁 Namespaces: `{cluster_info.namespaces}`

Ready for operations! """
        else:
            return "🟡 **Connection Status Unknown**"
    
    def is_connected(self) -> bool:
        """Check if connected to a cluster"""
        return self._connected