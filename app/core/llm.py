"""
LLM Integration for KubeGenie Chat
"""

from openai import OpenAI
import json
import re
import logging
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass
from enum import Enum

from app.core.config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()


class IntentType(Enum):
    """Intent types for chat processing"""
    DEPLOY = "deploy"
    SCALE = "scale"
    DELETE = "delete"
    STATUS = "status"
    PROVISION = "provision"
    LIST = "list"
    HELP = "help"
    UNKNOWN = "unknown"


@dataclass
class ParsedIntent:
    """Parsed intent from user message"""
    intent: IntentType
    resource_type: str = ""
    resource_name: str = ""
    namespace: str = "default"
    parameters: Dict[str, Any] = None
    confidence: float = 0.0
    
    def __post_init__(self):
        if self.parameters is None:
            self.parameters = {}


class LLMChatProcessor:
    """LLM-powered chat processor for KubeGenie"""
    
    def __init__(self):
        self.openai_api_key = settings.OPENAI_API_KEY if hasattr(settings, 'OPENAI_API_KEY') else None
        self.enable_llm = getattr(settings, 'ENABLE_LLM', True)
        # Only use OpenAI if both ENABLE_LLM is True and OPENAI_API_KEY is set
        self.use_openai = bool(self.openai_api_key) and self.enable_llm
        if self.use_openai:
            self.client = OpenAI(api_key=self.openai_api_key)
            logger.info("OpenAI integration enabled")
        else:
            self.client = None
            logger.info("Using rule-based chat processing (OpenAI disabled or missing API key)")
    
    def process_message(self, message: str, context: Dict[str, Any] = None) -> Tuple[str, List[Dict[str, Any]], List[str]]:
        """
        Process a chat message and return response, actions, and suggestions
        
        Args:
            message: User message
            context: Additional context (user info, history, etc.)
            
        Returns:
            Tuple of (response, actions, suggestions)
        """
        if context is None:
            context = {}
            
        try:
            if self.use_openai:
                return self._process_with_openai(message, context)
            else:
                return self._process_with_rules(message, context)
        except Exception as e:
            logger.error(f"Error processing message: {e}")
            return (
                "I'm having trouble understanding your request right now. Please try again or use more specific commands.",
                [],
                ["deploy nginx --replicas=3", "list pods", "scale my-app --replicas=5"]
            )
    
    def _process_with_openai(self, message: str, context: Dict[str, Any]) -> Tuple[str, List[Dict[str, Any]], List[str]]:
        """Process message using OpenAI GPT"""
        
        system_prompt = """You are KubeGenie, an intelligent Kubernetes and cloud infrastructure assistant. 
        You help users manage Kubernetes clusters and provision cloud resources via Crossplane.
        
        Your capabilities include:
        - Deploying and managing Kubernetes workloads
        - Scaling deployments and services
        - Monitoring cluster health and troubleshooting
        - Provisioning cloud resources (AWS, GCP, Azure) via Crossplane
        - Providing guidance on best practices
        
        When users request actions, respond with:
        1. A helpful explanation of what you'll do
        2. Specific actions to execute (in JSON format)
        3. Follow-up suggestions
        
        Always prioritize safety and ask for confirmation on destructive operations.
        """
        
        try:
            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": message}
                ],
                max_tokens=500,
                temperature=0.7
            )
            
            ai_response = response.choices[0].message.content
            
            # Parse the response for actions
            actions = self._extract_actions_from_response(ai_response)
            suggestions = self._generate_suggestions(message)
            
            return ai_response, actions, suggestions
            
        except Exception as e:
            logger.error(f"OpenAI API error: {e}")
            # Fallback to rule-based processing
            return self._process_with_rules(message, context)
    
    def _process_with_rules(self, message: str, context: Dict[str, Any]) -> Tuple[str, List[Dict[str, Any]], List[str]]:
        """Process message using rule-based approach"""
        message_lower = message.lower()
        # Deploy intent
        if "deploy" in message_lower:
            return self._handle_deploy_intent(message)
        # Scale intent
        elif "scale" in message_lower:
            return self._handle_scale_intent(message)
        # Status/health intent
        elif any(word in message_lower for word in ["status", "health", "check", "show"]):
            return self._handle_status_intent(message)
        # List namespaces intent
        elif any(word in message_lower for word in ["list", "get", "show"]) and "namespace" in message_lower:
            return self._handle_list_namespaces_intent(message)
        # List pods intent (match any query containing 'pod' or 'pods')
        elif "pod" in message_lower or "pods" in message_lower:
            return self._handle_list_intent(message)
        # List intent (deployments/services)
        elif any(word in message_lower for word in ["list", "get", "show"]) and any(word in message_lower for word in ["deployments", "services"]):
            return self._handle_list_intent(message)
        # Provision intent (Crossplane)
        elif any(word in message_lower for word in ["provision", "create"]) and any(word in message_lower for word in ["s3", "rds", "bucket", "database"]):
            return self._handle_provision_intent(message)
        # Help intent
        elif any(word in message_lower for word in ["help", "what", "how", "can"]):
            return self._handle_help_intent()
        # Default response
        else:
            return self._handle_unknown_intent()

    def _handle_list_namespaces_intent(self, message: str) -> Tuple[str, List[Dict[str, Any]], List[str]]:
        """Handle list namespaces requests"""
        response = "Here are the namespaces in your cluster:"
        actions = [{
            "type": "list_namespaces",
            "parameters": {}
        }]
        suggestions = [
            "Show namespace details",
            "List pods in a namespace",
            "Create a new namespace"
        ]
        return response, actions, suggestions
    
    def _handle_deploy_intent(self, message: str) -> Tuple[str, List[Dict[str, Any]], List[str]]:
        """Handle deployment requests"""
        
        # Extract application name and replicas
        app_name = "nginx"  # default
        replicas = 1
        namespace = "default"
        
        # Simple regex extraction
        app_match = re.search(r'deploy\s+(\w+)', message.lower())
        if app_match:
            app_name = app_match.group(1)
        
        replicas_match = re.search(r'(\d+)\s*replica', message.lower())
        if replicas_match:
            replicas = int(replicas_match.group(1))
        
        namespace_match = re.search(r'namespace\s+(\w+)', message.lower())
        if namespace_match:
            namespace = namespace_match.group(1)
        
        response = f"I'll deploy {app_name} with {replicas} replica{'s' if replicas != 1 else ''} in the {namespace} namespace."
        
        actions = [{
            "type": "create_deployment",
            "parameters": {
                "name": app_name,
                "image": f"{app_name}:latest",
                "replicas": replicas,
                "namespace": namespace
            }
        }]
        
        suggestions = [
            f"Expose {app_name} as a service",
            f"Scale {app_name} to more replicas",
            "Check deployment status"
        ]
        
        return response, actions, suggestions
    
    def _handle_scale_intent(self, message: str) -> Tuple[str, List[Dict[str, Any]], List[str]]:
        """Handle scaling requests"""
        
        app_name = "my-app"
        replicas = 3
        namespace = "default"
        
        # Extract app name
        app_match = re.search(r'scale\s+(\w+)', message.lower())
        if app_match:
            app_name = app_match.group(1)
        
        # Extract replica count
        replicas_match = re.search(r'to\s+(\d+)', message.lower()) or re.search(r'(\d+)\s*replica', message.lower())
        if replicas_match:
            replicas = int(replicas_match.group(1))
        
        namespace_match = re.search(r'namespace\s+(\w+)', message.lower())
        if namespace_match:
            namespace = namespace_match.group(1)
        
        response = f"I'll scale {app_name} to {replicas} replica{'s' if replicas != 1 else ''} in the {namespace} namespace."
        
        actions = [{
            "type": "scale_deployment",
            "parameters": {
                "name": app_name,
                "replicas": replicas,
                "namespace": namespace
            }
        }]
        
        suggestions = [
            f"Check {app_name} status after scaling",
            "Monitor resource usage",
            "Set up auto-scaling"
        ]
        
        return response, actions, suggestions
    
    def _handle_status_intent(self, message: str) -> Tuple[str, List[Dict[str, Any]], List[str]]:
        """Handle status check requests"""
        namespace = "default"
        namespace_match = re.search(r'namespace\s+(\w+)', message.lower())
        if namespace_match:
            namespace = namespace_match.group(1)
        response = f"Let me check the cluster status in the {namespace} namespace..."
        actions = [{
            "type": "get_cluster_status",
            "parameters": {"namespace": namespace}
        }]
        suggestions = [
            "Show pod logs",
            "Check recent events", 
            "Monitor resource usage"
        ]
        return response, actions, suggestions
    
    def _handle_list_intent(self, message: str) -> Tuple[str, List[Dict[str, Any]], List[str]]:
        """Handle list/show requests"""
        namespace = "default"
        resource_type = "pods"
        if "deployment" in message.lower():
            resource_type = "deployments"
        elif "service" in message.lower():
            resource_type = "services"
        namespace_match = re.search(r'namespace\s+(\w+)', message.lower())
        if namespace_match:
            namespace = namespace_match.group(1)
        response = f"Here are the {resource_type} in the {namespace} namespace:"
        actions = []
        if resource_type == "pods":
            actions.append({
                "type": "list_pods",
                "parameters": {"namespace": namespace}
            })
        else:
            actions.append({
                "type": f"list_{resource_type}",
                "parameters": {"namespace": namespace}
            })
        suggestions = [
            f"Show {resource_type} details",
            "Check logs",
            "Monitor health"
        ]
        return response, actions, suggestions
    
    def _handle_provision_intent(self, message: str) -> Tuple[str, List[Dict[str, Any]], List[str]]:
        """Handle Crossplane provisioning requests"""
        
        provider = "aws"
        resource_type = "s3"
        resource_name = "my-resource"
        
        if "s3" in message.lower() or "bucket" in message.lower():
            resource_type = "s3"
            resource_name = "my-s3-bucket"
        elif "rds" in message.lower() or "database" in message.lower():
            resource_type = "rds"
            resource_name = "my-database"
        
        if "gcp" in message.lower() or "google" in message.lower():
            provider = "gcp"
        elif "azure" in message.lower():
            provider = "azure"
        
        response = f"I'll provision a {resource_type} resource on {provider.upper()} for you."
        
        actions = [{
            "type": "provision_resource",
            "parameters": {
                "name": resource_name,
                "provider": provider,
                "resource_type": resource_type
            }
        }]
        
        suggestions = [
            "Set up backup policies",
            "Configure monitoring",
            "Review cost estimates"
        ]
        
        return response, actions, suggestions
    
    def _handle_help_intent(self) -> Tuple[str, List[Dict[str, Any]], List[str]]:
        """Handle help requests"""
        
        response = """I'm KubeGenie, your intelligent Kubernetes assistant! Here's what I can help you with:

**Kubernetes Operations:**
• Deploy applications: "deploy nginx with 3 replicas"
• Scale deployments: "scale my-app to 5 replicas"  
• Check status: "show cluster health"
• List resources: "list all pods in production"

**Cloud Resources (Crossplane):**
• Provision storage: "create an S3 bucket"
• Provision databases: "provision an RDS instance"
• Manage resources: "list all cloud resources"

Just ask me in natural language and I'll help you manage your infrastructure!"""
        
        suggestions = [
            "deploy nginx with 3 replicas",
            "show cluster status",
            "provision an S3 bucket on AWS",
            "list all pods in production",
            "scale redis to 5 replicas"
        ]
        
        return response, [], suggestions
    
    def _handle_unknown_intent(self) -> Tuple[str, List[Dict[str, Any]], List[str]]:
        """Handle unknown requests"""
        
        response = """I'm not sure I understand that request. I can help you with:
• Deploying and managing Kubernetes applications
• Scaling workloads and checking cluster status  
• Provisioning cloud resources via Crossplane
• Monitoring and troubleshooting

Try asking something like "deploy nginx" or "show cluster status"."""
        
        suggestions = [
            "deploy nginx with 3 replicas",
            "scale my-app to 5 replicas",
            "show cluster status",
            "provision an S3 bucket",
            "list all pods"
        ]
        
        return response, [], suggestions
    
    def _extract_actions_from_response(self, response: str) -> List[Dict[str, Any]]:
        """Extract action commands from AI response"""
        # This would be more sophisticated with proper JSON parsing
        # For now, return empty list and let rule-based system handle it
        return []
    
    def _generate_suggestions(self, message: str) -> List[str]:
        """Generate contextual suggestions based on message"""
        return [
            "deploy nginx with 3 replicas",
            "show cluster status",
            "scale my-app to 5 replicas",
            "list all pods",
            "provision an S3 bucket"
        ]


# Global LLM processor instance
llm_processor = LLMChatProcessor()