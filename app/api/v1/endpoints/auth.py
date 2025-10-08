"""
Authentication endpoints
"""

from fastapi import APIRouter, HTTPException, status, Depends
from fastapi.security import HTTPBearer
from pydantic import BaseModel
from typing import Dict, Any
import logging

from app.core.auth import auth_manager, get_current_active_user

logger = logging.getLogger(__name__)

router = APIRouter()
security = HTTPBearer()


class LoginRequest(BaseModel):
    """Login request model"""
    username: str
    password: str


class LoginResponse(BaseModel):
    """Login response model"""
    access_token: str
    token_type: str = "bearer"
    user: Dict[str, Any]


class UserProfile(BaseModel):
    """User profile model"""
    username: str
    email: str = ""
    full_name: str = ""
    permissions: list[str] = []
    is_active: bool = True


# In-memory user store (replace with database in production)
# Initialize users_db as empty initially
users_db = {}

def initialize_users():
    """Initialize users with hashed passwords"""
    global users_db
    try:
        users_db = {
            "admin": {
                "username": "admin", 
                "hashed_password": auth_manager.get_password_hash("admin123"),  # Change this!
                "permissions": ["kubernetes:read", "kubernetes:write", "crossplane:read", "crossplane:write"],
                "is_active": True
            },
            "operator": {
                "username": "operator", 
                "hashed_password": auth_manager.get_password_hash("operator123"),
                "permissions": ["kubernetes:read", "kubernetes:write"],
                "is_active": True
            },
            "viewer": {
                "username": "viewer", 
                "hashed_password": auth_manager.get_password_hash("viewer123"),
                "permissions": ["kubernetes:read"],
                "is_active": True
            }
        }
    except Exception as e:
        # Fallback with simple passwords for development
        print(f"Warning: Using simple passwords due to bcrypt issue: {e}")
        users_db = {
            "admin": {
                "username": "admin", 
                "hashed_password": "admin123",  # Simple password for dev
                "permissions": ["kubernetes:read", "kubernetes:write", "crossplane:read", "crossplane:write"],
                "is_active": True
            },
            "operator": {
                "username": "operator", 
                "hashed_password": "operator123",
                "permissions": ["kubernetes:read", "kubernetes:write"],
                "is_active": True
            },
            "viewer": {
                "username": "viewer", 
                "hashed_password": "viewer123",
                "permissions": ["kubernetes:read"],
                "is_active": True
            }
        }


def authenticate_user(username: str, password: str) -> Optional[dict]:
    """Authenticate a user with username and password"""
    if not users_db:  # Initialize if empty
        initialize_users()
    user = users_db.get(username)
    if not user:
        return None
    
    if not auth_manager.verify_password(password, user["hashed_password"]):
        return None
    
    if not user["is_active"]:
        return None
        
    return user


@router.post("/login", response_model=Token)
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    """Login endpoint to get access token"""
    try:
        # Initialize users if needed
        if not users_db:
            initialize_users()
            
        user = authenticate_user(form_data.username, form_data.password)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect username or password",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        if not user["is_active"]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Inactive user"
            )
        
        access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = auth_manager.create_access_token(
            data={"sub": user["username"]}, expires_delta=access_token_expires
        )
        
        logger.info("User %s logged in successfully", user['username'])
        
        return {
            "access_token": access_token,
            "token_type": "bearer",
            "expires_in": settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60
        }
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Login error: %s", str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Authentication failed"
        ) from e


@router.post("/logout")
async def logout(current_user: Dict[str, Any] = Depends(get_current_active_user)):
    """Logout user (token invalidation would be implemented here)"""
    logger.info("User %s logged out", current_user['username'])
    return {"message": "Successfully logged out"}


@router.get("/me", response_model=UserProfile)
async def get_current_user_profile(current_user: Dict[str, Any] = Depends(get_current_active_user)) -> UserProfile:
    """Get current user profile"""
    payload = current_user.get("payload", {})
    
    return UserProfile(
        username=current_user["username"],
        email=payload.get("email", ""),
        full_name=payload.get("full_name", ""),
        permissions=payload.get("permissions", []),
        is_active=True
    )


@router.get("/permissions")
async def get_user_permissions(current_user: Dict[str, Any] = Depends(get_current_active_user)) -> Dict[str, Any]:
    """Get current user permissions"""
    payload = current_user.get("payload", {})
    permissions = payload.get("permissions", [])
    
    return {
        "username": current_user["username"],
        "permissions": permissions,
        "has_admin": "admin" in permissions,
        "has_cluster_read": "cluster:read" in permissions,
        "has_cluster_write": "cluster:write" in permissions,
        "has_crossplane_read": "crossplane:read" in permissions,
        "has_crossplane_write": "crossplane:write" in permissions
    }


@router.get("/validate-token")
async def validate_token(current_user: Dict[str, Any] = Depends(get_current_active_user)) -> Dict[str, Any]:
    """Validate current token"""
    return {
        "valid": True,
        "username": current_user["username"],
        "message": "Token is valid"
    }