"""
Database models for KubeGenie
"""

from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text, JSON
from sqlalchemy.sql import func
from app.core.database import Base


class User(Base):
    """User model"""
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, index=True, nullable=False)
    email = Column(String(100), unique=True, index=True, nullable=False)
    full_name = Column(String(100), nullable=False)
    hashed_password = Column(String(255), nullable=False)
    permissions = Column(JSON, default=list)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class AuditLog(Base):
    """Audit log model"""
    __tablename__ = "audit_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, index=True)
    username = Column(String(50), index=True)
    action = Column(String(100), nullable=False)
    resource_type = Column(String(50))
    resource_name = Column(String(200))
    namespace = Column(String(100))
    details = Column(JSON)
    success = Column(Boolean, default=True)
    error_message = Column(Text)
    ip_address = Column(String(45))
    user_agent = Column(Text)
    timestamp = Column(DateTime(timezone=True), server_default=func.now())


class ChatHistory(Base):
    """Chat history model"""
    __tablename__ = "chat_history"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, index=True)
    username = Column(String(50), index=True)
    session_id = Column(String(100), index=True)
    message = Column(Text, nullable=False)
    response = Column(Text, nullable=False)
    actions_executed = Column(JSON, default=list)
    success = Column(Boolean, default=True)
    timestamp = Column(DateTime(timezone=True), server_default=func.now())


class ResourceOperation(Base):
    """Resource operation history"""
    __tablename__ = "resource_operations"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, index=True)
    username = Column(String(50), index=True)
    operation_type = Column(String(50), nullable=False)  # create, update, delete, scale
    resource_type = Column(String(50), nullable=False)   # deployment, service, pod, etc.
    resource_name = Column(String(200), nullable=False)
    namespace = Column(String(100))
    cluster_context = Column(String(100))
    parameters = Column(JSON)
    result = Column(JSON)
    status = Column(String(20), default="pending")  # pending, success, failed
    error_message = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    completed_at = Column(DateTime(timezone=True))


class CrossplaneResource(Base):
    """Crossplane resource tracking"""
    __tablename__ = "crossplane_resources"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, index=True)
    username = Column(String(50), index=True)
    name = Column(String(200), nullable=False)
    provider = Column(String(50), nullable=False)
    resource_type = Column(String(100), nullable=False)
    composition_name = Column(String(200))
    parameters = Column(JSON)
    status = Column(String(50), default="provisioning")
    external_id = Column(String(500))  # Cloud provider resource ID
    endpoint = Column(String(500))
    cost_estimate = Column(String(50))
    tags = Column(JSON, default=dict)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    deleted_at = Column(DateTime(timezone=True))