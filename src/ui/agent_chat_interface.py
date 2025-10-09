"""
KubeGenie Agent-powered Chat Interface
Gradio interface integrated with LangChain agent

Step 4: LangChain agent integration with Gradio
"""

import gradio as gr
import asyncio
import os
from datetime import datetime
from typing import List, Tuple, Optional, Dict

# Load environment variables from .env file
try:
    from dotenv import load_dotenv
    load_dotenv()
    print("✅ Environment variables loaded from .env")
except ImportError:
    print("⚠️ python-dotenv not available - using system environment")

# Import our agent
try:
    import sys
    import os
    sys.path.append(os.path.dirname(os.path.dirname(__file__)))
    from agents.base_agent import KubeGenieAgent
    AGENT_AVAILABLE = True
except ImportError as e:
    AGENT_AVAILABLE = False
    print(f"⚠️ KubeGenieAgent not available: {e}")


class KubeGenieAgentChat:
    """Enhanced chat interface with LangChain agent integration"""
    
    def __init__(self):
        self.agent = None
        self.initialization_status = "🔄 Initializing..."
        
        if AGENT_AVAILABLE:
            try:
                self.agent = KubeGenieAgent()
                self.initialization_status = self._get_status_message()
            except Exception as e:
                self.initialization_status = f"❌ Agent initialization failed: {str(e)}"
        else:
            self.initialization_status = "❌ Agent not available - check imports"
    
    def _get_status_message(self) -> str:
        """Get comprehensive status message"""
        if not self.agent:
            return "❌ Agent not initialized"
        
        status = self.agent.get_connection_status()
        
        parts = ["🤖 **KubeGenie Agent Status:**"]
        
        # LangChain status
        if status.get("langchain_available") and status.get("llm_initialized"):
            parts.append("✅ LangChain Agent: Active")
        else:
            parts.append("⚠️ LangChain Agent: Fallback mode")
        
        # Kubernetes status
        if status.get("k8s_available"):
            if status.get("k8s_connected"):
                parts.append("✅ Kubernetes: Connected")
            else:
                parts.append("🔌 Kubernetes: Available (not connected)")
        else:
            parts.append("❌ Kubernetes: Not available")
        
        # Session info
        parts.append(f"🆔 Session: {status.get('session_id', 'Unknown')}")
        
        return "\n".join(parts)
    
    def process_message(self, message: str, chat_history: List[Dict[str, str]]) -> Tuple[List[Dict[str, str]], str]:
        """Process user message and return updated chat history"""
        
        if not message.strip():
            return chat_history, ""
        
        # Get AI response
        if self.agent:
            ai_response = self.agent.chat(message)
        else:
            ai_response = "❌ Agent not available. Please check the setup."
        
        # Update chat history with messages format
        updated_history = chat_history + [
            {"role": "user", "content": message},
            {"role": "assistant", "content": ai_response}
        ]
        
        return updated_history, ""  # Return empty string to clear input
    
    def get_example_prompts(self) -> List[str]:
        """Get list of example prompts for users"""
        return [
            "Hello! What can you help me with?",
            "Connect to my Kubernetes cluster",
            "Show me the cluster status",
            "List all nodes in the cluster",
            "Show pods in the kube-system namespace",
            "List all namespaces",
            "What pods are running?",
            "Help me troubleshoot my cluster",
            "Explain Kubernetes concepts",
            "Reset our conversation"
        ]
    
    def create_interface(self) -> gr.Blocks:
        """Create and configure Gradio interface"""
        
        with gr.Blocks(
            title="KubeGenie - AI Kubernetes Assistant",
            css="""
                .status-box { 
                    padding: 15px; 
                    margin: 10px 0; 
                    border-radius: 8px; 
                    background: #f0f8ff; 
                    border-left: 4px solid #007acc; 
                }
                .example-btn { 
                    margin: 2px; 
                    font-size: 0.9em; 
                }
                .main-container { 
                    max-width: 1200px; 
                    margin: 0 auto; 
                }
            """
        ) as interface:
            
            gr.Markdown("""
            # 🤖 KubeGenie - AI Kubernetes Assistant
            
            **Powered by LangChain + OpenAI + Gradio**
            
            Your intelligent companion for Kubernetes cluster management through natural conversation.
            """, elem_classes=["main-container"])
            
            # Status display
            status_display = gr.Markdown(
                value=self.initialization_status,
                elem_classes=["status-box"]
            )
            
            # Main chat interface
            with gr.Row():
                with gr.Column(scale=4):
                    chatbot = gr.Chatbot(
                        value=[],
                        height=500,
                        show_label=False,
                        container=True,
                        show_copy_button=True,
                        bubble_full_width=False,
                        type="messages"
                    )
                    
                    with gr.Row():
                        msg_input = gr.Textbox(
                            placeholder="Ask me anything about your Kubernetes cluster...",
                            show_label=False,
                            container=False,
                            scale=4
                        )
                        send_btn = gr.Button("Send", variant="primary", scale=1)
                
                with gr.Column(scale=1):
                    gr.Markdown("### 💡 Quick Actions")
                    
                    # Example buttons
                    example_buttons = []
                    for example in self.get_example_prompts():
                        btn = gr.Button(
                            example,
                            elem_classes=["example-btn"],
                            size="sm"
                        )
                        example_buttons.append(btn)
                    
                    gr.Markdown("### ⚡ Quick Commands")
                    refresh_status_btn = gr.Button("🔄 Refresh Status", size="sm")
                    clear_chat_btn = gr.Button("🗑️ Clear Chat", size="sm")
                    reset_agent_btn = gr.Button("🔄 Reset Agent", size="sm")
            
            # Event handlers
            def submit_message(message, history):
                return self.process_message(message, history)
            
            def use_example(example_text):
                return example_text
            
            def refresh_status():
                return self._get_status_message()
            
            def clear_chat():
                return []
            
            def reset_agent():
                if self.agent:
                    self.agent.reset_conversation()
                return "🔄 Agent conversation reset", []
            
            # Wire up events
            msg_input.submit(
                fn=submit_message,
                inputs=[msg_input, chatbot],
                outputs=[chatbot, msg_input]
            )
            
            send_btn.click(
                fn=submit_message,
                inputs=[msg_input, chatbot],
                outputs=[chatbot, msg_input]
            )
            
            # Example button events
            for btn in example_buttons:
                btn.click(
                    fn=use_example,
                    inputs=[btn],
                    outputs=[msg_input]
                )
            
            # Utility button events
            refresh_status_btn.click(
                fn=refresh_status,
                outputs=[status_display]
            )
            
            clear_chat_btn.click(
                fn=clear_chat,
                outputs=[chatbot]
            )
            
            reset_agent_btn.click(
                fn=reset_agent,
                outputs=[status_display, chatbot]
            )
            
            # Initial welcome message
            interface.load(
                fn=lambda: [{"role": "assistant", "content": """👋 **Welcome to KubeGenie!**

I'm your AI Kubernetes Assistant, powered by LangChain and OpenAI. I can help you:

🔗 **Connect to clusters** - Link to your Kubernetes environments
📊 **Monitor status** - Get real-time cluster health and metrics  
🚀 **Manage workloads** - Deploy, scale, and troubleshoot applications
📚 **Learn concepts** - Understand Kubernetes best practices
🛠️ **Troubleshoot issues** - Diagnose and resolve problems

**To get started:**
1. Try "Connect to my Kubernetes cluster"
2. Ask "Show me the cluster status"
3. Or use any of the quick action buttons →

How can I help you today?"""}],
                outputs=[chatbot]
            )
        
        return interface


def main():
    """Launch the KubeGenie Agent Chat Interface"""
    
    print("🚀 Starting KubeGenie Agent Chat Interface...")
    print(f"⏰ Timestamp: {datetime.now()}")
    
    # Create chat interface
    chat = KubeGenieAgentChat()
    interface = chat.create_interface()
    
    # Launch with configuration
    interface.launch(
        server_name="0.0.0.0",
        server_port=7864,  # Different port to avoid conflicts
        share=False,
        debug=True,
        show_error=True,
        inbrowser=True
    )


if __name__ == "__main__":
    main()