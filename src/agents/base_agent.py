"""
KubeGenie LangChain Agent
Core AI agent for Kubernetes management using OpenAI and LangChain

Step 4: LangChain basic agent implementation
"""

import os
from typing import List, Dict, Any, Optional
from datetime import datetime

# Load environment variables from .env file
try:
    from dotenv import load_dotenv
    load_dotenv()
    print("✅ Environment variables loaded from .env")
except ImportError:
    print("⚠️ python-dotenv not available - using system environment")

# LangChain imports (with fallbacks)
try:
    from langchain_openai import ChatOpenAI
    from langchain_core.messages import HumanMessage, SystemMessage, AIMessage
    from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
    from langchain.agents import create_openai_tools_agent, AgentExecutor
    from langchain_core.runnables.history import RunnableWithMessageHistory
    from langchain_community.chat_message_histories import ChatMessageHistory
    LANGCHAIN_AVAILABLE = True
except ImportError:
    LANGCHAIN_AVAILABLE = False
    print("⚠️ LangChain not available - will use fallback responses")

# Import our tools
try:
    import sys
    sys.path.append(os.path.dirname(os.path.dirname(__file__)))
    from tools.kubectl_tools import create_kubernetes_tools
    from tools.k8s_operations import KubernetesOperations
    TOOLS_AVAILABLE = True
except ImportError as e:
    TOOLS_AVAILABLE = False
    print(f"⚠️ Tools import error: {e}")


class KubeGenieAgent:
    """Main LangChain agent for KubeGenie AI Kubernetes Assistant"""
    
    def __init__(self):
        self.llm = None
        self.agent = None
        self.agent_executor = None
        self.agent_with_history = None
        self.k8s_ops = None
        self.chat_history = ChatMessageHistory() if LANGCHAIN_AVAILABLE else None
        self.session_id = f"kubegenie-{datetime.now().strftime('%Y%m%d-%H%M%S')}"
        
        # Initialize components
        self._initialize_llm()
        self._initialize_k8s_ops()
        self._initialize_agent()
    
    def _initialize_llm(self):
        """Initialize the OpenAI LLM"""
        if not LANGCHAIN_AVAILABLE:
            return
        
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            print("⚠️ OPENAI_API_KEY not set - agent will use fallback responses")
            return
        
        try:
            self.llm = ChatOpenAI(
                model="gpt-3.5-turbo",
                temperature=0,
                api_key=api_key
            )
            print("✅ OpenAI LLM initialized successfully")
        except Exception as e:
            print(f"⚠️ Failed to initialize OpenAI LLM: {e}")
    
    def _initialize_k8s_ops(self):
        """Initialize Kubernetes operations"""
        if TOOLS_AVAILABLE:
            try:
                self.k8s_ops = KubernetesOperations()
                print("✅ Kubernetes operations initialized")
            except Exception as e:
                print(f"⚠️ Failed to initialize Kubernetes operations: {e}")
    
    def _initialize_agent(self):
        """Initialize the LangChain agent with tools"""
        if not LANGCHAIN_AVAILABLE or not self.llm:
            return
        
        # Create system prompt
        system_prompt = """You are KubeGenie, an expert AI Kubernetes Assistant. You help users manage their Kubernetes clusters through natural conversation.

Your capabilities include:
- Connecting to Kubernetes clusters
- Monitoring cluster health and status
- Listing and managing nodes, pods, and namespaces
- Providing intelligent recommendations
- Explaining Kubernetes concepts and best practices

Key guidelines:
1. Always be helpful and explain what you're doing
2. Use the available tools to perform actual Kubernetes operations
3. Provide clear, actionable responses
4. If a cluster connection is needed, guide the user to connect first
5. Format responses with appropriate emojis and structure for readability
6. When errors occur, provide troubleshooting guidance

Available tools allow you to:
- connect_to_cluster: Connect to Kubernetes clusters
- get_cluster_status: Get comprehensive cluster overview
- list_cluster_nodes: List all cluster nodes with details
- list_pods: List pods in namespaces (with options for specific or all namespaces)
- list_namespaces: List all available namespaces

Always use tools when users ask for specific information or actions related to Kubernetes clusters."""

        try:
            # Create tools
            tools = create_kubernetes_tools() if TOOLS_AVAILABLE else []
            
            # Create prompt template
            prompt = ChatPromptTemplate.from_messages([
                ("system", system_prompt),
                MessagesPlaceholder("chat_history"),
                ("human", "{input}"),
                MessagesPlaceholder("agent_scratchpad")
            ])
            
            # Create agent
            self.agent = create_openai_tools_agent(self.llm, tools, prompt)
            
            # Create agent executor
            self.agent_executor = AgentExecutor(
                agent=self.agent,
                tools=tools,
                verbose=True,
                max_iterations=3,
                early_stopping_method="generate"
            )
            
            # Add message history
            self.agent_with_history = RunnableWithMessageHistory(
                self.agent_executor,
                lambda session_id: self.chat_history,
                input_messages_key="input",
                history_messages_key="chat_history"
            )
            
            print("✅ LangChain agent initialized with Kubernetes tools")
            
        except Exception as e:
            print(f"⚠️ Failed to initialize agent: {e}")
    
    def chat(self, message: str) -> str:
        """Process a chat message and return AI response"""
        
        # If LangChain agent is available, use it
        if hasattr(self, 'agent_with_history') and self.agent_with_history and self.llm:
            try:
                response = self.agent_with_history.invoke(
                    {"input": message},
                    config={"configurable": {"session_id": self.session_id}}
                )
                return response.get("output", "Sorry, I couldn't process that request.")
                
            except Exception as e:
                return f"❌ Agent error: {str(e)}\n\nFalling back to basic responses..."
        
        # Fallback to rule-based responses
        return self._fallback_response(message)
    
    def _fallback_response(self, message: str) -> str:
        """Fallback response system when LangChain is not available"""
        
        message_lower = message.lower()
        
        if any(word in message_lower for word in ['hello', 'hi', 'hey']):
            return """👋 Hello! I'm KubeGenie, your AI Kubernetes Assistant.

**Current Status:** 
- 🤖 Chat: ✅ Active (Fallback mode)
- 🔗 Kubernetes: ✅ Available

**I can help you with:**
- Connect to cluster
- Show cluster status  
- List nodes, pods, namespaces
- Basic Kubernetes operations

Try asking me about your cluster!"""

        elif 'connect' in message_lower and 'cluster' in message_lower:
            if self.k8s_ops:
                return self.k8s_ops.connect_to_cluster()
            else:
                return "❌ Kubernetes operations not available"
        
        elif 'status' in message_lower or ('cluster' in message_lower and 'overview' in message_lower):
            if self.k8s_ops and self.k8s_ops.is_connected():
                return self.k8s_ops.get_cluster_overview()
            else:
                return "❌ Not connected to cluster. Please connect first with: 'Connect to cluster'"
        
        elif 'nodes' in message_lower or 'list nodes' in message_lower:
            if self.k8s_ops and self.k8s_ops.is_connected():
                return self.k8s_ops.list_cluster_nodes()
            else:
                return "❌ Not connected to cluster. Please connect first with: 'Connect to cluster'"
        
        elif 'pods' in message_lower:
            if self.k8s_ops and self.k8s_ops.is_connected():
                # Check if specific namespace mentioned
                if 'kube-system' in message_lower:
                    return self.k8s_ops.list_pods_in_namespace('kube-system')
                elif 'default' in message_lower:
                    return self.k8s_ops.list_pods_in_namespace('default')
                elif 'all' in message_lower:
                    return self.k8s_ops.list_all_pods()  # All namespaces
                else:
                    return self.k8s_ops.list_all_pods()  # All namespaces by default
            else:
                return "❌ Not connected to cluster. Please connect first with: 'Connect to cluster'"
        
        elif 'namespaces' in message_lower or 'namespace' in message_lower:
            if self.k8s_ops and self.k8s_ops.is_connected():
                return self.k8s_ops.list_namespaces()
            else:
                return "❌ Not connected to cluster. Please connect first with: 'Connect to cluster'"
        
        else:
            return f"""🤖 I understand you said: "{message}"

**Available Commands:**
- "Connect to cluster" - Connect to your Kubernetes cluster
- "Show cluster status" - Get cluster overview
- "List nodes" - Show all cluster nodes
- "Show pods" or "List pods" - Show all pods
- "Show pods in kube-system" - Pods in specific namespace
- "List namespaces" - Show all namespaces

**💡 Tip:** Even without OpenAI, I can perform all Kubernetes operations!"""
    
    def get_connection_status(self) -> Dict[str, Any]:
        """Get detailed status of all components"""
        return {
            "langchain_available": LANGCHAIN_AVAILABLE,
            "llm_initialized": self.llm is not None,
            "agent_initialized": self.agent is not None,
            "k8s_available": TOOLS_AVAILABLE,
            "k8s_connected": self.k8s_ops.is_connected() if self.k8s_ops else False,
            "session_id": self.session_id
        }
    
    def reset_conversation(self):
        """Reset conversation history"""
        if self.chat_history:
            self.chat_history.clear()
        self.session_id = f"kubegenie-{datetime.now().strftime('%Y%m%d-%H%M%S')}"