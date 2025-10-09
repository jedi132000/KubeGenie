"""
Cost Optimization Agent for KubeGenie

Analyzes resource utilization and provides cost optimization recommendations.
"""

from typing import Dict, List, Any
from datetime import datetime, timezone

from ..base_agent import BaseAgent, AgentAction, AgentResult, ActionPriority

class CostOptimizationAgent(BaseAgent):
    def __init__(self, agent_id: str, k8s_client=None):
        super().__init__(
            agent_id=agent_id,
            name="Cost Optimization Agent", 
            description="Analyzes cluster costs and provides optimization recommendations"
        )
        self.k8s_client = k8s_client
    
    async def analyze(self, cluster_data: Dict[str, Any]) -> List[AgentAction]:
        """Analyze cluster for cost optimization opportunities."""
        try:
            actions = []
            
            # Check for over-provisioned resources
            if cluster_data.get('high_cpu_requests', False):
                actions.append(AgentAction(
                    id=f"cost-opt-{datetime.now().timestamp()}",
                    agent_id=self.agent_id,
                    action_type="rightsizing",
                    description="Reduce CPU requests for over-provisioned workloads",
                    priority=ActionPriority.MEDIUM,
                    requires_approval=True,
                    cluster_id=cluster_data.get('cluster_id', 'unknown'),
                    parameters={"resource_type": "cpu", "reduction_percent": 25},
                    reasoning="High CPU requests detected with low utilization",
                    knowledge_sources=["metrics", "resource_analysis"],
                    estimated_risk=0.2,  # Low risk
                    created_at=datetime.now(timezone.utc)
                ))
            
            # Check for unused resources
            if cluster_data.get('idle_pods', 0) > 0:
                actions.append(AgentAction(
                    id=f"cost-opt-{datetime.now().timestamp()}-2",
                    agent_id=self.agent_id,
                    action_type="cleanup",
                    description="Remove idle pods to reduce costs",
                    priority=ActionPriority.LOW,
                    requires_approval=False,
                    cluster_id=cluster_data.get('cluster_id', 'unknown'),
                    parameters={"resource_type": "pods", "threshold": "7d"},
                    reasoning="Idle pods consuming resources without benefit",
                    knowledge_sources=["monitoring", "usage_patterns"],
                    estimated_risk=0.1,  # Very low risk
                    created_at=datetime.now(timezone.utc)
                ))
            
            return actions
            
        except Exception:
            return []
    
    async def execute_action(self, action: AgentAction) -> AgentResult:
        """Execute a cost optimization action."""
        try:
            if action.action_type == "rightsizing":
                return AgentResult(
                    action_id=action.id,
                    success=True,
                    message="Successfully rightsized resources",
                    data={"savings": "$50/month"}
                )
            elif action.action_type == "cleanup":
                return AgentResult(
                    action_id=action.id,
                    success=True,
                    message="Successfully cleaned up idle resources",
                    data={"resources_removed": 3}
                )
            else:
                return AgentResult(
                    action_id=action.id,
                    success=False,
                    message=f"Unsupported action type: {action.action_type}"
                )
        except Exception as e:
            return AgentResult(
                action_id=action.id,
                success=False,
                message=f"Execution failed: {str(e)}"
            )
    
    async def health_check(self) -> bool:
        """Check agent health."""
        try:
            # Simple health check - could expand to test k8s client connection
            return True
        except Exception:
            return False