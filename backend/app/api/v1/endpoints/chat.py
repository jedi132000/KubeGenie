"""
Chat/Conversational AI endpoints
"""

from fastapi import APIRouter, HTTPException, status, Header
from typing import Dict, Any, List
import logging
from pydantic import BaseModel

from app.core.llm import llm_processor
from app.api.v1.endpoints.auth_simple import verify_simple_token

logger = logging.getLogger(__name__)

router = APIRouter()


class ChatMessage(BaseModel):
    """Chat message model"""
    message: str
    context: Dict[str, Any] = {}


class ChatResponse(BaseModel):
    """Chat response model"""
    response: str
    actions: List[Dict[str, Any]] = []
    suggestions: List[str] = []


@router.post("/message")
async def process_message(
    chat_message: ChatMessage,
    authorization: str = Header(None)
) -> ChatResponse:
    """Process a natural language message and return actions"""
    try:
        logger.info(f"[DEBUG] Incoming chat message: {chat_message.message}")
        # --- AUTH DISABLED FOR DEBUG ---
        # if not authorization or not authorization.startswith("Bearer "):
        #     logger.warning("[DEBUG] Missing or invalid authorization header")
        #     raise HTTPException(
        #         status_code=status.HTTP_401_UNAUTHORIZED,
        #         detail="Missing or invalid authorization header"
        #     )
        # token = authorization.replace("Bearer ", "")
        # current_user = verify_simple_token(token)
        # logger.info(f"[DEBUG] Authenticated user: {current_user}")
        # Prepare context with dummy user info
        context = {
            "user": {"username": "debug", "permissions": ["all"]},
            "username": "debug",
            "permissions": ["all"]
        }
        logger.info(f"[DEBUG] Context for LLM: {context}")
        # Process message using LLM processor
        response_text, actions, suggestions = llm_processor.process_message(
            chat_message.message, 
            context
        )
        logger.info("[DEBUG] LLM response: %s", response_text)
        logger.info("[DEBUG] LLM actions: %s", actions)
        logger.info("[DEBUG] LLM suggestions: %s", suggestions)

        # Try to execute supported actions and return real data
        real_response = response_text
        from app.core.kubernetes import k8s_client
        # Synchronous initialization for API context
        if k8s_client.v1 is None:
            try:
                # Try in-cluster config, then kubeconfig
                try:
                    from kubernetes import config, client
                    config.load_incluster_config()
                except Exception:
                    config.load_kube_config()
                k8s_client.v1 = client.CoreV1Api()
                k8s_client.apps_v1 = client.AppsV1Api()
            except Exception as e:
                logger.error("[DEBUG] Failed to initialize Kubernetes client: %s", str(e))
        for action in actions:
            action_type = action.get("type")
            params = action.get("parameters", {})
            if action_type == "get_cluster_status" and k8s_client.v1:
                try:
                    nodes = k8s_client.v1.list_node()
                    node_count = len(nodes.items)
                    pods = k8s_client.v1.list_pod_for_all_namespaces()
                    pod_count = len(pods.items)
                    real_response = f"🚀 Cluster Status: {node_count} nodes, {pod_count} pods running."
                except Exception as e:
                    real_response = f"❌ Error getting cluster status: {str(e)}"
            elif action_type == "list_pods" and k8s_client.v1:
                namespace = params.get("namespace", "default")
                try:
                    pods = k8s_client.v1.list_namespaced_pod(namespace=namespace)
                    pod_names = [pod.metadata.name for pod in pods.items]
                    real_response = f"📦 Pods in {namespace}:\n" + "\n".join(pod_names)
                except Exception as e:
                    real_response = f"❌ Error getting pods: {str(e)}"
            elif action_type == "list_namespaces" and k8s_client.v1:
                try:
                    namespaces = k8s_client.v1.list_namespace()
                    ns_names = [ns.metadata.name for ns in namespaces.items]
                    real_response = "🏷️ Namespaces:\n" + "\n".join(ns_names)
                except Exception as e:
                    real_response = f"❌ Error getting namespaces: {str(e)}"

        # For list_pods and list_namespaces, do not return actions or suggestions
        if any(a.get('type') in ['list_pods', 'list_namespaces'] for a in actions):
            return ChatResponse(
                response=real_response,
                actions=[],
                suggestions=[]
            )
        else:
            return ChatResponse(
                response=real_response,
                actions=actions,
                suggestions=suggestions
            )
    except Exception as e:
        logger.error(f"Failed to process message: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to process message: {str(e)}"
        )


@router.get("/suggestions")
async def get_suggestions() -> List[str]:
    """Get conversation suggestions"""
    try:
        suggestions = [
            "deploy nginx with 3 replicas",
            "scale redis to 5 replicas",
            "show me all pods",
            "provision an AWS RDS instance",
            "create an S3 bucket with versioning",
            "check cluster health",
            "list all namespaces",
            "show recent events"
        ]
        return suggestions
    except Exception as e:
        logger.error(f"Failed to get suggestions: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get suggestions: {str(e)}"
        )


@router.get("/history")
async def get_chat_history() -> List[Dict[str, Any]]:
    """Get chat history (mock implementation)"""
    try:
        # Mock chat history
        history = [
            {
                "timestamp": "2024-01-01T10:00:00Z",
                "message": "deploy nginx with 3 replicas",
                "response": "Deployed nginx with 3 replicas successfully",
                "actions_executed": 1
            },
            {
                "timestamp": "2024-01-01T10:05:00Z", 
                "message": "scale nginx to 5 replicas",
                "response": "Scaled nginx deployment to 5 replicas",
                "actions_executed": 1
            }
        ]
        return history
    except Exception as e:
        logger.error(f"Failed to get chat history: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get chat history: {str(e)}"
        )