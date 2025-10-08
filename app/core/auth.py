"""
Authentication and authorization utilities
"""

import jwt
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from passlib.context import CryptContext
from passlib.hash import bcrypt
from fastapi import HTTPException, status, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import logging

from app.core.config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# JWT token handling
security = HTTPBearer()


class AuthManager:
    """Authentication and authorization manager"""
    
    def __init__(self):
        self.secret_key = settings.JWT_SECRET
        self.algorithm = settings.JWT_ALGORITHM
        self.access_token_expire_minutes = settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES
    
    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """Verify a password against its hash"""
        return pwd_context.verify(plain_password, hashed_password)
    
    def get_password_hash(self, password: str) -> str:
        """Hash a password"""
        return pwd_context.hash(password)
    
    def create_access_token(self, data: Dict[str, Any], expires_delta: Optional[timedelta] = None) -> str:
        """Create a JWT access token"""
        to_encode = data.copy()
        
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(minutes=self.access_token_expire_minutes)
        
        to_encode.update({"exp": expire})
        
        try:
            encoded_jwt = jwt.encode(to_encode, self.secret_key, algorithm=self.algorithm)
            return encoded_jwt
        except Exception as e:
            logger.error(f"Error creating access token: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Could not create access token"
            )
    
    def verify_token(self, token: str) -> Dict[str, Any]:
        """Verify and decode a JWT token"""
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
            return payload
        except jwt.ExpiredSignatureError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token has expired",
                headers={"WWW-Authenticate": "Bearer"},
            )
        except jwt.InvalidTokenError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Could not validate credentials",
                headers={"WWW-Authenticate": "Bearer"},
            )
    
    def get_current_user(self, credentials: HTTPAuthorizationCredentials = Depends(security)) -> Dict[str, Any]:
        """Get current user from JWT token"""
        token = credentials.credentials
        payload = self.verify_token(token)
        
        username: str = payload.get("sub")
        if username is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Could not validate credentials",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        return {"username": username, "payload": payload}


# Global auth manager instance
auth_manager = AuthManager()


# Dependency functions for FastAPI
async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)) -> Dict[str, Any]:
    """FastAPI dependency to get current authenticated user"""
    return auth_manager.get_current_user(credentials)


async def get_current_active_user(current_user: Dict[str, Any] = Depends(get_current_user)) -> Dict[str, Any]:
    """FastAPI dependency to get current active user"""
    # Add any additional checks here (e.g., user is active, not banned, etc.)
    return current_user


def require_permission(permission: str):
    """Decorator to require specific permission"""
    def permission_checker(current_user: Dict[str, Any] = Depends(get_current_active_user)) -> Dict[str, Any]:
        user_permissions = current_user.get("payload", {}).get("permissions", [])
        if permission not in user_permissions:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Permission '{permission}' required"
            )
        return current_user
    return permission_checker


# Common permission requirements
require_cluster_read = require_permission("cluster:read")
require_cluster_write = require_permission("cluster:write")
require_crossplane_read = require_permission("crossplane:read")
require_crossplane_write = require_permission("crossplane:write")
require_admin = require_permission("admin")