"""
Advanced Analytics Engine for KubeGenie

Provides real-time cluster metrics analysis, trend detection,
performance dashboards, and predictive alerting capabilities.
"""

import logging
from typing import Dict, List, Any, Optional
from datetime import datetime, timezone, timedelta
from dataclasses import dataclass
from enum import Enum
import statistics

logger = logging.getLogger(__name__)

class MetricType(Enum):
    GAUGE = "gauge"
    COUNTER = "counter" 
    HISTOGRAM = "histogram"
    SUMMARY = "summary"

class AlertSeverity(Enum):
    INFO = "info"
    WARNING = "warning"
    CRITICAL = "critical"
    EMERGENCY = "emergency"

@dataclass
class MetricPoint:
    """A single metric data point"""
    timestamp: datetime
    value: float
    labels: Dict[str, str]

@dataclass
class TimeSeries:
    """Time series data for a metric"""
    metric_name: str
    metric_type: MetricType
    data_points: List[MetricPoint]
    unit: str = ""
    description: str = ""

@dataclass
class Alert:
    """System alert based on metric analysis"""
    alert_id: str
    severity: AlertSeverity
    title: str
    description: str
    metric_name: str
    current_value: float
    threshold: float
    cluster_id: str
    created_at: datetime
    resolved_at: Optional[datetime] = None

class TrendAnalyzer:
    """Analyzes trends in time series data"""
    
    @staticmethod
    def calculate_trend(data_points: List[MetricPoint], window_minutes: int = 30) -> Dict[str, Any]:
        """Calculate trend analysis for metric data points"""
        
        if len(data_points) < 2:
            return {"trend": "insufficient_data", "slope": 0, "confidence": 0}
        
        # Filter to recent window
        cutoff_time = datetime.now(timezone.utc) - timedelta(minutes=window_minutes)
        recent_points = [p for p in data_points if p.timestamp >= cutoff_time]
        
        if len(recent_points) < 2:
            recent_points = data_points[-10:]  # Use last 10 points if no recent data
        
        # Calculate linear trend
        x_values = [(p.timestamp - recent_points[0].timestamp).total_seconds() for p in recent_points]
        y_values = [p.value for p in recent_points]
        
        n = len(recent_points)
        if n < 2:
            return {"trend": "insufficient_data", "slope": 0, "confidence": 0}
        
        # Linear regression
        x_mean = sum(x_values) / n
        y_mean = sum(y_values) / n
        
        numerator = sum((x_values[i] - x_mean) * (y_values[i] - y_mean) for i in range(n))
        denominator = sum((x_values[i] - x_mean) ** 2 for i in range(n))
        
        if denominator == 0:
            slope = 0
        else:
            slope = numerator / denominator
        
        # Determine trend direction and confidence
        if abs(slope) < 0.001:
            trend = "stable"
            confidence = 0.5
        elif slope > 0:
            trend = "increasing"
            confidence = min(abs(slope) * 100, 1.0)
        else:
            trend = "decreasing"
            confidence = min(abs(slope) * 100, 1.0)
        
        return {
            "trend": trend,
            "slope": slope,
            "confidence": confidence,
            "data_points": len(recent_points),
            "time_window": window_minutes
        }
    
    @staticmethod
    def detect_anomalies(data_points: List[MetricPoint], threshold_std: float = 2.0) -> List[MetricPoint]:
        """Detect anomalous data points using statistical analysis"""
        
        if len(data_points) < 10:
            return []
        
        values = [p.value for p in data_points]
        mean_val = statistics.mean(values)
        std_val = statistics.stdev(values) if len(values) > 1 else 0
        
        if std_val == 0:
            return []
        
        anomalies = []
        for point in data_points:
            z_score = abs(point.value - mean_val) / std_val
            if z_score > threshold_std:
                anomalies.append(point)
        
        return anomalies

class AdvancedAnalyticsEngine:
    """Main analytics engine for processing cluster metrics"""
    
    def __init__(self):
        self.metrics_store: Dict[str, TimeSeries] = {}
        self.active_alerts: Dict[str, Alert] = {}
        self.resolved_alerts: List[Alert] = []
        self.trend_analyzer = TrendAnalyzer()
        
        # Alert thresholds (configurable)
        self.alert_thresholds = {
            "cpu_usage_percent": {"warning": 80, "critical": 95},
            "memory_usage_percent": {"warning": 85, "critical": 95},
            "disk_usage_percent": {"warning": 85, "critical": 95},
            "pod_restart_rate": {"warning": 5, "critical": 10},
            "node_not_ready_count": {"warning": 1, "critical": 2},
            "failed_pod_count": {"warning": 3, "critical": 5}
        }
    
    async def ingest_metrics(self, cluster_id: str, metrics_data: Dict[str, Any]) -> Dict[str, Any]:
        """Ingest and process real-time metrics from clusters"""
        
        timestamp = datetime.now(timezone.utc)
        processed_metrics = []
        new_alerts = []
        
        logger.info("Ingesting metrics for cluster %s", cluster_id)
        
        # Handle both flat dictionary and API format with 'metrics' array
        metrics_to_process = []
        
        if "metrics" in metrics_data and isinstance(metrics_data["metrics"], list):
            # API format: {"metrics": [{"name": "cpu", "value": 50, ...}, ...]}
            for metric_item in metrics_data["metrics"]:
                if isinstance(metric_item, dict) and "name" in metric_item and "value" in metric_item:
                    metric_timestamp = timestamp
                    if "timestamp" in metric_item:
                        try:
                            metric_timestamp = datetime.fromisoformat(metric_item["timestamp"].replace('Z', '+00:00'))
                        except (ValueError, TypeError):
                            metric_timestamp = timestamp
                            
                    metrics_to_process.append({
                        "name": metric_item["name"],
                        "value": float(metric_item["value"]),
                        "timestamp": metric_timestamp,
                        "labels": metric_item.get("labels", {})
                    })
        else:
            # Flat dictionary format: {"cpu_usage": 50, "memory_usage": 70}
            for metric_name, metric_value in metrics_data.items():
                if isinstance(metric_value, (int, float)):
                    metrics_to_process.append({
                        "name": metric_name,
                        "value": float(metric_value),
                        "timestamp": timestamp,
                        "labels": {"cluster_id": cluster_id}
                    })
        
        # Process metrics
        for metric_info in metrics_to_process:
            metric_name = metric_info["name"]
            metric_value = metric_info["value"]
            metric_timestamp = metric_info["timestamp"]
            labels = dict(metric_info["labels"])
            labels["cluster_id"] = cluster_id
            
            # Create metric point
            point = MetricPoint(
                timestamp=metric_timestamp,
                value=float(metric_value),
                labels=labels
            )
            
            # Store in time series
            if metric_name not in self.metrics_store:
                self.metrics_store[metric_name] = TimeSeries(
                    metric_name=metric_name,
                    metric_type=MetricType.GAUGE,
                    data_points=[],
                    unit=self._get_metric_unit(metric_name),
                    description=self._get_metric_description(metric_name)
                )
            
            self.metrics_store[metric_name].data_points.append(point)
            
            # Keep only last 1000 points per metric
            if len(self.metrics_store[metric_name].data_points) > 1000:
                self.metrics_store[metric_name].data_points = \
                    self.metrics_store[metric_name].data_points[-1000:]
            
            processed_metrics.append({
                "metric_name": metric_name,
                "value": metric_value,
                "timestamp": metric_timestamp.isoformat()
            })
            
            # Check for alerts
            alert = self._check_alert_threshold(metric_name, metric_value, cluster_id, metric_timestamp)
            if alert:
                new_alerts.append(alert)
        
        return {
            "cluster_id": cluster_id,
            "processed_metrics": len(processed_metrics),
            "metrics": processed_metrics,
            "new_alerts": len(new_alerts),
            "alerts": [self._alert_to_dict(alert) for alert in new_alerts],
            "timestamp": timestamp.isoformat()
        }
    
    async def get_dashboard_data(self, cluster_id: Optional[str] = None, time_window_hours: int = 24) -> Dict[str, Any]:
        """Generate comprehensive dashboard data"""
        
        cutoff_time = datetime.now(timezone.utc) - timedelta(hours=time_window_hours)
        
        dashboard_data = {
            "overview": await self._get_cluster_overview(cluster_id, cutoff_time),
            "metrics": await self._get_metrics_summary(cluster_id, cutoff_time),
            "trends": await self._get_trend_analysis(cluster_id, cutoff_time),
            "alerts": await self._get_alerts_summary(cluster_id),
            "performance": await self._get_performance_insights(cluster_id, cutoff_time),
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "time_window_hours": time_window_hours
        }
        
        return dashboard_data
    
    async def _get_cluster_overview(self, cluster_id: Optional[str], cutoff_time: datetime) -> Dict[str, Any]:
        """Get high-level cluster overview"""
        
        # Simulate cluster overview data
        return {
            "total_clusters": 1 if cluster_id else 3,
            "healthy_clusters": 1,
            "clusters_with_alerts": len([a for a in self.active_alerts.values() 
                                       if not cluster_id or a.cluster_id == cluster_id]),
            "total_metrics": len(self.metrics_store),
            "data_points_collected": sum(len(ts.data_points) for ts in self.metrics_store.values()),
            "active_alerts": len(self.active_alerts),
            "resolved_alerts_24h": len([a for a in self.resolved_alerts 
                                      if a.resolved_at and a.resolved_at >= cutoff_time])
        }
    
    async def _get_metrics_summary(self, cluster_id: Optional[str], cutoff_time: datetime) -> Dict[str, Any]:
        """Get summary of key metrics"""
        
        metrics_summary = {}
        
        for metric_name, time_series in self.metrics_store.items():
            recent_points = [p for p in time_series.data_points 
                           if p.timestamp >= cutoff_time and 
                           (not cluster_id or p.labels.get("cluster_id") == cluster_id)]
            
            if recent_points:
                values = [p.value for p in recent_points]
                metrics_summary[metric_name] = {
                    "current": recent_points[-1].value,
                    "average": statistics.mean(values),
                    "min": min(values),
                    "max": max(values),
                    "data_points": len(recent_points),
                    "unit": time_series.unit,
                    "description": time_series.description
                }
        
        return metrics_summary
    
    async def _get_trend_analysis(self, cluster_id: Optional[str], cutoff_time: datetime) -> Dict[str, Any]:
        """Get trend analysis for key metrics"""
        
        trend_analysis = {}
        
        for metric_name, time_series in self.metrics_store.items():
            recent_points = [p for p in time_series.data_points 
                           if p.timestamp >= cutoff_time and
                           (not cluster_id or p.labels.get("cluster_id") == cluster_id)]
            
            if len(recent_points) >= 2:
                trend = self.trend_analyzer.calculate_trend(recent_points)
                anomalies = self.trend_analyzer.detect_anomalies(recent_points)
                
                trend_analysis[metric_name] = {
                    **trend,
                    "anomalies_detected": len(anomalies),
                    "last_anomaly": anomalies[-1].timestamp.isoformat() if anomalies else None
                }
        
        return trend_analysis
    
    async def _get_alerts_summary(self, cluster_id: Optional[str]) -> Dict[str, Any]:
        """Get alerts summary"""
        
        active_alerts = [a for a in self.active_alerts.values() 
                        if not cluster_id or a.cluster_id == cluster_id]
        
        alerts_by_severity = {}
        for severity in AlertSeverity:
            alerts_by_severity[severity.value] = len([a for a in active_alerts 
                                                    if a.severity == severity])
        
        return {
            "active_alerts": len(active_alerts),
            "by_severity": alerts_by_severity,
            "recent_alerts": [self._alert_to_dict(a) for a in active_alerts[-5:]],
            "top_metrics_with_alerts": self._get_top_alert_metrics(active_alerts)
        }
    
    async def _get_performance_insights(self, cluster_id: Optional[str], cutoff_time: datetime) -> Dict[str, Any]:
        """Generate performance insights and recommendations"""
        
        insights = []
        
        # Analyze CPU trends
        cpu_metric = "cpu_usage_percent"
        if cpu_metric in self.metrics_store:
            recent_points = [p for p in self.metrics_store[cpu_metric].data_points 
                           if p.timestamp >= cutoff_time and
                           (not cluster_id or p.labels.get("cluster_id") == cluster_id)]
            if recent_points:
                avg_cpu = statistics.mean([p.value for p in recent_points])
                if avg_cpu > 80:
                    insights.append({
                        "type": "performance",
                        "severity": "warning",
                        "title": "High CPU Usage Detected",
                        "description": f"Average CPU usage is {avg_cpu:.1f}% - consider scaling or optimization",
                        "metric": cpu_metric,
                        "recommendation": "Scale horizontally or optimize workloads"
                    })
        
        # Analyze memory trends
        memory_metric = "memory_usage_percent"
        if memory_metric in self.metrics_store:
            recent_points = [p for p in self.metrics_store[memory_metric].data_points 
                           if p.timestamp >= cutoff_time and
                           (not cluster_id or p.labels.get("cluster_id") == cluster_id)]
            if recent_points:
                trend = self.trend_analyzer.calculate_trend(recent_points)
                if trend["trend"] == "increasing" and trend["confidence"] > 0.7:
                    insights.append({
                        "type": "trend",
                        "severity": "info",
                        "title": "Memory Usage Trending Up",
                        "description": f"Memory usage has been increasing with {trend['confidence']:.1%} confidence",
                        "metric": memory_metric,
                        "recommendation": "Monitor for potential memory leaks"
                    })
        
        return {
            "insights": insights,
            "insights_count": len(insights),
            "performance_score": self._calculate_performance_score(),
            "optimization_opportunities": self._identify_optimization_opportunities()
        }
    
    def _check_alert_threshold(self, metric_name: str, value: float, cluster_id: str, 
                             timestamp: datetime) -> Optional[Alert]:
        """Check if metric value exceeds alert thresholds"""
        
        if metric_name not in self.alert_thresholds:
            return None
        
        thresholds = self.alert_thresholds[metric_name]
        
        severity = None
        threshold = None
        
        if value >= thresholds.get("critical", float('inf')):
            severity = AlertSeverity.CRITICAL
            threshold = thresholds["critical"]
        elif value >= thresholds.get("warning", float('inf')):
            severity = AlertSeverity.WARNING
            threshold = thresholds["warning"]
        
        if severity:
            alert_id = f"{metric_name}_{cluster_id}_{severity.value}_{int(timestamp.timestamp())}"
            
            # Check if similar alert already exists
            existing_alert = next((a for a in self.active_alerts.values() 
                                 if a.metric_name == metric_name and a.cluster_id == cluster_id), None)
            
            if not existing_alert:
                alert = Alert(
                    alert_id=alert_id,
                    severity=severity,
                    title=f"{metric_name.replace('_', ' ').title()} Alert",
                    description=f"{metric_name} is {value} (threshold: {threshold})",
                    metric_name=metric_name,
                    current_value=value,
                    threshold=float(threshold) if threshold is not None else 0.0,
                    cluster_id=cluster_id,
                    created_at=timestamp
                )
                
                self.active_alerts[alert_id] = alert
                return alert
        
        return None
    
    def _get_metric_unit(self, metric_name: str) -> str:
        """Get appropriate unit for metric"""
        units = {
            "cpu_usage_percent": "%",
            "memory_usage_percent": "%", 
            "disk_usage_percent": "%",
            "pod_restart_rate": "restarts/min",
            "node_not_ready_count": "nodes",
            "failed_pod_count": "pods",
            "network_rx_bytes": "bytes/sec",
            "network_tx_bytes": "bytes/sec"
        }
        return units.get(metric_name, "")
    
    def _get_metric_description(self, metric_name: str) -> str:
        """Get description for metric"""
        descriptions = {
            "cpu_usage_percent": "CPU utilization percentage across cluster nodes",
            "memory_usage_percent": "Memory utilization percentage across cluster nodes",
            "disk_usage_percent": "Disk utilization percentage across cluster nodes",
            "pod_restart_rate": "Rate of pod restarts per minute",
            "node_not_ready_count": "Number of nodes in NotReady state",
            "failed_pod_count": "Number of pods in failed state"
        }
        return descriptions.get(metric_name, f"Metric: {metric_name}")
    
    def _alert_to_dict(self, alert: Alert) -> Dict[str, Any]:
        """Convert alert to dictionary"""
        return {
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
    
    def _get_top_alert_metrics(self, alerts: List[Alert]) -> List[str]:
        """Get metrics that generate the most alerts"""
        metric_counts = {}
        for alert in alerts:
            metric_counts[alert.metric_name] = metric_counts.get(alert.metric_name, 0) + 1
        
        return sorted(metric_counts.keys(), key=lambda x: metric_counts.get(x, 0), reverse=True)[:5]
    
    def _calculate_performance_score(self) -> float:
        """Calculate overall cluster performance score (0-100)"""
        # Simplified performance scoring
        score = 100
        
        # Deduct points for active alerts
        for alert in self.active_alerts.values():
            if alert.severity == AlertSeverity.CRITICAL:
                score -= 20
            elif alert.severity == AlertSeverity.WARNING:
                score -= 10
        
        return max(score, 0)
    
    def _identify_optimization_opportunities(self) -> List[Dict[str, Any]]:
        """Identify optimization opportunities"""
        opportunities = []
        
        # Example optimization opportunities based on metrics
        cpu_metric = "cpu_usage_percent"
        if cpu_metric in self.metrics_store:
            recent_points = self.metrics_store[cpu_metric].data_points[-10:]
            if recent_points:
                avg_cpu = statistics.mean([p.value for p in recent_points])
                if avg_cpu < 30:
                    opportunities.append({
                        "type": "rightsizing",
                        "title": "CPU Over-provisioning Detected",
                        "description": f"Average CPU usage is only {avg_cpu:.1f}%",
                        "potential_savings": "20-40% cost reduction",
                        "priority": "medium"
                    })
        
        return opportunities

# Global analytics engine instance
analytics_engine = AdvancedAnalyticsEngine()