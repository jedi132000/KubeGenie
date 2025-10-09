"""
FastAPI Main Application for KubeGenie

Central API gateway that coordinates between agents, orchestrator,
and provides endpoints for the Gradio UI.
"""

from fastapi import FastAPI, HTTPException, BackgroundTasks, Form
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import asyncio
import logging
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta

from ..orchestrator.coordinator import AIOrchestrator
from ..agents.monitoring.monitoring_agent import MonitoringAgent
from ..agents.remediation.remediation_agent import RemediationAgent
from ..agents.cost_optimization.cost_optimization_agent import CostOptimizationAgent
from ..agents.security.security_agent import SecurityAgent
from ..vector_db.chroma_manager import initialize_vector_db, search_knowledge_base, get_knowledge_stats
from ..workflows.automation_engine import workflow_engine
from ..analytics.advanced_engine import AdvancedAnalyticsEngine
from ..cluster.manager import cluster_manager

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Global orchestrator instance
orchestrator = AIOrchestrator()

# Global analytics engine instance
analytics_engine = AdvancedAnalyticsEngine()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan management"""
    logger.info("Starting KubeGenie API...")
    
    # Initialize vector database
    vector_db_success = await initialize_vector_db()
    if vector_db_success:
        logger.info("Vector database initialized successfully")
    else:
        logger.warning("Failed to initialize vector database")
    
    # Initialize agents
    monitoring_agent = MonitoringAgent()
    remediation_agent = RemediationAgent("remediation_agent_001")
    cost_optimization_agent = CostOptimizationAgent("cost_optimization_agent_001")
    security_agent = SecurityAgent("security_agent_001")
    
    await orchestrator.register_agent(monitoring_agent)
    await orchestrator.register_agent(cost_optimization_agent)
    await orchestrator.register_agent(security_agent)
    
    logger.info("KubeGenie API started successfully")
    yield
    
    logger.info("Shutting down KubeGenie API...")
    # Cleanup would go here


# Create FastAPI app
app = FastAPI(
    title="KubeGenie API",
    description="AI-Powered Kubernetes Multi-Cluster Management Platform",
    version="1.0.0",
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Authentication endpoints  
@app.post("/api/v1/auth/login")
async def login_form(username: str = Form(...), password: str = Form(...)):
    """Authentication endpoint for form data"""
    logger.info(f"Login attempt for user: {username}")
    
    # Simple authentication for development - accept any credentials
    if username and password:
        access_token = f"demo_token_{username}_{datetime.now().timestamp()}"
        return {
            "access_token": access_token,
            "token_type": "bearer", 
            "expires_in": 3600,
            "user": username
        }
    else:
        raise HTTPException(status_code=401, detail="Invalid credentials")


@app.post("/api/v1/auth/login-json")  
async def login_json(credentials: Dict[str, str]):
    """Authentication endpoint for JSON data"""
    username = credentials.get("username", "")
    password = credentials.get("password", "")
    
    logger.info(f"Login attempt for user: {username}")
    
    # Simple authentication for development - accept any credentials
    if username and password:
        access_token = f"demo_token_{username}_{datetime.now().timestamp()}"
        return {
            "access_token": access_token,
            "token_type": "bearer",
            "expires_in": 3600,
            "user": username
        }
    else:
        raise HTTPException(status_code=401, detail="Invalid credentials")


@app.get("/api/v1/auth/verify")
async def verify_token():
    """Verify authentication token"""
    return {"valid": True, "user": "demo_user"}


@app.get("/")
async def root():
    """Health check endpoint"""
    return {"message": "KubeGenie API is running", "status": "healthy"}


@app.get("/api/v1/status")
async def get_system_status():
    """Get overall system status"""
    try:
        orchestrator_status = await orchestrator.get_orchestrator_status()
        agent_status = await orchestrator.get_agent_status()
        
        return {
            "orchestrator": orchestrator_status,
            "agents": agent_status,
            "timestamp": "2024-01-01T00:00:00Z"  # Would use actual timestamp
        }
    except Exception as e:
        logger.error("Error getting system status: %s", str(e))
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/v1/analyze")
async def analyze_clusters(cluster_data: Dict[str, Any]):
    """
    Analyze cluster data and get recommended actions
    
    Args:
        cluster_data: Dictionary containing metrics and state for all clusters
        
    Returns:
        List of recommended actions from all agents
    """
    try:
        actions = await orchestrator.analyze_clusters(cluster_data)
        
        # Convert actions to serializable format
        action_dicts = []
        for action in actions:
            action_dict = {
                "id": action.id,
                "agent_id": action.agent_id,
                "action_type": action.action_type,
                "description": action.description,
                "priority": action.priority.name,
                "requires_approval": action.requires_approval,
                "cluster_id": action.cluster_id,
                "parameters": action.parameters,
                "reasoning": action.reasoning,
                "knowledge_sources": action.knowledge_sources,
                "estimated_risk": action.estimated_risk,
                "created_at": action.created_at.isoformat()
            }
            action_dicts.append(action_dict)
            
        return {"actions": action_dicts}
        
    except Exception as e:
        logger.error("Error analyzing clusters: %s", str(e))
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/v1/execute")
async def execute_actions(
    action_ids: List[str],
    background_tasks: BackgroundTasks
):
    """
    Execute a list of actions by their IDs
    
    Args:
        action_ids: List of action IDs to execute
        
    Returns:
        Task ID for tracking execution status
    """
    try:
        # In a real implementation, would look up actions by ID
        # and execute them through the orchestrator
        
        task_id = f"exec_task_{len(action_ids)}"
        
        # Add background task for execution
        background_tasks.add_task(
            _execute_actions_background, 
            action_ids
        )
        
        return {
            "task_id": task_id,
            "status": "submitted",
            "action_count": len(action_ids)
        }
        
    except Exception as e:
        logger.error("Error submitting actions for execution: %s", str(e))
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/v1/clusters")
async def get_clusters():
    """Get list of all managed clusters"""
    # Mock data - would come from cluster registry
    return {
        "clusters": [
            {
                "id": "prod-us-east-1",
                "name": "Production US East",
                "status": "healthy",
                "nodes": 15,
                "pods": 450,
                "last_updated": "2024-01-01T00:00:00Z"
            },
            {
                "id": "staging-us-west-2", 
                "name": "Staging US West",
                "status": "warning",
                "nodes": 8,
                "pods": 120,
                "last_updated": "2024-01-01T00:00:00Z"
            }
        ]
    }


@app.get("/api/v1/knowledge/search")
async def search_knowledge_endpoint(query: str, limit: int = 10):
    """
    Search the knowledge base using vector similarity
    
    Args:
        query: Search query
        limit: Maximum number of results
        
    Returns:
        List of relevant knowledge base entries
    """
    try:
        # Use actual vector database search
        search_results = await search_knowledge_base(query, limit)
        
        # Convert search results to API response format
        results = []
        for search_result in search_results:
            result = {
                "id": search_result.document.id,
                "title": search_result.document.title,
                "content": search_result.document.content[:500] + "..." if len(search_result.document.content) > 500 else search_result.document.content,
                "source": search_result.document.source,
                "score": round(search_result.score, 3),
                "metadata": search_result.document.metadata
            }
            results.append(result)
        
        return {
            "query": query,
            "results": results,
            "total_count": len(results)
        }
        
    except Exception as e:
        logger.error("Error searching knowledge base: %s", str(e))
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/v1/knowledge/stats")
async def get_knowledge_base_stats():
    """
    Get knowledge base statistics
    
    Returns:
        Knowledge base statistics and metadata
    """
    try:
        stats = await get_knowledge_stats()
        return stats
        
    except Exception as e:
        logger.error("Error getting knowledge base stats: %s", str(e))
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/v1/k8s/cluster-info")
async def get_cluster_info():
    """
    Get basic cluster information for the UI
    
    Returns:
        Cluster information and status
    """
    try:
        # Mock cluster information for development
        cluster_info = {
            "clusters": [
                {
                    "name": "demo-cluster",
                    "status": "healthy",
                    "nodes": 3,
                    "pods": 25,
                    "services": 8,
                    "version": "v1.28.2",
                    "provider": "local"
                }
            ],
            "total_clusters": 1,
            "healthy_clusters": 1,
            "last_updated": datetime.now().isoformat()
        }
        
        return cluster_info
        
    except Exception as e:
        logger.error("Error getting cluster info: %s", str(e))
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/v1/workflows/create")
async def create_workflow_from_analysis(analysis_result: Dict[str, Any]):
    """
    Create an automated workflow from analysis results
    
    Args:
        analysis_result: Analysis result containing actions from agents
        
    Returns:
        Workflow creation status and workflow ID
    """
    try:
        workflow = await workflow_engine.create_workflow_from_analysis(analysis_result)
        
        return {
            "workflow_id": workflow.workflow_id,
            "name": workflow.name,
            "description": workflow.description,
            "total_actions": workflow.total_actions,
            "status": workflow.status.value,
            "created_at": workflow.created_at.isoformat()
        }
        
    except Exception as e:
        logger.error("Error creating workflow: %s", str(e))
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/v1/workflows/{workflow_id}/execute")
async def execute_workflow(workflow_id: str):
    """
    Execute a workflow with dependency management
    
    Args:
        workflow_id: ID of the workflow to execute
        
    Returns:
        Execution results and status
    """
    try:
        # Get workflow from active or completed workflows
        workflow = (workflow_engine.active_workflows.get(workflow_id) or 
                   workflow_engine.completed_workflows.get(workflow_id))
        
        if not workflow:
            raise HTTPException(status_code=404, detail="Workflow not found")
        
        if workflow.status.value != "pending":
            raise HTTPException(status_code=400, detail=f"Workflow already {workflow.status.value}")
        
        result = await workflow_engine.execute_workflow(workflow)
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Error executing workflow: %s", str(e))
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/v1/workflows/{workflow_id}/status")
async def get_workflow_status(workflow_id: str):
    """
    Get the current status of a workflow
    
    Args:
        workflow_id: ID of the workflow
        
    Returns:
        Current workflow status and progress
    """
    try:
        status = workflow_engine.get_workflow_status(workflow_id)
        
        if not status:
            raise HTTPException(status_code=404, detail="Workflow not found")
        
        return status
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Error getting workflow status: %s", str(e))
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/v1/workflows/analyze-and-execute")
async def analyze_and_execute_workflow(cluster_data: Dict[str, Any]):
    """
    Complete workflow: Analyze cluster data and execute resulting workflow
    
    Args:
        cluster_data: Dictionary containing cluster metrics and state
        
    Returns:
        Analysis results and workflow execution status
    """
    try:
        # Step 1: Analyze clusters
        logger.info("Starting analyze-and-execute workflow")
        actions = await orchestrator.analyze_clusters(cluster_data)
        
        # Convert actions to serializable format
        action_dicts = []
        for action in actions:
            action_dict = {
                "id": action.id,
                "agent_id": action.agent_id,
                "action_type": action.action_type,
                "description": action.description,
                "priority": action.priority.name,
                "requires_approval": action.requires_approval,
                "cluster_id": action.cluster_id,
                "parameters": action.parameters,
                "reasoning": action.reasoning,
                "knowledge_sources": action.knowledge_sources,
                "estimated_risk": action.estimated_risk,
                "created_at": action.created_at.isoformat()
            }
            action_dicts.append(action_dict)
        
        analysis_result = {"actions": action_dicts}
        
        # Step 2: Create workflow
        workflow = await workflow_engine.create_workflow_from_analysis(analysis_result)
        
        # Step 3: Execute workflow
        execution_result = await workflow_engine.execute_workflow(workflow)
        
        return {
            "analysis": {
                "total_actions": len(action_dicts),
                "actions": action_dicts
            },
            "workflow": execution_result
        }
        
    except Exception as e:
        logger.error("Error in analyze-and-execute workflow: %s", str(e))
        raise HTTPException(status_code=500, detail=str(e))


# Analytics endpoints
@app.post("/api/v1/analytics/ingest")
async def ingest_metrics(metrics_data: Dict[str, Any]):
    """Ingest metrics data for analytics processing"""
    try:
        cluster_id = metrics_data.get("cluster_id", "default")
        metrics = metrics_data.get("metrics", [])
        
        logger.info("Ingesting %d metrics for cluster %s", len(metrics), cluster_id)
        
        # Process metrics using the analytics engine
        result = await analytics_engine.ingest_metrics(cluster_id, metrics_data)
        
        return {
            "status": "success",
            "result": result,
            "cluster_id": cluster_id
        }
        
    except Exception as e:
        logger.error("Error ingesting metrics: %s", str(e))
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/v1/analytics/dashboard")
async def get_analytics_dashboard(cluster_id: Optional[str] = None):
    """Get comprehensive analytics dashboard data"""
    try:
        logger.info("Fetching dashboard data for cluster: %s", cluster_id or "all")
        
        dashboard_data = await analytics_engine.get_dashboard_data(cluster_id)
        
        return {
            "status": "success",
            "dashboard": dashboard_data,
            "generated_at": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error("Error fetching dashboard data: %s", str(e))
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/v1/analytics/metrics/{metric_name}")
async def get_metric_timeseries(metric_name: str, cluster_id: Optional[str] = None, hours: int = 24):
    """Get time series data for a specific metric"""
    try:
        logger.info("Fetching time series for metric %s, cluster: %s", metric_name, cluster_id or "all")
        
        # Get time series data (simplified implementation)
        if metric_name in analytics_engine.metrics_store:
            time_series = analytics_engine.metrics_store[metric_name]
            cutoff_time = datetime.now() - timedelta(hours=hours)
            
            recent_points = [p for p in time_series.data_points 
                           if p.timestamp >= cutoff_time and
                           (not cluster_id or p.labels.get("cluster_id") == cluster_id)]
            
            return {
                "status": "success",
                "metric_name": metric_name,
                "cluster_id": cluster_id,
                "data_points": len(recent_points),
                "time_series": [
                    {
                        "timestamp": p.timestamp.isoformat(),
                        "value": p.value,
                        "labels": p.labels
                    }
                    for p in recent_points[-100:]  # Last 100 points
                ]
            }
        else:
            return {
                "status": "success",
                "metric_name": metric_name,
                "cluster_id": cluster_id,
                "data_points": 0,
                "time_series": []
            }
        
    except Exception as e:
        logger.error("Error fetching metric time series: %s", str(e))
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/v1/analytics/alerts")
async def get_active_alerts(cluster_id: Optional[str] = None):
    """Get active alerts"""
    try:
        logger.info("Fetching active alerts for cluster: %s", cluster_id or "all")
        
        active_alerts = [a for a in analytics_engine.active_alerts.values() 
                        if not cluster_id or a.cluster_id == cluster_id]
        
        return {
            "status": "success",
            "alerts": [
                {
                    "alert_id": alert.alert_id,
                    "severity": alert.severity.value,
                    "title": alert.title,
                    "description": alert.description,
                    "metric_name": alert.metric_name,
                    "current_value": alert.current_value,
                    "threshold": alert.threshold,
                    "cluster_id": alert.cluster_id,
                    "created_at": alert.created_at.isoformat(),
                    "resolved_at": alert.resolved_at.isoformat() if alert.resolved_at else None
                }
                for alert in active_alerts
            ],
            "total_alerts": len(active_alerts)
        }
        
    except Exception as e:
        logger.error("Error fetching alerts: %s", str(e))
        raise HTTPException(status_code=500, detail=str(e))


# Cluster Management endpoints
@app.get("/api/v1/clusters/discover")
async def discover_clusters():
    """Discover available Kubernetes clusters"""
    try:
        logger.info("Discovering available clusters")
        
        clusters = await cluster_manager.discover_clusters()
        
        return {
            "status": "success",
            "clusters": [
                {
                    "name": cluster.name,
                    "type": cluster.cluster_type,
                    "context": cluster.context,
                    "connected": cluster.connected
                }
                for cluster in clusters
            ],
            "total_clusters": len(clusters)
        }
        
    except Exception as e:
        logger.error("Error discovering clusters: %s", str(e))
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/v1/clusters/{cluster_name}/connect")
async def connect_cluster(cluster_name: str):
    """Connect to a specific Kubernetes cluster"""
    try:
        logger.info("Connecting to cluster: %s", cluster_name)
        
        success = await cluster_manager.connect_to_cluster(cluster_name)
        
        if success:
            return {
                "status": "success",
                "message": f"Successfully connected to cluster {cluster_name}",
                "cluster_name": cluster_name,
                "connected": True
            }
        else:
            raise HTTPException(status_code=400, detail=f"Failed to connect to cluster {cluster_name}")
            
    except Exception as e:
        logger.error("Error connecting to cluster %s: %s", cluster_name, str(e))
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/v1/clusters/{cluster_name}/health")
async def get_cluster_health_status(cluster_name: Optional[str] = None):
    """Get health status of cluster"""
    try:
        logger.info("Getting cluster health for: %s", cluster_name or "active cluster")
        
        health_data = await cluster_manager.get_cluster_health(cluster_name)
        
        return {
            "status": "success",
            "health": health_data
        }
        
    except Exception as e:
        logger.error("Error getting cluster health: %s", str(e))
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/v1/clusters/{cluster_name}/metrics")
async def get_cluster_metrics_data(cluster_name: Optional[str] = None):
    """Get metrics from cluster for analytics"""
    try:
        logger.info("Getting cluster metrics for: %s", cluster_name or "active cluster")
        
        metrics_data = await cluster_manager.get_cluster_metrics(cluster_name)
        
        # Also ingest the metrics into analytics engine
        if "metrics" in metrics_data and metrics_data["metrics"]:
            analytics_result = await analytics_engine.ingest_metrics(
                cluster_name or "default", 
                metrics_data
            )
            return {
                "status": "success",
                "metrics": metrics_data,
                "analytics_ingested": analytics_result.get("processed_metrics", 0)
            }
        else:
            return {
                "status": "success", 
                "metrics": metrics_data
            }
        
    except Exception as e:
        logger.error("Error getting cluster metrics: %s", str(e))
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/v1/clusters/{cluster_name}/kubectl")
async def execute_kubectl_command(cluster_name: str, command_data: Dict[str, Any]):
    """Execute kubectl command on cluster"""
    try:
        command = command_data.get("command", [])
        namespace = command_data.get("namespace")
        
        logger.info("Executing kubectl command on %s: %s", cluster_name, " ".join(command))
        
        # First ensure we're connected to the cluster
        if cluster_manager.active_cluster != cluster_name:
            await cluster_manager.connect_to_cluster(cluster_name)
        
        result = await cluster_manager.execute_kubectl_command(command, namespace)
        
        return {
            "status": "success",
            "cluster_name": cluster_name,
            "command": command,
            "result": result
        }
        
    except Exception as e:
        logger.error("Error executing kubectl command: %s", str(e))
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/v1/clusters")
async def list_clusters():
    """List all configured clusters"""
    try:
        clusters = cluster_manager.get_cluster_list()
        active_cluster = cluster_manager.get_active_cluster()
        
        return {
            "status": "success",
            "clusters": clusters,
            "active_cluster": active_cluster,
            "total_clusters": len(clusters)
        }
        
    except Exception as e:
        logger.error("Error listing clusters: %s", str(e))
        raise HTTPException(status_code=500, detail=str(e))


async def _execute_actions_background(action_ids: List[str]):
    """Background task for executing actions"""
    logger.info("Executing actions in background: %s", action_ids)
    
    # Implementation would:
    # 1. Look up actions by ID
    # 2. Execute through orchestrator
    # 3. Store results
    # 4. Send notifications
    
    # Mock execution
    await asyncio.sleep(2)
    logger.info("Background execution completed for actions: %s", action_ids)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)