"""
AI Orchestrator - Central coordinator for all agents

Manages task planning, agent coordination, decision making,
and escalation workflows.
"""

import asyncio
import logging
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from datetime import datetime
from enum import Enum

from ..agents.base_agent import BaseAgent, AgentAction, AgentResult, ActionPriority

logger = logging.getLogger(__name__)


class OrchestratorStatus(Enum):
    IDLE = "idle"
    ANALYZING = "analyzing"
    COORDINATING = "coordinating" 
    EXECUTING = "executing"
    ERROR = "error"


@dataclass
class OrchestrationTask:
    """Represents a task being orchestrated across multiple agents"""
    id: str
    description: str
    priority: ActionPriority
    cluster_ids: List[str]
    requested_by: str
    created_at: datetime
    actions: List[AgentAction]
    status: str = "pending"
    results: Optional[List[AgentResult]] = None


class AIOrchestrator:
    """
    Central AI orchestrator that coordinates all agents
    
    Responsibilities:
    - Analyze cluster data across all agents
    - Coordinate multi-agent workflows
    - Make decisions on action execution
    - Handle approval workflows
    - Manage escalations and conflicts
    """
    
    def __init__(self):
        self.agents: Dict[str, BaseAgent] = {}
        self.status = OrchestratorStatus.IDLE
        self.active_tasks: Dict[str, OrchestrationTask] = {}
        self.task_queue = asyncio.Queue()
        
    async def register_agent(self, agent: BaseAgent):
        """Register a new agent with the orchestrator"""
        self.agents[agent.agent_id] = agent
        await agent.start()
        logger.info(f"Registered agent: {agent.agent_id}")
    
    async def unregister_agent(self, agent_id: str):
        """Unregister an agent"""
        if agent_id in self.agents:
            await self.agents[agent_id].stop()
            del self.agents[agent_id]
            logger.info(f"Unregistered agent: {agent_id}")
    
    async def analyze_clusters(self, cluster_data: Dict[str, Any]) -> List[AgentAction]:
        """
        Run analysis across all agents and collect recommended actions
        
        Args:
            cluster_data: Current state and metrics for all clusters
            
        Returns:
            Consolidated list of recommended actions from all agents
        """
        self.status = OrchestratorStatus.ANALYZING
        all_actions = []
        
        # Run analysis in parallel across all agents
        tasks = []
        for agent in self.agents.values():
            if agent.status.value != "disabled":
                tasks.append(agent.analyze(cluster_data))
        
        try:
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            for i, result in enumerate(results):
                if isinstance(result, Exception):
                    logger.error(f"Agent analysis failed: {result}")
                    continue
                    
                if isinstance(result, list):
                    all_actions.extend(result)
                    
        except Exception as e:
            logger.error(f"Error during cluster analysis: {e}")
            self.status = OrchestratorStatus.ERROR
            return []
        
        # Sort actions by priority and risk
        all_actions.sort(key=lambda x: (x.priority.value, x.estimated_risk), reverse=True)
        
        self.status = OrchestratorStatus.IDLE
        return all_actions
    
    async def create_orchestration_task(
        self, 
        description: str,
        actions: List[AgentAction],
        requested_by: str
    ) -> OrchestrationTask:
        """Create a new orchestration task"""
        task_id = f"task_{datetime.now().timestamp()}"
        
        # Determine overall priority
        max_priority = max((action.priority.value for action in actions), default=ActionPriority.LOW.value)
        max_priority = ActionPriority(max_priority)
        
        # Extract unique cluster IDs
        cluster_ids = list(set(action.cluster_id for action in actions))
        
        task = OrchestrationTask(
            id=task_id,
            description=description,
            priority=max_priority,
            cluster_ids=cluster_ids,
            requested_by=requested_by,
            created_at=datetime.now(),
            actions=actions,
            results=[]
        )
        
        self.active_tasks[task_id] = task
        await self.task_queue.put(task)
        
        logger.info(f"Created orchestration task: {task_id}")
        return task
    
    async def execute_actions(self, actions: List[AgentAction]) -> List[AgentResult]:
        """
        Execute a list of actions, handling dependencies and coordination
        
        Args:
            actions: List of actions to execute
            
        Returns:
            List of execution results
        """
        self.status = OrchestratorStatus.EXECUTING
        results = []
        
        # Group actions by agent
        agent_actions = {}
        for action in actions:
            if action.agent_id not in agent_actions:
                agent_actions[action.agent_id] = []
            agent_actions[action.agent_id].append(action)
        
        # Execute actions per agent (could be parallelized based on dependencies)
        for agent_id, agent_actions_list in agent_actions.items():
            if agent_id not in self.agents:
                logger.error(f"Agent {agent_id} not found")
                continue
                
            agent = self.agents[agent_id]
            
            for action in agent_actions_list:
                try:
                    result = await agent.execute_action(action)
                    results.append(result)
                    logger.info(f"Action {action.id} executed: {result.success}")
                except Exception as e:
                    error_result = AgentResult(
                        action_id=action.id,
                        success=False,
                        message=f"Execution failed: {str(e)}",
                        errors=[str(e)]
                    )
                    results.append(error_result)
                    logger.error(f"Action {action.id} failed: {e}")
        
        self.status = OrchestratorStatus.IDLE
        return results
    
    async def get_agent_status(self) -> Dict[str, Any]:
        """Get status of all registered agents"""
        status = {}
        for agent_id, agent in self.agents.items():
            status[agent_id] = await agent.get_status()
        return status
    
    async def get_orchestrator_status(self) -> Dict[str, Any]:
        """Get current orchestrator status"""
        return {
            "status": self.status.value,
            "registered_agents": len(self.agents),
            "active_tasks": len(self.active_tasks),
            "queue_size": self.task_queue.qsize()
        }