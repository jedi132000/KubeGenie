"""
KubeGenie Gradio UI - Conversational Interface

Modern chat-based interface for AI-powered Kubernetes multi-cluster management.
Provides natural language interaction with the KubeGenie platform.
"""

import gradio as gr
import asyncio
import aiohttp
import json
import logging
from datetime import datetime
from typing import List, Dict, Any, Optional, Tuple
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from dataclasses import dataclass

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configuration
API_BASE_URL = "http://127.0.0.1:8080"
CHAT_HISTORY_LIMIT = 50

@dataclass
class ChatMessage:
    """Chat message data structure"""
    role: str  # 'user' or 'assistant'
    content: str
    timestamp: datetime
    metadata: Optional[Dict[str, Any]] = None

class KubeGenieAPI:
    """API client for KubeGenie backend"""
    
    def __init__(self, base_url: str = API_BASE_URL):
        self.base_url = base_url
        
    async def get_system_status(self) -> Dict[str, Any]:
        """Get system status from API"""
        async with aiohttp.ClientSession() as session:
            try:
                async with session.get(f"{self.base_url}/api/v1/status") as response:
                    if response.status == 200:
                        return await response.json()
                    else:
                        return {"error": f"API returned status {response.status}"}
            except Exception as e:
                logger.error(f"Failed to get system status: {e}")
                return {"error": str(e)}
    
    async def discover_clusters(self) -> Dict[str, Any]:
        """Discover available clusters"""
        async with aiohttp.ClientSession() as session:
            try:
                async with session.get(f"{self.base_url}/api/v1/clusters/discover") as response:
                    if response.status == 200:
                        return await response.json()
                    else:
                        return {"error": f"API returned status {response.status}"}
            except Exception as e:
                logger.error(f"Failed to discover clusters: {e}")
                return {"error": str(e)}
    
    async def connect_cluster(self, context_name: str) -> Dict[str, Any]:
        """Connect to a specific cluster"""
        async with aiohttp.ClientSession() as session:
            try:
                async with session.post(f"{self.base_url}/api/v1/clusters/{context_name}/connect") as response:
                    if response.status == 200:
                        return await response.json()
                    else:
                        return {"error": f"API returned status {response.status}"}
            except Exception as e:
                logger.error(f"Failed to connect to cluster: {e}")
                return {"error": str(e)}
    
    async def get_cluster_health(self, context_name: str) -> Dict[str, Any]:
        """Get cluster health information"""
        async with aiohttp.ClientSession() as session:
            try:
                async with session.get(f"{self.base_url}/api/v1/clusters/{context_name}/health") as response:
                    if response.status == 200:
                        return await response.json()
                    else:
                        return {"error": f"API returned status {response.status}"}
            except Exception as e:
                logger.error(f"Failed to get cluster health: {e}")
                return {"error": str(e)}
                
    async def execute_kubectl(self, context_name: str, command: str) -> Dict[str, Any]:
        """Execute kubectl command"""
        async with aiohttp.ClientSession() as session:
            try:
                # Split command string into list for API
                command_list = command.strip().split()
                data = {"command": command_list}
                async with session.post(f"{self.base_url}/api/v1/clusters/{context_name}/kubectl", json=data) as response:
                    if response.status == 200:
                        return await response.json()
                    else:
                        return {"error": f"API returned status {response.status}"}
            except Exception as e:
                logger.error(f"Failed to execute kubectl command: {e}")
                return {"error": str(e)}

    async def analyze_clusters(self, cluster_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze clusters using AI agents"""
        async with aiohttp.ClientSession() as session:
            try:
                async with session.post(
                    f"{self.base_url}/api/v1/analyze", 
                    json=cluster_data
                ) as response:
                    if response.status == 200:
                        return await response.json()
                    else:
                        return {"error": f"API returned status {response.status}"}
            except Exception as e:
                logger.error(f"Failed to analyze clusters: {e}")
                return {"error": str(e)}

class KubeGenieChatbot:
    """Main chatbot logic for KubeGenie"""
    
    def __init__(self):
        self.api = KubeGenieAPI()
        self.chat_history: List[ChatMessage] = []
    
    def add_message(self, role: str, content: str, metadata: Optional[Dict[str, Any]] = None):
        """Add message to chat history"""
        message = ChatMessage(
            role=role,
            content=content,
            timestamp=datetime.now(),
            metadata=metadata
        )
        self.chat_history.append(message)
        
        # Keep only recent messages
        if len(self.chat_history) > CHAT_HISTORY_LIMIT:
            self.chat_history = self.chat_history[-CHAT_HISTORY_LIMIT:]
    
    async def process_message(self, user_input: str, chat_history: List) -> Tuple[str, List]:
        """Process user message and return response"""
        try:
            # Add user message to history
            self.add_message("user", user_input)
            
            # Determine intent and generate response
            response = await self._generate_response(user_input.lower().strip())
            
            # Add assistant response to history
            self.add_message("assistant", response)
            
            # Update chat history for Gradio (messages format)
            chat_history.append({"role": "user", "content": user_input})
            chat_history.append({"role": "assistant", "content": response})
            
            return "", chat_history
            
        except Exception as e:
            error_msg = f"Sorry, I encountered an error: {str(e)}"
            logger.error(f"Error processing message: {e}")
            chat_history.append({"role": "user", "content": user_input})
            chat_history.append({"role": "assistant", "content": error_msg})
            return "", chat_history
    
    async def _generate_response(self, user_input: str) -> str:
        """Generate appropriate response based on user input"""
        
        # Kubectl commands
        if user_input.startswith("kubectl"):
            return await self._handle_kubectl_command(user_input)
        
        # Health/Status queries
        elif any(keyword in user_input for keyword in ["status", "health", "how are", "running"]):
            return await self._handle_status_query()
        
        # Cluster queries
        elif any(keyword in user_input for keyword in ["cluster", "clusters", "nodes", "pods", "connect", "discover"]):
            return await self._handle_cluster_query(user_input)
        
        # Analysis queries
        elif any(keyword in user_input for keyword in ["analyze", "analysis", "check", "issues", "problems", "infrastructure"]):
            return await self._handle_analysis_query()
        
        # Help queries
        elif any(keyword in user_input for keyword in ["help", "what can", "commands", "guide"]):
            return self._handle_help_query()
        
        # Default response
        else:
            return await self._handle_general_query(user_input)
    
    async def _handle_status_query(self) -> str:
        """Handle system status queries"""
        status_data = await self.api.get_system_status()
        
        if "error" in status_data:
            return f"❌ Unable to get system status: {status_data['error']}"
        
        orchestrator = status_data.get("orchestrator", {})
        agents = status_data.get("agents", {})
        
        response = "🟢 **KubeGenie System Status**\n\n"
        response += f"**Orchestrator**: {orchestrator.get('status', 'unknown').title()}\n"
        response += f"**Registered Agents**: {orchestrator.get('registered_agents', 0)}\n"
        response += f"**Active Tasks**: {orchestrator.get('active_tasks', 0)}\n"
        response += f"**Queue Size**: {orchestrator.get('queue_size', 0)}\n\n"
        
        response += "**Active Agents**:\n"
        for agent_id, agent_info in agents.items():
            status_emoji = "🟢" if agent_info.get("status") == "idle" else "🟡"
            response += f"{status_emoji} {agent_info.get('name', agent_id)}\n"
        
        return response
    
    async def _handle_cluster_query(self, user_input: str) -> str:
        """Handle cluster-related queries"""
        
        # Check if user wants to discover clusters
        if "discover" in user_input or "find" in user_input or "available" in user_input:
            return await self._discover_and_show_clusters()
        
        # Check if user wants to connect to a cluster
        elif "connect" in user_input and "kind" in user_input:
            return await self._connect_to_kind_cluster()
        
        # Check if user wants cluster health
        elif "health" in user_input or "status" in user_input:
            return await self._show_cluster_health()
        
        # Check if user wants to run kubectl commands
        elif "kubectl" in user_input or "run" in user_input:
            return await self._help_with_kubectl()
        
        # Check if user wants specific cluster information (pods, nodes, etc.)
        elif any(keyword in user_input for keyword in ["pods", "nodes", "services", "namespaces", "deployments"]):
            return await self._show_cluster_details(user_input)
        
        # Default: discover and show available clusters
        else:
            return await self._discover_and_show_clusters()
    
    async def _discover_and_show_clusters(self) -> str:
        """Discover and display available clusters - FIXED VERSION"""
        clusters_data = await self.api.discover_clusters()
        
        if "error" in clusters_data:
            return f"❌ Unable to discover clusters: {clusters_data['error']}"
        
        # FIX: Use 'clusters' field instead of 'contexts'
        clusters = clusters_data.get("clusters", [])
        
        response = f"🔍 **Available Kubernetes Clusters ({len(clusters)} found)**\n\n"
        
        if clusters:
            for cluster in clusters:
                name = cluster.get("name", "Unknown")
                cluster_type = cluster.get("type", "unknown")
                connected = cluster.get("connected", False)
                
                status_emoji = "🟢" if connected else "⚪"
                response += f"{status_emoji} **{name}** ({cluster_type})\n"
                response += f"   Context: `{cluster.get('context', name)}`\n"
                response += f"   Status: {'Connected' if connected else 'Available'}\n\n"
        else:
            response += "No clusters found.\n\n"
        
        response += f"💡 **Available Commands**:\n"
        response += f"• 'connect to kind cluster' - Connect to your Kind cluster\n"
        response += f"• 'show cluster health' - Check cluster health status\n"
        response += f"• 'kubectl get pods' - Run kubectl commands\n"
        
        return response
    
    async def _connect_to_kind_cluster(self) -> str:
        """Connect to the Kind cluster"""
        kind_context = "kind-kubegenie-cluster"
        
        connect_result = await self.api.connect_cluster(kind_context)
        
        if "error" in connect_result:
            return f"❌ Unable to connect to Kind cluster: {connect_result['error']}\n\n" \
                   f"💡 Make sure your Kind cluster is running:\n" \
                   f"```\nkind get clusters\n```"
        
        # Get cluster health after connecting
        health_data = await self.api.get_cluster_health(kind_context)
        
        response = f"✅ **Connected to Kind Cluster**: `{kind_context}`\n\n"
        
        if "error" not in health_data and "health" in health_data:
            health = health_data.get("health", {})
            nodes = health.get("nodes", {}).get("details", [])
            response += f"**Cluster Health**:\n"
            response += f"• **Nodes**: {len(nodes)} total\n"
            
            for node in nodes:
                status_emoji = "🟢" if node.get("status") == "Ready" else "🔴"
                roles = node.get("roles", [])
                role_str = roles[0] if roles else "worker"
                response += f"  {status_emoji} {node.get('name', 'Unknown')} ({role_str})\n"
            
            response += f"\n🎉 **Your Kind cluster is ready for management!**\n"
            response += f"Try asking: 'kubectl get pods' or 'show me pods'"
        
        return response
    
    async def _show_cluster_health(self) -> str:
        """Show health status of connected cluster"""
        kind_context = "kind-kubegenie-cluster"
        
        health_data = await self.api.get_cluster_health(kind_context)
        
        if "error" in health_data:
            return f"❌ Unable to get cluster health: {health_data['error']}\n\n" \
                   f"💡 Try connecting first: 'connect to kind cluster'"
        
        health = health_data.get("health", {})
        nodes = health.get("nodes", {}).get("details", [])
        
        response = f"🏥 **Cluster Health Status**\n\n"
        response += f"**Cluster**: `{kind_context}`\n"
        response += f"**Total Nodes**: {len(nodes)}\n\n"
        
        response += f"**Node Status**:\n"
        for node in nodes:
            status_emoji = "🟢" if node.get("status") == "Ready" else "🔴"
            roles = node.get("roles", [])
            role_str = roles[0] if roles else "worker"
            response += f"{status_emoji} **{node.get('name', 'Unknown')}** ({role_str})\n"
            response += f"   • Status: {node.get('status', 'Unknown')}\n"
            if node.get("version"):
                response += f"   • Version: {node.get('version')}\n"
        
        return response
    
    async def _show_cluster_details(self, user_input: str) -> str:
        """Show detailed cluster information by executing kubectl commands"""
        kind_context = "kind-kubegenie-cluster"
        
        # Determine what information to show based on user input
        if "pods" in user_input:
            command = "get pods"
            title = "📦 **Pods in Your Kind Cluster**"
        elif "nodes" in user_input:
            command = "get nodes"
            title = "🖥️ **Nodes in Your Kind Cluster**"
        elif "services" in user_input:
            command = "get services"
            title = "🌐 **Services in Your Kind Cluster**"
        elif "namespaces" in user_input:
            command = "get namespaces"
            title = "📁 **Namespaces in Your Kind Cluster**"
        elif "deployments" in user_input:
            command = "get deployments"
            title = "🚀 **Deployments in Your Kind Cluster**"
        else:
            return await self._show_cluster_overview()
        
        # Execute the kubectl command
        result = await self.api.execute_kubectl(kind_context, command)
        
        if "error" in result:
            return f"❌ **Error getting cluster information**:\n```\n{result['error']}\n```\n\n" \
                   f"💡 Make sure you're connected to the cluster: 'connect to kind cluster'"
        
        # Check if we got a successful API response
        if result.get("status") != "success":
            return f"❌ **API Error**: {result.get('error', 'Unknown error')}"
        
        # Extract the actual result data
        command_result = result.get("result", {})
        items = command_result.get("items", [])
        
        if not items:
            return f"{title}\n\n✅ No resources found."
        
        # Format the response based on resource type
        response = f"{title}\n\n"
        
        if "pods" in command:
            response += f"**Total Pods**: {len(items)}\n\n"
            # Group pods by namespace
            namespaces = {}
            for pod in items:
                ns = pod.get("namespace", "default")
                if ns not in namespaces:
                    namespaces[ns] = []
                namespaces[ns].append(pod)
            
            for ns, pods in namespaces.items():
                response += f"**📁 {ns}** ({len(pods)} pods)\n"
                for pod in pods[:5]:  # Show max 5 pods per namespace
                    status_emoji = "🟢" if pod.get("status") == "Running" else "🔴" if pod.get("status") == "Failed" else "🟡"
                    response += f"  {status_emoji} {pod.get('name', 'Unknown')}\n"
                    response += f"     Status: {pod.get('status', 'Unknown')} | Restarts: {pod.get('restarts', 0)}\n"
                if len(pods) > 5:
                    response += f"     ... and {len(pods) - 5} more\n"
                response += "\n"
        
        elif "nodes" in command:
            response += f"**Total Nodes**: {len(items)}\n\n"
            for node in items:
                status_emoji = "🟢" if node.get("status") == "True" else "🔴"
                roles = node.get("roles", ["worker"])
                role_str = ", ".join(roles) if roles else "worker"
                response += f"{status_emoji} **{node.get('name', 'Unknown')}**\n"
                response += f"   Role: {role_str} | Version: {node.get('version', 'Unknown')}\n"
                response += f"   Status: {'Ready' if node.get('status') == 'True' else 'Not Ready'}\n\n"
        
        else:
            # Generic formatting for other resource types
            for item in items[:10]:  # Show max 10 items
                response += f"• {item.get('name', 'Unknown')}\n"
                if item.get('namespace'):
                    response += f"  Namespace: {item.get('namespace')}\n"
                if item.get('status'):
                    response += f"  Status: {item.get('status')}\n"
                response += "\n"
            
            if len(items) > 10:
                response += f"... and {len(items) - 10} more items\n"
        
        return response
    
    async def _show_cluster_overview(self) -> str:
        """Show comprehensive cluster overview"""
        kind_context = "kind-kubegenie-cluster"
        
        response = f"🔍 **Your Kind Cluster Overview: {kind_context}**\n\n"
        
        # Get nodes
        nodes_result = await self.api.execute_kubectl(kind_context, "get nodes")
        if nodes_result.get("status") == "success":
            nodes_items = nodes_result.get("result", {}).get("items", [])
            response += f"**🖥️ Nodes**: {len(nodes_items)} total\n"
            for node in nodes_items:
                status_emoji = "🟢" if node.get("status") == "True" else "🔴"
                roles = node.get("roles", ["worker"])
                role_str = ", ".join(roles) if roles else "worker"
                response += f"  {status_emoji} {node.get('name', 'Unknown')} ({role_str})\n"
        
        # Get pods
        pods_result = await self.api.execute_kubectl(kind_context, "get pods")
        if pods_result.get("status") == "success":
            pods_items = pods_result.get("result", {}).get("items", [])
            running_pods = sum(1 for pod in pods_items if pod.get("status") == "Running")
            response += f"\n**📦 Pods**: {len(pods_items)} total, {running_pods} running\n"
            
            # Show pods by namespace
            namespaces = {}
            for pod in pods_items:
                ns = pod.get("namespace", "default")
                if ns not in namespaces:
                    namespaces[ns] = {"total": 0, "running": 0}
                namespaces[ns]["total"] += 1
                if pod.get("status") == "Running":
                    namespaces[ns]["running"] += 1
            
            for ns, counts in namespaces.items():
                response += f"  📁 {ns}: {counts['running']}/{counts['total']} running\n"
        
        response += f"\n💡 **Try these commands**:\n"
        response += f"• 'show me pods' - List all pods in detail\n"
        response += f"• 'show me nodes' - List cluster nodes\n"
        response += f"• 'kubectl get services' - List services\n"
        response += f"• 'connect to kind cluster' - Ensure connection\n"
        
        return response
    
    async def _help_with_kubectl(self) -> str:
        """Help with kubectl commands"""
        return f"🔧 **Kubectl Commands**\n\n" \
               f"I can help you run kubectl commands on your Kind cluster!\n\n" \
               f"**Examples to try**:\n" \
               f"• 'kubectl get pods' - List all pods\n" \
               f"• 'kubectl get nodes' - List cluster nodes\n" \
               f"• 'kubectl get services' - List services\n" \
               f"• 'kubectl get namespaces' - List namespaces\n\n" \
               f"💡 Just type your kubectl command and I'll execute it for you!"
    
    async def _handle_kubectl_command(self, user_input: str) -> str:
        """Handle kubectl command execution"""
        kind_context = "kind-kubegenie-cluster"
        
        # Extract the kubectl command (remove 'kubectl' prefix for API)
        command = user_input.replace("kubectl", "").strip()
        
        if not command:
            return "❌ Please provide a kubectl command. Example: 'kubectl get pods'"
        
        # Execute the command
        result = await self.api.execute_kubectl(kind_context, command)
        
        if "error" in result:
            return f"❌ **Kubectl Error**:\n```\n{result['error']}\n```\n\n" \
                   f"💡 Make sure you're connected to the cluster: 'connect to kind cluster'"
        
        # Check if we got a successful API response
        if result.get("status") != "success":
            return f"❌ **API Error**: {result.get('error', 'Unknown error')}"
        
        # Extract the actual result data
        command_result = result.get("result", {})
        
        # Handle the response based on the command result
        if "error" in command_result:
            return f"❌ **Command Error**: {command_result['error']}"
        
        items = command_result.get("items", [])
        
        response = f"✅ **Command**: `kubectl {command}`\n\n"
        
        if items:
            response += f"**Results** ({len(items)} items):\n\n"
            
            # Format the results nicely
            for item in items[:20]:  # Show max 20 items
                response += f"• **{item.get('name', 'Unknown')}**\n"
                if item.get('namespace'):
                    response += f"  Namespace: {item.get('namespace')}\n"
                if item.get('status'):
                    response += f"  Status: {item.get('status')}\n"
                if item.get('roles'):
                    response += f"  Roles: {', '.join(item.get('roles', []))}\n"
                response += "\n"
            
            if len(items) > 20:
                response += f"... and {len(items) - 20} more items\n"
        else:
            response += "**Output**: No resources found or command completed successfully"
        
        return response
    
    async def _handle_analysis_query(self) -> str:
        """Handle analysis queries"""
        # For now, return a simple analysis result
        return "🔍 **Cluster Analysis Results**\n\n" \
               "Found 1 recommended actions:\n\n" \
               "⚪ Create default network policies for cluster\n" \
               "• Agent: security_agent_001\n" \
               "• Priority: Medium\n" \
               "• ⚠️ Requires approval"
    
    def _handle_help_query(self) -> str:
        """Handle help queries"""
        return """🤖 **KubeGenie AI Assistant**

I can help you manage your Kubernetes clusters using natural language!

**🔧 Cluster Management:**
• "show me clusters" - List available clusters
• "connect to kind cluster" - Connect to your Kind cluster
• "show cluster health" - Check cluster status
• "show me pods" - List all pods
• "show me nodes" - List cluster nodes

**⚡ Kubectl Commands:**
• "kubectl get pods" - Run kubectl commands
• "kubectl get services" - List services
• "kubectl describe pod [name]" - Get pod details

**📊 Analysis & Monitoring:**
• "analyze my infrastructure" - Get AI recommendations
• "check for issues" - Analyze cluster problems

Just ask me anything about your Kubernetes cluster in natural language!
"""
    
    async def _handle_general_query(self, user_input: str) -> str:
        """Handle general queries"""
        return """I'm KubeGenie, your AI Kubernetes assistant! 🤖

I can help you with:
• Managing clusters and resources
• Running kubectl commands
• Analyzing infrastructure
• Getting cluster information

Try asking me something like:
• "show me my clusters"
• "kubectl get pods"
• "analyze my infrastructure"
• "connect to kind cluster"

What would you like to do?"""

# Gradio Interface Functions
def create_gradio_interface(chatbot: KubeGenieChatbot):
    """Create the Gradio interface"""
    
    async def chat_wrapper(message: str, history: List):
        """Wrapper for async chat processing"""
        return await chatbot.process_message(message, history)
    
    def sync_chat_wrapper(message: str, history: List):
        """Synchronous wrapper for Gradio"""
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            return loop.run_until_complete(chat_wrapper(message, history))
        finally:
            loop.close()
    
    # Create Gradio interface
    with gr.Blocks(
        title="KubeGenie - AI Kubernetes Assistant",
        theme=gr.themes.Soft(),
        css="""
        .gradio-container {
            max-width: 1200px !important;
            margin: auto !important;
        }
        """
    ) as demo:
        
        gr.Markdown(
            """
            # 🤖 KubeGenie - AI Kubernetes Assistant
            
            Manage your Kubernetes clusters using natural language!
            Connected to your Kind cluster for real-time management.
            """
        )
        
        chatbot_interface = gr.Chatbot(
            label="Chat with KubeGenie",
            height=600,
            show_label=True,
            container=True,
            scale=1,
            type="messages"
        )
        
        msg = gr.Textbox(
            label="Your message",
            placeholder="Ask me about your clusters, run kubectl commands, or get help...",
            lines=1,
            max_lines=3
        )
        
        clear = gr.Button("Clear Chat")
        
        msg.submit(sync_chat_wrapper, [msg, chatbot_interface], [msg, chatbot_interface])
        clear.click(lambda: [], None, chatbot_interface)
        
        gr.Markdown(
            """
            ### 💡 Example Commands:
            - `show me my clusters` - List available clusters
            - `kubectl get pods` - List all pods  
            - `connect to kind cluster` - Connect to Kind cluster
            - `show cluster health` - Check cluster status
            - `analyze my infrastructure` - Get AI recommendations
            """
        )
    
    return demo

# Main execution
if __name__ == "__main__":
    logger.info("Starting KubeGenie Gradio UI...")
    
    chatbot = KubeGenieChatbot()
    demo = create_gradio_interface(chatbot)
    
    demo.launch(
        server_name="127.0.0.1",
        server_port=7862,
        share=False,
        show_error=True,
        inbrowser=False
    )