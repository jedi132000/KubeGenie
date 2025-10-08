"""
ClusterManager for multi-cluster registration, listing, and switching
"""

from typing import Dict, Any, List, Optional
from .agent import KubernetesAgent
import logging

logger = logging.getLogger(__name__)

class ClusterManager:
    def __init__(self):
        self.agents: Dict[str, KubernetesAgent] = {}
        self.active_agent: Optional[str] = None

    def register_cluster(self, name: str, config: Dict[str, Any]):
        agent = KubernetesAgent(name, config)
        agent.initialize()
        self.agents[name] = agent
        logger.info("Registered cluster agent: %s", name)
        if self.active_agent is None:
            self.active_agent = name

    def list_clusters(self) -> List[str]:
        return list(self.agents.keys())

    def switch_cluster(self, name: str):
        if name in self.agents:
            self.active_agent = name
            logger.info("Switched active cluster to: %s", name)
        else:
            logger.warning("Cluster %s not found.", name)

    def get_active_agent(self) -> Optional[KubernetesAgent]:
        if self.active_agent:
            return self.agents[self.active_agent]
        return None
