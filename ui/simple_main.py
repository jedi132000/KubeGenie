"""
Diagnostic version of KubeGenie UI - without asyncio
"""

import gradio as gr
import httpx
import requests
import json
import logging
from datetime import datetime
from typing import List, Dict, Any, Optional, Tuple
import os

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configuration
BACKEND_URL = os.getenv("KUBEGENIE_BACKEND_URL", "http://localhost:8000")
API_BASE = f"{BACKEND_URL}/api/v1"

class SimpleKubeGenieUI:
    """Simplified KubeGenie UI without async complications"""
    
    def __init__(self):
        self.auth_token = None
        self.backend_url = BACKEND_URL
        
    def authenticate(self, username: str, password: str) -> str:
        """Fast synchronous authentication"""
        try:
            # Use requests for faster authentication
            response = requests.post(
                f"{API_BASE}/auth/login",
                data={"username": username, "password": password},
                headers={"Content-Type": "application/x-www-form-urlencoded"},
                timeout=5  # 5 second timeout
            )
            
            if response.status_code == 200:
                data = response.json()
                self.auth_token = data.get("access_token")
                return "✅ Authentication successful!"
            else:
                return f"❌ Authentication failed: {response.text}"
                
        except requests.exceptions.Timeout:
            return f"❌ Authentication timeout - backend took too long to respond"
        except Exception as e:
            logger.error(f"Authentication error: {e}")
            return f"❌ Authentication error: {str(e)}"
    
    def get_cluster_info(self) -> str:
        """Get cluster information synchronously"""
        try:
            headers = {}
            if self.auth_token:
                headers["Authorization"] = f"Bearer {self.auth_token}"
                
            with httpx.Client() as client:
                response = client.get(f"{API_BASE}/k8s/cluster-info", headers=headers)
                
                if response.status_code == 200:
                    cluster_info = response.json()
                    return f"""🚀 **Cluster Information**
    
✅ Status: {cluster_info.get('status', 'Unknown')}
🏷️ Version: {cluster_info.get('version', 'Unknown')}  
🖥️ Nodes: {cluster_info.get('nodes', 'Unknown')}
⚙️ Platform: {cluster_info.get('platform', 'kubernetes')}
"""
                else:
                    return f"❌ Failed to get cluster info: {response.text}"
                    
        except Exception as e:
            logger.error(f"Cluster info error: {e}")
            return f"❌ Error: {str(e)}"
    
    def process_chat_message(self, message: str, history: Optional[List[List[str]]] = None) -> Tuple[str, List[List[str]]]:
        """Process chat message using the REAL OpenAI-powered chat endpoint"""
        try:
            # Initialize history if None - ensure it's always a list
            if history is None or not isinstance(history, list):
                history = []
            
            if not message.strip():
                return "", history
            
            # Call the REAL chat endpoint with OpenAI integration
            response = self._call_real_chat_endpoint(message)
            
            # Update history - ensure we're appending a list of two strings
            history.append([str(message), str(response)])
            
            return "", history
            
        except Exception as e:
            error_response = f"Sorry, I encountered an error: {str(e)}"
            if history is None or not isinstance(history, list):
                history = []
            history.append([str(message), str(error_response)])
            return "", history
    
    def _call_real_chat_endpoint(self, message: str) -> str:
        """Call the real OpenAI-powered chat endpoint"""
        try:
            # Check if we're authenticated
            if not self.auth_token:
                return "⚠️ Please authenticate first using the Login section below."
            
            response = requests.post(
                f"{self.backend_url}/api/v1/chat/message",
                headers={
                    "Authorization": f"Bearer {self.auth_token}",
                    "Content-Type": "application/json"
                },
                json={"message": message},
                timeout=30
            )
            
            if response.status_code == 200:
                chat_response = response.json()
                return chat_response.get("response", "No response received")
            elif response.status_code == 401:
                return "🔒 Authentication failed. Please login again."
            else:
                return f"❌ Backend error (status {response.status_code}): {response.text}"
                
        except Exception as e:
            return f"🔌 Connection error: {str(e)}"
    
    def _handle_user_intent(self, message: str) -> str:
        """Handle user intent synchronously"""
        message_lower = message.lower()
        
        # Cluster status queries
        if any(keyword in message_lower for keyword in ["status", "cluster", "info", "health"]):
            return self._handle_cluster_status()
            
        # Pod management
        elif any(keyword in message_lower for keyword in ["pod", "pods", "list pods"]):
            return self._handle_pods_query()
            
        # Namespace queries
        elif any(keyword in message_lower for keyword in ["namespace", "namespaces"]):
            return self._handle_namespace_query()
            
        # Help and general queries
        else:
            return self._handle_general_query(message)
    
    def _handle_cluster_status(self) -> str:
        """Handle cluster status queries"""
        return self.get_cluster_info()
    
    def _handle_pods_query(self) -> str:
        """Handle pod queries"""
        try:
            headers = {}
            if self.auth_token:
                headers["Authorization"] = f"Bearer {self.auth_token}"
                
            with httpx.Client() as client:
                response = client.get(f"{API_BASE}/k8s/pods", headers=headers)
                
                if response.status_code == 200:
                    pods = response.json()
                    if not pods:
                        return "📦 No pods found in default namespace"
                    
                    result = "📦 **Pods in default namespace:**\n\n"
                    for pod in pods[:5]:  # Limit to first 5 pods
                        status_icon = "✅" if pod['status'] == "Running" else "⚠️"
                        result += f"{status_icon} **{pod['name']}**\n"
                        result += f"   Status: {pod['status']} | Ready: {pod['ready']}\n"
                        result += f"   Node: {pod.get('node', 'Unknown')}\n\n"
                    
                    return result
                else:
                    return f"❌ Failed to get pods: {response.text}"
                    
        except Exception as e:
            return f"❌ Error getting pods: {str(e)}"
    
    def _handle_namespace_query(self) -> str:
        """Handle namespace queries"""
        try:
            headers = {}
            if self.auth_token:
                headers["Authorization"] = f"Bearer {self.auth_token}"
                
            with httpx.Client() as client:
                response = client.get(f"{API_BASE}/k8s/namespaces", headers=headers)
                
                if response.status_code == 200:
                    namespaces = response.json()
                    result = "🏷️ **Available Namespaces:**\n\n"
                    for ns in namespaces:
                        status_icon = "✅" if ns['status'] == "Active" else "⚠️"
                        result += f"{status_icon} **{ns['name']}** ({ns['status']})\n"
                    
                    return result
                else:
                    return f"❌ Failed to get namespaces: {response.text}"
                    
        except Exception as e:
            return f"❌ Error getting namespaces: {str(e)}"
    
    def _handle_general_query(self, message: str) -> str:
        """Handle general queries"""
        return f"""👋 **Hi! I'm KubeGenie, your Kubernetes assistant!**

I can help you manage your Kubernetes cluster. Here are some things you can ask:

**📊 Cluster Information:**
- "What's the cluster status?"
- "Show me cluster info"

**📦 Pod Management:**
- "List all pods"
- "Show me pods"

**🏷️ Namespaces:**
- "Show me all namespaces"
- "List namespaces"

Just ask me what you'd like to do! 🎯

*Your message: "{message}"*
"""

# Initialize the UI
kubegenie = SimpleKubeGenieUI()

def create_simple_ui():
    """Create simplified Gradio interface"""
    
    with gr.Blocks(title="KubeGenie - Smart Kubernetes Management") as demo:
        
        gr.Markdown("""
        # 🧞‍♂️ KubeGenie - Smart Kubernetes Management
        
        **Manage your Kubernetes cluster through natural language conversations**
        """)
        
        with gr.Row():
            with gr.Column(scale=2):
                # Main chat interface
                chatbot = gr.Chatbot(
                    label="💬 Chat with KubeGenie",
                    height=400
                )
                
                msg_input = gr.Textbox(
                    label="Message",
                    placeholder="Ask me anything about your Kubernetes cluster..."
                )
                
                send_btn = gr.Button("Send 🚀", variant="primary")
                
                # Example buttons
                with gr.Row():
                    status_btn = gr.Button("Cluster Status")
                    pods_btn = gr.Button("List Pods") 
                    ns_btn = gr.Button("List Namespaces")
            
            with gr.Column(scale=1):
                # Authentication section
                gr.Markdown("### 🔐 Authentication")
                username_input = gr.Textbox(label="Username", value="admin")
                password_input = gr.Textbox(label="Password", type="password", value="admin123")
                auth_btn = gr.Button("Login")
                auth_status = gr.Textbox(label="Status", interactive=False)
                
                # Quick info section
                gr.Markdown("### 🏷️ Quick Info")
                info_btn = gr.Button("Get Cluster Info")
                info_display = gr.Textbox(label="Information", lines=6, interactive=False)
        
        # Event handlers
        def handle_auth(username, password):
            return kubegenie.authenticate(username, password)
        
        def handle_message(message, history):
            _, new_history = kubegenie.process_chat_message(message, history)
            return "", new_history
        
        def get_info():
            return kubegenie.get_cluster_info()
        
        def quick_status(history):
            _, new_history = kubegenie.process_chat_message("What's the cluster status?", history)
            return new_history
        
        def quick_pods(history):
            _, new_history = kubegenie.process_chat_message("List all pods", history)
            return new_history
            
        def quick_namespaces(history):
            _, new_history = kubegenie.process_chat_message("Show me all namespaces", history)
            return new_history
        
        # Wire up events
        auth_btn.click(handle_auth, inputs=[username_input, password_input], outputs=[auth_status])
        info_btn.click(get_info, outputs=[info_display])
        
        send_btn.click(handle_message, inputs=[msg_input, chatbot], outputs=[msg_input, chatbot])
        msg_input.submit(handle_message, inputs=[msg_input, chatbot], outputs=[msg_input, chatbot])
        
        status_btn.click(quick_status, inputs=[chatbot], outputs=[chatbot])
        pods_btn.click(quick_pods, inputs=[chatbot], outputs=[chatbot])  
        ns_btn.click(quick_namespaces, inputs=[chatbot], outputs=[chatbot])
    
    return demo

if __name__ == "__main__":
    print("🧞‍♂️ Starting KubeGenie Simple UI...")
    print(f"🔗 Backend URL: {BACKEND_URL}")
    print("🌐 UI will be available at: http://localhost:7862")
    
    demo = create_simple_ui()
    demo.launch(server_port=7875, share=False)