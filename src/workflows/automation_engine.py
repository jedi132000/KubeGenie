"""
Workflow Automation System for KubeGenie

Chains multiple agent actions together based on dependencies,
priorities, and execution requirements.
"""

import asyncio
import json
from typing import Dict, List, Any, Optional
from datetime import datetime, timezone
from enum import Enum
import logging

logger = logging.getLogger(__name__)

class WorkflowStatus(Enum):
    PENDING = "pending"
    RUNNING = "running" 
    COMPLETED = "completed"
    FAILED = "failed"
    PAUSED = "paused"

class ActionStatus(Enum):
    WAITING = "waiting"
    READY = "ready"
    EXECUTING = "executing"
    COMPLETED = "completed"
    FAILED = "failed"
    SKIPPED = "skipped"

class WorkflowAction:
    """Represents an action within a workflow with dependencies"""
    
    def __init__(self, action_id: str, agent_id: str, action_type: str, 
                 description: str, parameters: Dict[str, Any],
                 dependencies: List[str] = None, timeout: int = 300):
        self.action_id = action_id
        self.agent_id = agent_id
        self.action_type = action_type
        self.description = description
        self.parameters = parameters
        self.dependencies = dependencies or []
        self.timeout = timeout
        self.status = ActionStatus.WAITING
        self.start_time: Optional[datetime] = None
        self.end_time: Optional[datetime] = None
        self.result: Optional[Dict[str, Any]] = None
        self.error: Optional[str] = None

class Workflow:
    """Manages a collection of actions with dependencies"""
    
    def __init__(self, workflow_id: str, name: str, description: str):
        self.workflow_id = workflow_id
        self.name = name
        self.description = description
        self.actions: Dict[str, WorkflowAction] = {}
        self.status = WorkflowStatus.PENDING
        self.created_at = datetime.now(timezone.utc)
        self.started_at: Optional[datetime] = None
        self.completed_at: Optional[datetime] = None
        self.total_actions = 0
        self.completed_actions = 0
        self.failed_actions = 0

    def add_action(self, action: WorkflowAction):
        """Add an action to the workflow"""
        self.actions[action.action_id] = action
        self.total_actions += 1

    def get_ready_actions(self) -> List[WorkflowAction]:
        """Get actions that are ready to execute (dependencies met)"""
        ready_actions = []
        
        for action in self.actions.values():
            if action.status != ActionStatus.WAITING:
                continue
                
            # Check if all dependencies are completed
            dependencies_met = True
            for dep_id in action.dependencies:
                if dep_id not in self.actions:
                    dependencies_met = False
                    break
                    
                dep_action = self.actions[dep_id]
                if dep_action.status != ActionStatus.COMPLETED:
                    dependencies_met = False
                    break
            
            if dependencies_met:
                action.status = ActionStatus.READY
                ready_actions.append(action)
        
        return ready_actions

class WorkflowEngine:
    """Executes workflows with dependency management"""
    
    def __init__(self):
        self.active_workflows: Dict[str, Workflow] = {}
        self.completed_workflows: Dict[str, Workflow] = {}
    
    async def create_workflow_from_analysis(self, analysis_result: Dict[str, Any]) -> Workflow:
        """Create a workflow from multi-agent analysis results"""
        
        workflow_id = f"workflow_{datetime.now().timestamp()}"
        workflow = Workflow(
            workflow_id=workflow_id,
            name="Multi-Agent Remediation Workflow",
            description="Automated workflow from cluster analysis"
        )
        
        actions = analysis_result.get("actions", [])
        
        # Create workflow actions with smart dependencies
        security_actions = []
        cost_actions = []
        remediation_actions = []
        
        for action_data in actions:
            workflow_action = WorkflowAction(
                action_id=action_data["id"],
                agent_id=action_data["agent_id"], 
                action_type=action_data["action_type"],
                description=action_data["description"],
                parameters=action_data["parameters"]
            )
            
            # Categorize actions
            if "security" in action_data["agent_id"]:
                security_actions.append(workflow_action)
            elif "cost" in action_data["agent_id"]:
                cost_actions.append(workflow_action)
            elif "remediation" in action_data["agent_id"]:
                remediation_actions.append(workflow_action)
            
            workflow.add_action(workflow_action)
        
        # Set up intelligent dependencies
        # Rule 1: Security hardening should happen before cost optimization
        for cost_action in cost_actions:
            for security_action in security_actions:
                if security_action.action_type == "security_hardening":
                    cost_action.dependencies.append(security_action.action_id)
        
        # Rule 2: Remediation should happen before optimization
        for cost_action in cost_actions:
            for remediation_action in remediation_actions:
                cost_action.dependencies.append(remediation_action.action_id)
        
        logger.info(f"Created workflow {workflow_id} with {len(actions)} actions")
        
        # Store workflow in active workflows
        self.active_workflows[workflow.workflow_id] = workflow
        
        return workflow
    
    async def execute_workflow(self, workflow: Workflow) -> Dict[str, Any]:
        """Execute a workflow with dependency management"""
        
        workflow.status = WorkflowStatus.RUNNING
        workflow.started_at = datetime.now(timezone.utc)
        self.active_workflows[workflow.workflow_id] = workflow
        
        logger.info(f"Starting workflow execution: {workflow.workflow_id}")
        
        try:
            while workflow.completed_actions + workflow.failed_actions < workflow.total_actions:
                # Get actions ready to execute
                ready_actions = workflow.get_ready_actions()
                
                if not ready_actions:
                    # Check if we're stuck (no ready actions but not done)
                    waiting_actions = [a for a in workflow.actions.values() 
                                     if a.status == ActionStatus.WAITING]
                    if waiting_actions:
                        logger.error(f"Workflow stuck - circular dependencies detected")
                        workflow.status = WorkflowStatus.FAILED
                        break
                    else:
                        # All actions processed
                        break
                
                # Execute ready actions (simulate execution)
                for action in ready_actions:
                    await self._execute_action(workflow, action)
                
                # Small delay between batches
                await asyncio.sleep(0.5)
            
            # Determine final status
            if workflow.failed_actions > 0:
                workflow.status = WorkflowStatus.FAILED
            else:
                workflow.status = WorkflowStatus.COMPLETED
            
            workflow.completed_at = datetime.now(timezone.utc)
            
            # Move to completed workflows
            self.completed_workflows[workflow.workflow_id] = workflow
            del self.active_workflows[workflow.workflow_id]
            
            execution_time = (workflow.completed_at - workflow.started_at).total_seconds()
            
            result = {
                "workflow_id": workflow.workflow_id,
                "status": workflow.status.value,
                "total_actions": workflow.total_actions,
                "completed_actions": workflow.completed_actions,
                "failed_actions": workflow.failed_actions,
                "execution_time": execution_time,
                "actions": [
                    {
                        "action_id": action.action_id,
                        "agent_id": action.agent_id,
                        "status": action.status.value,
                        "description": action.description,
                        "dependencies": action.dependencies,
                        "execution_time": (action.end_time - action.start_time).total_seconds() 
                                        if action.start_time and action.end_time else 0
                    }
                    for action in workflow.actions.values()
                ]
            }
            
            logger.info(f"Workflow {workflow.workflow_id} completed with status: {workflow.status.value}")
            return result
            
        except Exception as e:
            workflow.status = WorkflowStatus.FAILED
            workflow.completed_at = datetime.now(timezone.utc)
            logger.error(f"Workflow execution failed: {e}")
            raise
    
    async def _execute_action(self, workflow: Workflow, action: WorkflowAction):
        """Execute a single action (simulated)"""
        
        action.status = ActionStatus.EXECUTING
        action.start_time = datetime.now(timezone.utc)
        
        logger.info(f"Executing action: {action.description}")
        
        try:
            # Simulate action execution time based on action type
            execution_times = {
                "security_hardening": 3,
                "network_security": 2,
                "cleanup": 1,
                "rightsizing": 4,
                "restart_pod": 2,
                "cleanup_job": 1
            }
            
            sleep_time = execution_times.get(action.action_type, 2)
            await asyncio.sleep(sleep_time)
            
            # Simulate success (90% success rate)
            import random
            if random.random() < 0.9:
                action.status = ActionStatus.COMPLETED
                action.result = {
                    "success": True,
                    "message": f"Successfully executed {action.action_type}",
                    "details": action.parameters
                }
                workflow.completed_actions += 1
            else:
                action.status = ActionStatus.FAILED
                action.error = f"Simulated failure for {action.action_type}"
                workflow.failed_actions += 1
            
            action.end_time = datetime.now(timezone.utc)
            
        except Exception as e:
            action.status = ActionStatus.FAILED
            action.error = str(e)
            action.end_time = datetime.now(timezone.utc)
            workflow.failed_actions += 1
    
    def get_workflow_status(self, workflow_id: str) -> Optional[Dict[str, Any]]:
        """Get the current status of a workflow"""
        
        workflow = (self.active_workflows.get(workflow_id) or 
                   self.completed_workflows.get(workflow_id))
        
        if not workflow:
            return None
        
        return {
            "workflow_id": workflow.workflow_id,
            "name": workflow.name,
            "status": workflow.status.value,
            "total_actions": workflow.total_actions,
            "completed_actions": workflow.completed_actions,
            "failed_actions": workflow.failed_actions,
            "created_at": workflow.created_at.isoformat(),
            "started_at": workflow.started_at.isoformat() if workflow.started_at else None,
            "completed_at": workflow.completed_at.isoformat() if workflow.completed_at else None
        }

# Global workflow engine instance
workflow_engine = WorkflowEngine()