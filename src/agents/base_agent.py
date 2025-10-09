"""
Base Agent Interface for KubeGenie AI Agents

All specialized agents inherit from this base class to ensure
consistent interface and behavior across the platform.
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional
from dataclasses import dataclass
from enum import Enum
import logging
from datetime import datetime

logger = logging.getLogger(__name__)


class AgentStatus(Enum):
    IDLE = "idle"
    RUNNING = "running"
    ERROR = "error"
    DISABLED = "disabled"


class ActionPriority(Enum):
    LOW = 1
    MEDIUM = 2
    HIGH = 3
    CRITICAL = 4


@dataclass
class AgentAction:
    """Represents an action that an agent wants to take"""
    id: str
    agent_id: str
    action_type: str
    description: str
    priority: ActionPriority
    requires_approval: bool
    cluster_id: str
    parameters: Dict[str, Any]
    reasoning: str
    knowledge_sources: List[str]  # References to knowledge base sources
    estimated_risk: float  # 0.0 to 1.0
    created_at: datetime
    
    
@dataclass 
class AgentResult:
    """Result of an agent action"""
    action_id: str
    success: bool
    message: str
    data: Optional[Dict[str, Any]] = None
    errors: Optional[List[str]] = None
    execution_time: Optional[float] = None


class BaseAgent(ABC):
    """
    Base class for all KubeGenie AI agents
    
    Each agent is responsible for a specific domain (monitoring, remediation, etc.)
    and communicates with the orchestrator for coordination.
    """
    
    def __init__(self, agent_id: str, name: str, description: str):
        self.agent_id = agent_id
        self.name = name
        self.description = description
        self.status = AgentStatus.IDLE
        self.last_activity = datetime.now()
        
    @abstractmethod
    async def analyze(self, cluster_data: Dict[str, Any]) -> List[AgentAction]:
        """
        Analyze cluster data and return list of recommended actions
        
        Args:
            cluster_data: Current state and metrics for clusters
            
        Returns:
            List of actions the agent recommends taking
        """
        pass
    
    @abstractmethod
    async def execute_action(self, action: AgentAction) -> AgentResult:
        """
        Execute a specific action
        
        Args:
            action: The action to execute
            
        Returns:
            Result of the action execution
        """
        pass
    
    @abstractmethod
    async def health_check(self) -> bool:
        """
        Check if the agent is healthy and operational
        
        Returns:
            True if healthy, False otherwise
        """
        pass
    
    async def get_status(self) -> Dict[str, Any]:
        """Get current agent status and metadata"""
        return {
            "agent_id": self.agent_id,
            "name": self.name,
            "description": self.description,
            "status": self.status.value,
            "last_activity": self.last_activity.isoformat()
        }
    
    def _set_status(self, status: AgentStatus):
        """Update agent status and last activity time"""
        self.status = status
        self.last_activity = datetime.now()
        logger.info(f"Agent {self.agent_id} status changed to {status.value}")
    
    async def start(self):
        """Start the agent"""
        logger.info(f"Starting agent {self.agent_id}")
        self._set_status(AgentStatus.IDLE)
    
    async def stop(self):
        """Stop the agent"""
        logger.info(f"Stopping agent {self.agent_id}")
        self._set_status(AgentStatus.DISABLED)