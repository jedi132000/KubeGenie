"""
UI Components for KubeGenie
Reusable Gradio components and styling
"""

import gradio as gr
from typing import Dict, Any


def create_status_indicator(
    service: str, 
    status: str, 
    color: str = "green"
) -> gr.Markdown:
    """Create a status indicator component"""
    
    status_icons = {
        "active": "✅",
        "pending": "⏳", 
        "error": "❌",
        "warning": "⚠️"
    }
    
    icon = status_icons.get(status, "❓")
    
    return gr.Markdown(f"{icon} **{service}**: {status}")


def create_header_section() -> gr.Markdown:
    """Create the main header section"""
    
    return gr.Markdown("""
    # 🤖 KubeGenie - AI Kubernetes Assistant
    ### LangChain + LangGraph + LangSmith + Gradio Stack
    
    **Current Development:** Step 2 - Basic Chat Interface ✅
    
    Conversational AI for Kubernetes cluster management, cost optimization, and multi-cloud infrastructure.
    """)


def create_footer_section() -> gr.Markdown:
    """Create footer with development status"""
    
    return gr.Markdown("""
    ---
    **Development Status:** 
    🏗️ Step 2/15 | 🤖 Chat: ✅ | 🔗 K8s Client: ⏳ | 🧠 AI Agents: ⏳ | ☁️ Crossplane: ⏳
    
    *Building with frequent commits and step-by-step approach*
    """)


# Custom CSS styling
KUBEGENIE_CSS = """
/* KubeGenie Custom Styling */
.gradio-container {
    max-width: 1200px !important;
    margin: 0 auto;
}

.chat-message {
    font-size: 14px !important;
    line-height: 1.5;
}

.status-indicator {
    background: #f0f9ff;
    border: 1px solid #bae6fd;
    border-radius: 8px;
    padding: 8px 12px;
    margin: 4px 0;
}

.kubegenie-header {
    text-align: center;
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    color: white;
    padding: 20px;
    border-radius: 12px;
    margin-bottom: 20px;
}

.development-status {
    background: #fef3c7;
    border: 1px solid #f59e0b;
    border-radius: 8px;
    padding: 12px;
    margin: 10px 0;
    font-size: 12px;
}
"""


def create_welcome_message() -> str:
    """Create the initial welcome message"""
    
    return """👋 **Welcome to KubeGenie!** 

I'm your AI Kubernetes Assistant, currently in active development.

**What I can discuss right now:**
- 🔍 My capabilities and roadmap
- 📊 Current development status
- ☁️ Planned Crossplane integration
- 🔧 Kubernetes management features

**Try asking:**
- "What can you do?"
- "What's your status?"
- "Tell me about Crossplane"
- "Show me your capabilities"

*Note: I'm currently in Step 2 of 15. Real cluster connectivity and AI agents coming soon!*"""