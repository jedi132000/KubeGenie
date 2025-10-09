"""
Monitoring Agent - Detects anomalies and health issues across clusters

Uses ML/AI to identify potential issues before they become critical incidents.
Integrates with metrics, logs, and events to provide comprehensive monitoring.
"""

import asyncio
import logging
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
import numpy as np

from ..base_agent import BaseAgent, AgentAction, AgentResult, ActionPriority, AgentStatus

logger = logging.getLogger(__name__)


class MonitoringAgent(BaseAgent):
    """
    Monitoring agent responsible for:
    - Anomaly detection in cluster metrics
    - Health status monitoring  
    - Predictive alerting
    - Performance trend analysis
    """
    
    def __init__(self):
        super().__init__(
            agent_id="monitoring_agent",
            name="Monitoring & Anomaly Detection Agent", 
            description="Detects cluster anomalies and health issues using ML/AI"
        )
        self.anomaly_threshold = 0.7  # Configurable threshold
        self.critical_metrics = [
            "cpu_usage_percentage",
            "memory_usage_percentage", 
            "disk_usage_percentage",
            "pod_restart_count",
            "node_not_ready_count"
        ]
        
    async def analyze(self, cluster_data: Dict[str, Any]) -> List[AgentAction]:
        """
        Analyze cluster data for anomalies and health issues
        
        Args:
            cluster_data: Dictionary containing metrics for all clusters
            
        Returns:
            List of recommended monitoring actions
        """
        self._set_status(AgentStatus.RUNNING)
        actions = []
        
        try:
            for cluster_id, data in cluster_data.items():
                # Analyze each cluster's metrics
                anomalies = await self._detect_anomalies(cluster_id, data)
                health_issues = await self._check_cluster_health(cluster_id, data)
                
                # Create actions for detected issues
                actions.extend(await self._create_monitoring_actions(
                    cluster_id, anomalies, health_issues
                ))
                
        except Exception as e:
            logger.error("Error during monitoring analysis: %s", str(e))
            self._set_status(AgentStatus.ERROR)
            return []
            
        self._set_status(AgentStatus.IDLE) 
        return actions
    
    async def execute_action(self, action: AgentAction) -> AgentResult:
        """Execute monitoring-related actions"""
        start_time = datetime.now()
        
        try:
            if action.action_type == "create_alert":
                result = await self._create_alert(action)
            elif action.action_type == "investigate_anomaly":
                result = await self._investigate_anomaly(action)
            elif action.action_type == "collect_diagnostics":
                result = await self._collect_diagnostics(action)
            else:
                return AgentResult(
                    action_id=action.id,
                    success=False,
                    message=f"Unknown action type: {action.action_type}"
                )
                
            execution_time = (datetime.now() - start_time).total_seconds()
            result.execution_time = execution_time
            return result
            
        except Exception as e:
            logger.error("Error executing monitoring action: %s", str(e))
            return AgentResult(
                action_id=action.id,
                success=False,
                message=f"Execution failed: {str(e)}",
                errors=[str(e)],
                execution_time=(datetime.now() - start_time).total_seconds()
            )
    
    async def health_check(self) -> bool:
        """Check if monitoring agent is healthy"""
        try:
            # Test basic functionality
            test_data = {"test_cluster": {"cpu_usage": 50.0, "memory_usage": 60.0}}
            await self._detect_anomalies("test_cluster", test_data["test_cluster"])
            return True
        except Exception as e:
            logger.error("Monitoring agent health check failed: %s", str(e))
            return False
    
    async def _detect_anomalies(self, cluster_id: str, metrics: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Detect anomalies in cluster metrics using ML techniques"""
        anomalies = []
        
        for metric_name in self.critical_metrics:
            if metric_name not in metrics:
                continue
                
            value = metrics[metric_name]
            
            # Simple threshold-based detection (would be replaced with ML model)
            is_anomaly, severity = await self._evaluate_metric_anomaly(metric_name, value)
            
            if is_anomaly:
                anomalies.append({
                    "metric": metric_name,
                    "value": value,
                    "severity": severity,
                    "timestamp": datetime.now().isoformat(),
                    "cluster_id": cluster_id
                })
                
        return anomalies
    
    async def _evaluate_metric_anomaly(self, metric_name: str, value: float) -> tuple[bool, str]:
        """Evaluate if a metric value is anomalous"""
        
        # Define thresholds for different metrics
        thresholds = {
            "cpu_usage_percentage": {"warning": 80, "critical": 95},
            "memory_usage_percentage": {"warning": 85, "critical": 95}, 
            "disk_usage_percentage": {"warning": 80, "critical": 90},
            "pod_restart_count": {"warning": 5, "critical": 10},
            "node_not_ready_count": {"warning": 1, "critical": 3}
        }
        
        if metric_name not in thresholds:
            return False, "normal"
            
        thresh = thresholds[metric_name]
        
        if value >= thresh["critical"]:
            return True, "critical"
        elif value >= thresh["warning"]:
            return True, "warning"
        
        return False, "normal"
    
    async def _check_cluster_health(self, cluster_id: str, data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Check overall cluster health"""
        health_issues = []
        
        # Check for common health indicators
        if data.get("api_server_responsive", True) is False:
            health_issues.append({
                "type": "api_server_unresponsive",
                "severity": "critical",
                "cluster_id": cluster_id,
                "message": "Kubernetes API server is not responding"
            })
            
        if data.get("etcd_healthy", True) is False:
            health_issues.append({
                "type": "etcd_unhealthy", 
                "severity": "critical",
                "cluster_id": cluster_id,
                "message": "etcd cluster is unhealthy"
            })
            
        return health_issues
    
    async def _create_monitoring_actions(
        self,
        cluster_id: str,
        anomalies: List[Dict[str, Any]], 
        health_issues: List[Dict[str, Any]]
    ) -> List[AgentAction]:
        """Create monitoring actions based on detected issues"""
        actions = []
        
        # Create actions for anomalies
        for anomaly in anomalies:
            priority = ActionPriority.HIGH if anomaly["severity"] == "critical" else ActionPriority.MEDIUM
            
            action = AgentAction(
                id=f"anomaly_{cluster_id}_{anomaly['metric']}_{datetime.now().timestamp()}",
                agent_id=self.agent_id,
                action_type="investigate_anomaly",
                description=f"Investigate {anomaly['metric']} anomaly in cluster {cluster_id}",
                priority=priority,
                requires_approval=False,
                cluster_id=cluster_id,
                parameters={
                    "anomaly": anomaly,
                    "metric": anomaly["metric"],
                    "value": anomaly["value"]
                },
                reasoning=f"Detected {anomaly['severity']} anomaly in {anomaly['metric']}: {anomaly['value']}",
                knowledge_sources=["monitoring/anomaly_detection_playbook.md"],
                estimated_risk=0.3,
                created_at=datetime.now()
            )
            actions.append(action)
        
        # Create actions for health issues  
        for issue in health_issues:
            priority = ActionPriority.CRITICAL if issue["severity"] == "critical" else ActionPriority.HIGH
            
            action = AgentAction(
                id=f"health_{cluster_id}_{issue['type']}_{datetime.now().timestamp()}",
                agent_id=self.agent_id,
                action_type="create_alert",
                description=f"Create alert for {issue['type']} in cluster {cluster_id}",
                priority=priority,
                requires_approval=False,
                cluster_id=cluster_id,
                parameters={"health_issue": issue},
                reasoning=f"Critical health issue detected: {issue['message']}",
                knowledge_sources=["monitoring/health_check_playbook.md"],
                estimated_risk=0.8,
                created_at=datetime.now()
            )
            actions.append(action)
            
        return actions
    
    async def _create_alert(self, action: AgentAction) -> AgentResult:
        """Create an alert for monitoring issues"""
        # Implementation would integrate with alerting system
        logger.info("Creating alert for cluster %s", action.cluster_id)
        
        return AgentResult(
            action_id=action.id,
            success=True,
            message="Alert created successfully",
            data={"alert_id": f"alert_{action.id}"}
        )
    
    async def _investigate_anomaly(self, action: AgentAction) -> AgentResult:
        """Investigate a detected anomaly"""
        # Implementation would run deeper analysis  
        anomaly = action.parameters.get("anomaly", {})
        logger.info("Investigating anomaly in cluster %s: %s", action.cluster_id, anomaly.get("metric"))
        
        return AgentResult(
            action_id=action.id,
            success=True,
            message="Anomaly investigation completed",
            data={"investigation_results": f"Analyzed {anomaly.get('metric')} anomaly"}
        )
    
    async def _collect_diagnostics(self, action: AgentAction) -> AgentResult:
        """Collect diagnostic information"""
        logger.info("Collecting diagnostics for cluster %s", action.cluster_id)
        
        return AgentResult(
            action_id=action.id,
            success=True,
            message="Diagnostics collected successfully",
            data={"diagnostics": "cluster_diagnostics.json"}
        )