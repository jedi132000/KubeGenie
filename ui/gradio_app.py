"""
Gradio UI for KubeGenie

A modern, interactive web interface built with Gradio for the KubeGenie 
Kubernetes and Crossplane automation agent.
"""

import gradio as gr
import requests
import json
import pandas as pd
from typing import List, Dict, Any, Tuple
import logging
import os
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configuration
API_BASE_URL = os.getenv("KUBEGENIE_API_URL", "http://localhost:8000")

class KubeGenieUI:
    """KubeGenie Gradio UI Class"""
    
    def __init__(self):
        self.chat_history = []
        
    def process_chat_message(self, message: str, history: List[List[str]]) -> Tuple[str, List[List[str]]]:
        """Process a chat message and return response with updated history"""
        try:
            # Add user message to history
            history.append([message, ""])
            
            # Call the backend API
            response = requests.post(
                f"{API_BASE_URL}/api/v1/chat/message",
                json={"message": message},
                timeout=30
            )
            response.raise_for_status()
            
            data = response.json()
            bot_response = data.get("response", "Sorry, I couldn't process that request.")
            
            # Add actions information if available
            if data.get("actions"):
                bot_response += "\n\n**Actions to be performed:**\n"
                for i, action in enumerate(data["actions"], 1):
                    bot_response += f"{i}. {action['type']}\n"
                    for key, value in action.get("parameters", {}).items():
                        bot_response += f"   • {key}: {value}\n"
            
            # Add suggestions if available
            if data.get("suggestions"):
                bot_response += "\n\n**Suggestions:**\n"
                for suggestion in data["suggestions"]:
                    bot_response += f"• {suggestion}\n"
            
            # Update the last message in history with bot response
            history[-1][1] = bot_response
            
            return "", history
            
        except requests.exceptions.RequestException as e:
            error_msg = f"❌ Error communicating with KubeGenie API: {str(e)}"
            history[-1][1] = error_msg
            return "", history
        except Exception as e:
            error_msg = f"❌ Unexpected error: {str(e)}"
            history[-1][1] = error_msg
            return "", history
    
    def get_pods(self, namespace: str = "default") -> str:
        """Get pods in a namespace and return as formatted text"""
        try:
            response = requests.get(
                f"{API_BASE_URL}/api/v1/k8s/pods",
                params={"namespace": namespace},
                timeout=30
            )
            response.raise_for_status()
            
            pods = response.json()
            
            if not pods:
                return f"No pods found in namespace '{namespace}'"
            
            # Create a formatted table
            result = f"**Pods in namespace '{namespace}':**\n\n"
            result += "| Name | Status | Ready | Restarts | Age |\n"
            result += "|------|--------|-------|----------|-----|\n"
            
            for pod in pods:
                result += f"| {pod['name']} | {pod['status']} | {pod['ready']} | {pod['restarts']} | {pod['age']} |\n"
            
            return result
            
        except requests.exceptions.RequestException as e:
            return f"❌ Error: {str(e)}"
    
    def deploy_application(self, name: str, image: str, replicas: int, namespace: str) -> str:
        """Deploy an application to Kubernetes"""
        try:
            response = requests.post(
                f"{API_BASE_URL}/api/v1/k8s/deployments",
                json={
                    "name": name,
                    "image": image,
                    "replicas": replicas,
                    "namespace": namespace
                },
                timeout=30
            )
            response.raise_for_status()
            
            data = response.json()
            return f"✅ Successfully deployed {name}\n• Image: {image}\n• Replicas: {replicas}\n• Namespace: {namespace}"
            
        except requests.exceptions.RequestException as e:
            return f"❌ Error deploying application: {str(e)}"
    
    def scale_deployment(self, name: str, replicas: int, namespace: str) -> str:
        """Scale a deployment"""
        try:
            response = requests.patch(
                f"{API_BASE_URL}/api/v1/k8s/deployments/{name}/scale",
                json={"replicas": replicas},
                params={"namespace": namespace},
                timeout=30
            )
            response.raise_for_status()
            
            return f"✅ Successfully scaled {name} to {replicas} replicas in namespace {namespace}"
            
        except requests.exceptions.RequestException as e:
            return f"❌ Error scaling deployment: {str(e)}"
    
    def list_crossplane_resources(self) -> str:
        """List Crossplane resources"""
        try:
            response = requests.get(
                f"{API_BASE_URL}/api/v1/crossplane/resources",
                timeout=30
            )
            response.raise_for_status()
            
            resources = response.json()
            
            if not resources:
                return "No Crossplane resources found"
            
            result = "**Crossplane Resources:**\n\n"
            result += "| Name | Provider | Type | Status | Endpoint |\n"
            result += "|------|----------|------|--------|----------|\n"
            
            for resource in resources:
                result += f"| {resource['name']} | {resource['provider']} | {resource['resource_type']} | {resource['status']} | {resource.get('endpoint', 'N/A')} |\n"
            
            return result
            
        except requests.exceptions.RequestException as e:
            return f"❌ Error: {str(e)}"
    
    def provision_resource(self, name: str, provider: str, resource_type: str) -> str:
        """Provision a cloud resource via Crossplane"""
        try:
            response = requests.post(
                f"{API_BASE_URL}/api/v1/crossplane/resources",
                json={
                    "name": name,
                    "provider": provider,
                    "resource_type": resource_type,
                    "parameters": {}
                },
                timeout=30
            )
            response.raise_for_status()
            
            data = response.json()
            return f"✅ Provisioning {resource_type} resource: {name}\n• Provider: {provider}\n• Status: {data.get('status', 'unknown')}"
            
        except requests.exceptions.RequestException as e:
            return f"❌ Error provisioning resource: {str(e)}"
    
    def get_cluster_status(self, namespace: str = "default") -> str:
        """Get cluster status overview"""
        try:
            # Get pods
            pods_response = requests.get(
                f"{API_BASE_URL}/api/v1/k8s/pods",
                params={"namespace": namespace},
                timeout=30
            )
            pods_response.raise_for_status()
            pods = pods_response.json()
            
            # Get events
            events_response = requests.get(
                f"{API_BASE_URL}/api/v1/k8s/events",
                params={"namespace": namespace},
                timeout=30
            )
            events_response.raise_for_status()
            events = events_response.json()
            
            # Create status summary
            result = f"**Cluster Status - Namespace: {namespace}**\n\n"
            
            # Pod summary
            running_pods = len([p for p in pods if p["status"] == "Running"])
            total_pods = len(pods)
            result += f"**Pods:** {running_pods}/{total_pods} running\n\n"
            
            # Recent events
            if events:
                result += "**Recent Events:**\n"
                for event in events[:5]:  # Show last 5 events
                    event_type = "🔴" if event["type"] == "Warning" else "🟢"
                    result += f"{event_type} {event['type']}: {event['message']}\n"
            
            return result
            
        except requests.exceptions.RequestException as e:
            return f"❌ Error getting cluster status: {str(e)}"

def create_kubegenie_ui():
    """Create and configure the Gradio interface"""
    
    ui = KubeGenieUI()
    
    with gr.Blocks(
        title="KubeGenie - Smart Kubernetes Automation",
        theme=gr.themes.Soft(),
        css="""
        .gradio-container {
            max-width: 1200px !important;
        }
        .chat-message {
            padding: 10px;
            margin: 5px 0;
            border-radius: 10px;
        }
        """
    ) as app:
        
        # Header
        gr.Markdown(
            """
            # 🧞‍♂️ KubeGenie
            ### Smart Kubernetes and Crossplane Automation Agent
            
            Interact with your Kubernetes clusters and provision cloud infrastructure using natural language commands.
            """
        )
        
        with gr.Tabs():
            
            # Chat Tab
            with gr.Tab("💬 Chat"):
                gr.Markdown("### Conversational Kubernetes Management")
                gr.Markdown("Ask me anything! Try: *'deploy nginx with 3 replicas'*, *'scale redis to 5 replicas'*, or *'show cluster status'*")
                
                chatbot = gr.Chatbot(
                    [],
                    elem_id="chatbot",
                    bubble_full_width=False,
                    height=500
                )
                
                with gr.Row():
                    msg = gr.Textbox(
                        placeholder="Type your message here... (e.g., 'deploy nginx with 3 replicas')",
                        container=False,
                        scale=4
                    )
                    submit_btn = gr.Button("Send", variant="primary", scale=1)
                
                # Chat functionality
                msg.submit(ui.process_chat_message, [msg, chatbot], [msg, chatbot])
                submit_btn.click(ui.process_chat_message, [msg, chatbot], [msg, chatbot])
                
                # Quick action buttons
                with gr.Row():
                    gr.Button("💡 Get Suggestions").click(
                        lambda: ("What can you help me with?", []),
                        outputs=[msg, chatbot]
                    )
                    gr.Button("📊 Cluster Status").click(
                        lambda: ("show cluster status", []),
                        outputs=[msg, chatbot]
                    )
                    gr.Button("🚀 List Pods").click(
                        lambda: ("list all pods", []),
                        outputs=[msg, chatbot]
                    )
            
            # Kubernetes Tab
            with gr.Tab("☸️ Kubernetes"):
                gr.Markdown("### Direct Kubernetes Operations")
                
                with gr.Row():
                    with gr.Column(scale=1):
                        gr.Markdown("#### 📋 View Resources")
                        
                        with gr.Group():
                            namespace_input = gr.Textbox(
                                value="default",
                                label="Namespace",
                                placeholder="default"
                            )
                            pods_btn = gr.Button("Get Pods", variant="primary")
                            pods_output = gr.Markdown()
                            
                        pods_btn.click(ui.get_pods, inputs=[namespace_input], outputs=[pods_output])
                        
                        status_btn = gr.Button("Get Cluster Status")
                        status_output = gr.Markdown()
                        status_btn.click(ui.get_cluster_status, inputs=[namespace_input], outputs=[status_output])
                    
                    with gr.Column(scale=1):
                        gr.Markdown("#### 🚀 Deploy Application")
                        
                        with gr.Group():
                            deploy_name = gr.Textbox(label="Application Name", placeholder="my-app")
                            deploy_image = gr.Textbox(label="Container Image", placeholder="nginx:latest")
                            deploy_replicas = gr.Number(label="Replicas", value=1, precision=0)
                            deploy_namespace = gr.Textbox(label="Namespace", value="default")
                            deploy_btn = gr.Button("Deploy", variant="primary")
                            deploy_output = gr.Markdown()
                            
                        deploy_btn.click(
                            ui.deploy_application,
                            inputs=[deploy_name, deploy_image, deploy_replicas, deploy_namespace],
                            outputs=[deploy_output]
                        )
                        
                        gr.Markdown("#### ⚖️ Scale Deployment")
                        
                        with gr.Group():
                            scale_name = gr.Textbox(label="Deployment Name", placeholder="my-app")
                            scale_replicas = gr.Number(label="New Replicas", value=3, precision=0)
                            scale_namespace = gr.Textbox(label="Namespace", value="default")
                            scale_btn = gr.Button("Scale", variant="secondary")
                            scale_output = gr.Markdown()
                            
                        scale_btn.click(
                            ui.scale_deployment,
                            inputs=[scale_name, scale_replicas, scale_namespace],
                            outputs=[scale_output]
                        )
            
            # Crossplane Tab
            with gr.Tab("☁️ Crossplane"):
                gr.Markdown("### Cloud Resource Provisioning")
                
                with gr.Row():
                    with gr.Column(scale=1):
                        gr.Markdown("#### 📋 View Resources")
                        
                        list_resources_btn = gr.Button("List Resources", variant="primary")
                        resources_output = gr.Markdown()
                        
                        list_resources_btn.click(ui.list_crossplane_resources, outputs=[resources_output])
                    
                    with gr.Column(scale=1):
                        gr.Markdown("#### 🏗️ Provision Resource")
                        
                        with gr.Group():
                            resource_name = gr.Textbox(label="Resource Name", placeholder="my-s3-bucket")
                            resource_provider = gr.Dropdown(
                                choices=["aws", "gcp", "azure"],
                                label="Cloud Provider",
                                value="aws"
                            )
                            resource_type = gr.Dropdown(
                                choices=["s3", "rds", "gke", "aks", "vpc", "subnet"],
                                label="Resource Type",
                                value="s3"
                            )
                            provision_btn = gr.Button("Provision", variant="primary")
                            provision_output = gr.Markdown()
                            
                        provision_btn.click(
                            ui.provision_resource,
                            inputs=[resource_name, resource_provider, resource_type],
                            outputs=[provision_output]
                        )
            
            # Status Tab
            with gr.Tab("📊 Status"):
                gr.Markdown("### System Status & Monitoring")
                
                # Auto-refresh status every 30 seconds
                with gr.Row():
                    with gr.Column():
                        gr.Markdown("#### 🔄 Real-time Status")
                        refresh_btn = gr.Button("Refresh Status", variant="primary")
                        
                        # System health
                        health_output = gr.Markdown("Loading system status...")
                        
                        def get_system_health():
                            try:
                                response = requests.get(f"{API_BASE_URL}/health", timeout=10)
                                if response.status_code == 200:
                                    data = response.json()
                                    return f"✅ **KubeGenie Backend:** {data.get('status', 'unknown').title()}\n• Version: {data.get('version', '1.0.0')}\n• Service: {data.get('service', 'kubegenie-backend')}"
                                else:
                                    return "❌ **Backend Status:** Unavailable"
                            except Exception as e:
                                return f"❌ **Backend Status:** Error - {str(e)}"
                        
                        refresh_btn.click(get_system_health, outputs=[health_output])
                        
                        # Load initial status
                        app.load(get_system_health, outputs=[health_output])
        
        # Footer
        gr.Markdown(
            """
            ---
            **KubeGenie v1.0.0** - Smart Kubernetes and Crossplane Automation Agent  
            💡 *Tip: Use natural language in the chat to interact with your infrastructure*
            """
        )
    
    return app

if __name__ == "__main__":
    # Create and launch the Gradio app
    app = create_kubegenie_ui()
    
    # Launch configuration
    app.launch(
        server_name="0.0.0.0",
        server_port=7860,
        share=False,  # Set to True for public sharing
        show_error=True,
        show_tips=True,
        enable_queue=True
    )