"""
Fixed KubeGenie Chat Interface
Clean implementation with proper Gradio messages format

Step 3: Enhanced with Kubernetes client integration (Fixed)
"""

import gradio as gr
import os
from typing import List, Dict
from datetime import datetime

# Import Kubernetes operations (with fallback)
try:
    from ..tools.k8s_operations import KubernetesOperations
    KUBERNETES_AVAILABLE = True
except ImportError:
    KUBERNETES_AVAILABLE = False
    print("⚠️ Kubernetes client not available - install requirements.txt")


class KubeGenieChatFixed:
    """Main chat interface for KubeGenie AI Kubernetes Assistant - Fixed Version"""
    
    def __init__(self):
        self.conversation_history: List[Dict[str, str]] = []
        
        # Initialize Kubernetes operations if available
        if KUBERNETES_AVAILABLE:
            try:
                self.k8s_ops = KubernetesOperations()
            except Exception:
                self.k8s_ops = None
                print("⚠️ Could not initialize Kubernetes operations")
        else:
            self.k8s_ops = None
        
    def process_user_message(self, message: str, history: List[Dict[str, str]]) -> tuple:
        """Process user message and return updated history"""
        
        if not message.strip():
            return history, ""
        
        # Enhanced command recognition with Kubernetes integration
        message_lower = message.lower()
        
        # Check if Kubernetes operations are available
        k8s_status = "✅ Ready" if KUBERNETES_AVAILABLE else "❌ Not available"
        
        # Generate response based on message
        response = self._generate_response(message, message_lower, k8s_status)
        
        # Add both user message and assistant response to history
        new_history = history + [
            {"role": "user", "content": message},
            {"role": "assistant", "content": response}
        ]
        
        return new_history, ""
    
    def _generate_response(self, message: str, message_lower: str, k8s_status: str) -> str:
        """Generate response based on user message"""
        
        if any(word in message_lower for word in ['hello', 'hi', 'hey']):
            return f"""👋 Hello! I'm KubeGenie, your AI Kubernetes Assistant.

I can help you with:
🔍 **Cluster monitoring** - Check pod status, node health, resource usage
💰 **Cost optimization** - Find unused resources, rightsizing recommendations  
🔒 **Security analysis** - RBAC checks, policy compliance, vulnerability scans
☁️ **Multi-cloud management** - Provision and manage cloud infrastructure with Crossplane

**Current Status:**
- ✅ Chat interface active
- {k8s_status} Kubernetes client (Step 3)
- ⏳ LangChain agents (Step 4+)

Try asking: "Connect to cluster" or "Show cluster status" """

        elif 'connect' in message_lower and 'cluster' in message_lower:
            if not KUBERNETES_AVAILABLE:
                return "❌ Kubernetes client not available. Install requirements: `pip install -r requirements.txt`"
            
            if not self.k8s_ops:
                return "❌ Kubernetes operations not initialized. Check configuration."
            
            try:
                return self.k8s_ops.connect_to_cluster()
            except Exception as e:
                return f"❌ Connection failed: {str(e)}\n\nTroubleshooting:\n- Check kubectl config: `kubectl cluster-info`\n- Verify kubeconfig: `~/.kube/config`"
        
        elif 'cluster' in message_lower and ('status' in message_lower or 'overview' in message_lower):
            if not KUBERNETES_AVAILABLE or not self.k8s_ops:
                return "❌ Kubernetes client not available."
            
            if not self.k8s_ops.is_connected():
                return "❌ Not connected to cluster. Ask me to 'connect to cluster' first."
            
            return self.k8s_ops.get_cluster_overview()
        
        elif 'nodes' in message_lower or 'node' in message_lower:
            if not KUBERNETES_AVAILABLE or not self.k8s_ops or not self.k8s_ops.is_connected():
                return "❌ Connect to cluster first: ask me to 'connect to cluster'"
            
            return self.k8s_ops.list_cluster_nodes()
        
        elif 'pods' in message_lower and 'all' in message_lower:
            if not KUBERNETES_AVAILABLE or not self.k8s_ops or not self.k8s_ops.is_connected():
                return "❌ Connect to cluster first: ask me to 'connect to cluster'"
            
            return self.k8s_ops.list_all_pods()
        
        elif 'pods' in message_lower:
            if not KUBERNETES_AVAILABLE or not self.k8s_ops or not self.k8s_ops.is_connected():
                return "❌ Connect to cluster first: ask me to 'connect to cluster'"
            
            # Check if specific namespace mentioned
            namespace = "default"
            if 'namespace' in message_lower:
                words = message_lower.split()
                try:
                    ns_index = words.index('namespace')
                    if ns_index + 1 < len(words):
                        namespace = words[ns_index + 1]
                except ValueError:
                    pass
            
            return self.k8s_ops.list_pods_in_namespace(namespace)
        
        elif 'namespaces' in message_lower or 'namespace' in message_lower:
            if not KUBERNETES_AVAILABLE or not self.k8s_ops or not self.k8s_ops.is_connected():
                return "❌ Connect to cluster first: ask me to 'connect to cluster'"
            
            return self.k8s_ops.list_namespaces()
        
        elif 'status' in message_lower or 'health' in message_lower:
            # Try to get cluster status if connected
            cluster_status = ""
            if KUBERNETES_AVAILABLE and self.k8s_ops and self.k8s_ops.is_connected():
                cluster_status = "\n\n" + self.k8s_ops.get_cluster_overview()
            elif KUBERNETES_AVAILABLE and self.k8s_ops:
                cluster_status = "\n\n" + self.k8s_ops.get_connection_status()
            
            return f"""📊 **System Status:**
- 🤖 KubeGenie Chat: ✅ Active
- 🔗 Kubernetes Client: {k8s_status}
- 🧠 LangChain Agents: ⏳ In development (Step 4+)
- 📈 LangSmith Observability: ⏳ Pending (Step 10)

**Next Steps:**
Step 2: ✅ Basic Gradio interface 
Step 3: ✅ Kubernetes client setup (current)
Step 4: 🔄 LangChain basic agent{cluster_status}"""

        elif 'capabilities' in message_lower or 'what can you do' in message_lower:
            return """🚀 **KubeGenie Capabilities (Full Roadmap):**

**Phase 1: Foundation**
- ✅ Conversational chat interface
- ✅ Kubernetes cluster integration
- 🔄 AI agent framework (LangChain)
- 🔄 Multi-agent routing (LangGraph)

**Phase 2: Core Agents**
- 🔄 Monitoring Agent: Real-time cluster health
- 🔄 Cost Agent: Resource optimization
- 🔄 Security Agent: Compliance & vulnerability scanning

**Phase 3: Advanced Features**
- 🔄 Multi-cluster management
- 🔄 Crossplane integration (AWS, GCP, Azure)
- 🔄 Advanced workflows & automation
- 🔄 Production-ready deployment

**Current Progress:** Step 3 of 15 complete"""

        elif 'crossplane' in message_lower or 'cloud' in message_lower:
            return """☁️ **Crossplane Multi-Cloud Integration:**

**Planned for Step 13** - This will be a game-changer!

**What Crossplane Adds:**
- 🌐 **Multi-cloud provisioning**: AWS, GCP, Azure resources via Kubernetes APIs
- 🔧 **Infrastructure as Code**: Declarative cloud resource management
- 🎛️ **Platform Engineering**: Self-service infrastructure for dev teams
- 💰 **Cross-cloud cost optimization**: Unified cost management
- 🔒 **Policy-driven governance**: Automated compliance across clouds

**Example Future Commands:**
- "Create a staging environment in GCP"
- "Add S3 and RDS to payments namespace"  
- "Show cloud cost breakdown by team"
- "Provision disaster recovery in another region" """

        else:
            return f"""🤔 I understand you said: "{message}"

**Current Status:** I'm in Step 3 of 15 - Kubernetes integration active!

**Available Commands:**
- "Connect to cluster" - Connect to your Kubernetes cluster
- "Show cluster status" - Get comprehensive cluster overview
- "List nodes" - See all cluster nodes
- "List pods" - Show pods in default namespace
- "List all pods" - Show pods across all namespaces
- "List namespaces" - Show all cluster namespaces

**Try asking:**
- "Hello" or "What can you do?"
- "Show me cluster status"
- "Tell me about Crossplane integration" """

    def create_interface(self) -> gr.Blocks:
        """Create and configure the Gradio chat interface"""
        
        # Custom CSS for KubeGenie styling
        custom_css = """
        .gradio-container {
            max-width: 1200px !important;
        }
        .chat-message {
            font-size: 14px !important;
        }
        """
        
        # Create the chat interface
        with gr.Blocks(
            title="KubeGenie - AI Kubernetes Assistant",
            theme=gr.themes.Soft(),
            css=custom_css
        ) as interface:
            
            gr.Markdown("""
            # 🤖 KubeGenie - AI Kubernetes Assistant
            ### LangChain + LangGraph + LangSmith + Gradio Stack
            
            **Current Status:** Step 3 - Kubernetes Client Integration ✅
            
            Chat with your AI Kubernetes assistant for cluster management, cost optimization, and security analysis.
            """)
            
            # Chat interface with proper messages format
            chatbot = gr.Chatbot(
                value=[{"role": "assistant", "content": "👋 Welcome to KubeGenie! I'm your AI Kubernetes Assistant. Ask me about cluster status, capabilities, or what I can help you with."}],
                height=500,
                show_label=False,
                type="messages"
            )
            
            # Message input
            msg = gr.Textbox(
                placeholder="Ask me about Kubernetes clusters, cost optimization, security, or Crossplane integration...",
                show_label=False,
                container=False
            )
            
            # Status indicators
            with gr.Row():
                k8s_indicator = "✅ Ready" if KUBERNETES_AVAILABLE else "❌ Not available"
                gr.Markdown(f"**Status:** 🤖 Chat: ✅ | 🔗 K8s: {k8s_indicator} | 🧠 Agents: ⏳ | 📊 Observability: ⏳")
            
            # Handle message submission
            msg.submit(
                fn=self.process_user_message,
                inputs=[msg, chatbot],
                outputs=[chatbot, msg]
            )
            
        return interface


def main():
    """Launch the KubeGenie chat interface"""
    print("🚀 Starting KubeGenie Chat Interface (Fixed Version)...")
    print("📍 Step 3: Kubernetes client integration")
    
    # Initialize chat interface
    chat = KubeGenieChatFixed()
    interface = chat.create_interface()
    
    # Launch with configuration - find available port
    port = int(os.environ.get("GRADIO_SERVER_PORT", 7863))
    interface.launch(
        server_name="127.0.0.1",
        server_port=port,
        share=False,
        show_api=False,
        quiet=False
    )


if __name__ == "__main__":
    main()