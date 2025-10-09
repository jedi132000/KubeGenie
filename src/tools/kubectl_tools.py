"""
KubeGenie LangChain Tools
LangChain tool wrappers for Kubernetes operations

Step 4: Tool integration for agent
"""

from typing import Optional, Type, Any, List
from pydantic import BaseModel, Field

# Import Kubernetes operations
KubernetesOperations = None
# Global shared instance for connection state persistence
_shared_k8s_ops = None

try:
    from .k8s_operations import KubernetesOperations
    _shared_k8s_ops = KubernetesOperations()
except ImportError:
    try:
        # Fallback for different import paths
        import sys
        import os
        sys.path.append(os.path.dirname(__file__))
        from k8s_operations import KubernetesOperations
        _shared_k8s_ops = KubernetesOperations()
    except ImportError:
        KubernetesOperations = None
        _shared_k8s_ops = None

# LangChain tool imports
try:
    from langchain_core.tools import BaseTool
    from langchain_core.callbacks import CallbackManagerForToolRun
    LANGCHAIN_AVAILABLE = True
except ImportError:
    # Fallback if LangChain not available
    class BaseTool:
        name: str = ""
        description: str = ""
        
        def _run(self, *args, **kwargs):
            pass
    
    class CallbackManagerForToolRun:
        pass
    
    LANGCHAIN_AVAILABLE = False

from typing import Type, Optional, List, Dict, Any
from langchain_core.tools import BaseTool
from langchain_core.callbacks import CallbackManagerForToolRun
from pydantic import BaseModel, Field

# Import our Kubernetes operations
try:
    from ..tools.k8s_operations import KubernetesOperations
    KUBERNETES_AVAILABLE = True
except ImportError:
    KUBERNETES_AVAILABLE = False


class ConnectClusterInput(BaseModel):
    """Input for cluster connection tool"""
    context: Optional[str] = Field(default=None, description="Specific kubectl context to use (optional)")
    kubeconfig_path: Optional[str] = Field(default=None, description="Path to kubeconfig file (optional)")


class ConnectClusterTool(BaseTool):
    """Tool for connecting to Kubernetes clusters"""
    name: str = "connect_to_cluster"
    description: str = """Connect to a Kubernetes cluster using kubeconfig.
    Use this when the user wants to connect to their cluster.
    Can optionally specify a specific context or kubeconfig path."""
    args_schema: Type[BaseModel] = ConnectClusterInput
    
    def _run(self, run_manager: Optional[CallbackManagerForToolRun] = None) -> str:
        """Execute cluster connection"""
        if _shared_k8s_ops is None:
            return "❌ Kubernetes client not available."
        
        return _shared_k8s_ops.connect_to_cluster()


class ClusterStatusInput(BaseModel):
    """Input for cluster status tool"""
    pass  # No parameters needed


class ClusterStatusTool(BaseTool):
    """Tool for getting cluster status overview"""
    name: str = "get_cluster_status"
    description: str = """Get comprehensive Kubernetes cluster status including nodes, pods, and health.
    Use this when the user asks about cluster health, status, or overview."""
    args_schema: Type[BaseModel] = ClusterStatusInput
    
    def _run(self, run_manager: Optional[CallbackManagerForToolRun] = None) -> str:
        """Execute cluster status check"""
        if _shared_k8s_ops is None:
            return "❌ Kubernetes client not available."
        
        if not _shared_k8s_ops.is_connected():
            return "❌ Not connected to cluster. Please connect first using connect_to_cluster."
        
        try:
            return _shared_k8s_ops.get_cluster_overview()
        except Exception as e:
            return f"❌ Failed to get cluster status: {str(e)}"


class ListNodesInput(BaseModel):
    """Input for list nodes tool"""
    pass  # No parameters needed


class ListNodesTool(BaseTool):
    """Tool for listing cluster nodes"""
    name: str = "list_cluster_nodes"
    description: str = """List all nodes in the Kubernetes cluster with their status, roles, and details.
    Use this when the user asks about nodes, workers, masters, or node health."""
    args_schema: Type[BaseModel] = ListNodesInput
    
    def _run(self, run_manager: Optional[CallbackManagerForToolRun] = None) -> str:
        """Execute node listing"""
        if _shared_k8s_ops is None:
            return "❌ Kubernetes client not available."
        
        if not _shared_k8s_ops.is_connected():
            return "❌ Not connected to cluster. Please connect first using connect_to_cluster."
        
        try:
            return _shared_k8s_ops.list_cluster_nodes()
        except Exception as e:
            return f"❌ Failed to list nodes: {str(e)}"


class ListPodsInput(BaseModel):
    """Input for list pods tool"""
    namespace: str = Field(default="default", description="Kubernetes namespace to list pods from")
    all_namespaces: bool = Field(default=False, description="List pods from all namespaces")


class ListPodsTool(BaseTool):
    """Tool for listing pods in Kubernetes"""
    name: str = "list_pods"
    description: str = """List pods in a specific namespace or all namespaces.
    Use this when the user asks about pods, applications, workloads, or deployments.
    Can specify a namespace or list from all namespaces."""
    args_schema: Type[BaseModel] = ListPodsInput
    
    def _run(
        self, 
        namespace: str = "default",
        all_namespaces: bool = False,
        run_manager: Optional[CallbackManagerForToolRun] = None
    ) -> str:
        """Execute pod listing"""
        if _shared_k8s_ops is None:
            return "❌ Kubernetes client not available."
        
        if not _shared_k8s_ops.is_connected():
            return "❌ Not connected to cluster. Please connect first using connect_to_cluster."
        
        try:
            if all_namespaces:
                return _shared_k8s_ops.list_all_pods()
            else:
                return _shared_k8s_ops.list_pods_in_namespace(namespace)
        except Exception as e:
            return f"❌ Failed to list pods: {str(e)}"


class ListNamespacesInput(BaseModel):
    """Input for list namespaces tool"""
    pass  # No parameters needed


class ListNamespacesTool(BaseTool):
    """Tool for listing Kubernetes namespaces"""
    name: str = "list_namespaces"
    description: str = """List all namespaces in the Kubernetes cluster.
    Use this when the user asks about namespaces, environments, or wants to see available namespaces."""
    args_schema: Type[BaseModel] = ListNamespacesInput
    
    def _run(self, run_manager: Optional[CallbackManagerForToolRun] = None) -> str:
        """Execute namespace listing"""
        if _shared_k8s_ops is None:
            return "❌ Kubernetes client not available."
        
        if not _shared_k8s_ops.is_connected():
            return "❌ Not connected to cluster. Please connect first using connect_to_cluster."
        
        try:
            return _shared_k8s_ops.list_namespaces()
        except Exception as e:
            return f"❌ Failed to list namespaces: {str(e)}"


def create_kubernetes_tools() -> List[BaseTool]:
    """Create and return all Kubernetes tools"""
    try:
        if KubernetesOperations is None:
            return []
        
        return [
            ConnectClusterTool(),
            ClusterStatusTool(),
            ListNodesTool(),
            ListPodsTool(),
            ListNamespacesTool()
        ]
    except Exception as e:
        print(f"Failed to create Kubernetes tools: {e}")
        return []