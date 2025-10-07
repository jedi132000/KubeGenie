"""
Simple authentication endpoints for development
"""

from fastapi import APIRouter, HTTPException, Depends, status
from fastapi.security import OAuth2PasswordRequestForm
from datetime import timedelta
import logging

# Simple imports to avoid dependency issues
router = APIRouter()
logger = logging.getLogger(__name__)

# Mock users for development
USERS = {
    "admin": {"username": "admin", "password": "admin123", "permissions": ["all"]},
    "operator": {"username": "operator", "password": "operator123", "permissions": ["read", "write"]},
    "viewer": {"username": "viewer", "password": "viewer123", "permissions": ["read"]}
}

# Simple token store (not for production!)
active_tokens = {}

def authenticate_user(username: str, password: str):
    """Simple authentication"""
    user = USERS.get(username)
    if user and user["password"] == password:
        return user
    return None

def create_token(username: str) -> str:
    """Create a simple token"""
    import secrets
    token = secrets.token_urlsafe(32)
    active_tokens[token] = username
    return token

def get_current_user(token: str = Depends(lambda: "dummy_token")):
    """Get current user (simplified)"""
    # For development, just return admin user
    return USERS["admin"]

@router.post("/login")
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    """Login endpoint"""
    user = authenticate_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    token = create_token(user["username"])
    return {
        "access_token": token,
        "token_type": "bearer"
    }

@router.get("/me")
async def get_me():
    """Get current user info"""
    return {"username": "admin", "permissions": ["all"]}

@router.post("/logout")
async def logout():
    """Logout"""
    return {"message": "Logged out"}


def verify_simple_token(token: str) -> dict:
    """Verify simple token and return user info"""
    if token in active_tokens:
        return {"username": "admin", "permissions": ["all"]}
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid authentication credentials"
    )