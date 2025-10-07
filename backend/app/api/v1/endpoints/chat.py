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
        # Verify authentication
        if not authorization or not authorization.startswith("Bearer "):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Missing or invalid authorization header"
            )
        
        token = authorization.replace("Bearer ", "")
        current_user = verify_simple_token(token)
        
        # Prepare context with user information
        context = {
            "user": current_user,
            "username": current_user.get("username", "unknown"),
            "permissions": current_user.get("permissions", [])
        }
        
        # Process message using LLM processor
        response_text, actions, suggestions = llm_processor.process_message(
            chat_message.message, 
            context
        )
        
        return ChatResponse(
            response=response_text,
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