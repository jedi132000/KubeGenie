"""
ChromaDB Vector Database Manager for KubeGenie

Handles document storage, embedding, and retrieval for the knowledge base.
Provides semantic search capabilities for Kubernetes documentation and best practices.
"""

import chromadb
from chromadb.config import Settings
import logging
import json
import uuid
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass
import os
from datetime import datetime
import hashlib

logger = logging.getLogger(__name__)

@dataclass
class Document:
    """Document data structure for vector storage"""
    id: str
    title: str
    content: str
    metadata: Dict[str, Any]
    source: str
    timestamp: datetime
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "title": self.title,
            "content": self.content,
            "metadata": self.metadata,
            "source": self.source,
            "timestamp": self.timestamp.isoformat()
        }

@dataclass
class SearchResult:
    """Search result from vector database"""
    document: Document
    score: float
    distance: float

class ChromaDBManager:
    """ChromaDB vector database manager"""
    
    def __init__(self, persist_directory: str = "./chroma_db", collection_name: str = "kubegenie_knowledge"):
        """Initialize ChromaDB manager
        
        Args:
            persist_directory: Directory to persist the database
            collection_name: Name of the collection to use
        """
        self.persist_directory = persist_directory
        self.collection_name = collection_name
        self.client = None
        self.collection = None
        
        # Ensure directory exists
        os.makedirs(persist_directory, exist_ok=True)
        
    async def initialize(self):
        """Initialize the ChromaDB client and collection"""
        try:
            # Initialize ChromaDB client with persistence
            self.client = chromadb.PersistentClient(
                path=self.persist_directory,
                settings=Settings(
                    anonymized_telemetry=False,
                    allow_reset=True
                )
            )
            
            # Get or create collection
            try:
                self.collection = self.client.get_collection(
                    name=self.collection_name,
                    embedding_function=chromadb.utils.embedding_functions.DefaultEmbeddingFunction()
                )
                logger.info(f"Loaded existing collection '{self.collection_name}'")
            except ValueError:
                # Collection doesn't exist, create it
                self.collection = self.client.create_collection(
                    name=self.collection_name,
                    embedding_function=chromadb.utils.embedding_functions.DefaultEmbeddingFunction(),
                    metadata={"description": "KubeGenie Knowledge Base"}
                )
                logger.info(f"Created new collection '{self.collection_name}'")
                
                # Initialize with sample data
                await self._initialize_sample_data()
            
            logger.info("ChromaDB initialized successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to initialize ChromaDB: {e}")
            return False
    
    async def _initialize_sample_data(self):
        """Initialize the database with sample Kubernetes knowledge"""
        sample_documents = [
            {
                "title": "Kubernetes Pod Networking Troubleshooting",
                "content": "When troubleshooting pod networking issues, check: 1) Pod IP assignment and CIDR ranges, 2) NetworkPolicy configurations, 3) Service endpoints and DNS resolution, 4) CNI plugin status and logs, 5) Firewall rules and security groups. Common solutions include restarting the CNI daemonset, checking node network connectivity, and validating service mesh configurations.",
                "source": "kubernetes_docs",
                "metadata": {
                    "category": "networking",
                    "difficulty": "intermediate",
                    "version": "1.28+",
                    "tags": "pods,networking,troubleshooting,CNI"
                }
            },
            {
                "title": "Pod Scaling Best Practices",
                "content": "Effective pod scaling requires: 1) Proper resource requests and limits, 2) Horizontal Pod Autoscaler (HPA) configuration with appropriate metrics, 3) Vertical Pod Autoscaler (VPA) for right-sizing, 4) Pod Disruption Budgets (PDB) for availability, 5) Node autoscaling coordination. Monitor CPU, memory, and custom metrics. Set conservative scaling policies to avoid thrashing.",
                "source": "kubernetes_best_practices",
                "metadata": {
                    "category": "scaling",
                    "difficulty": "advanced",
                    "version": "1.25+",
                    "tags": "scaling,HPA,VPA,autoscaling,resources"
                }
            },
            {
                "title": "Kubernetes Security Hardening Guide",
                "content": "Security hardening checklist: 1) Enable RBAC and principle of least privilege, 2) Use Pod Security Standards/Policies, 3) Enable audit logging, 4) Secure etcd with TLS, 5) Use NetworkPolicies for microsegmentation, 6) Regular image scanning and updates, 7) Secrets management with external systems, 8) Runtime security monitoring. Implement defense in depth.",
                "source": "security_guide",
                "metadata": {
                    "category": "security",
                    "difficulty": "advanced",
                    "version": "1.24+",
                    "tags": "security,RBAC,policies,hardening,compliance"
                }
            },
            {
                "title": "Resource Management and Optimization",
                "content": "Optimize Kubernetes resources: 1) Set appropriate resource requests/limits, 2) Use quality of service classes (QoS), 3) Implement resource quotas and limit ranges, 4) Monitor resource utilization with metrics, 5) Use node affinity and anti-affinity rules, 6) Implement cluster autoscaling, 7) Regular capacity planning and rightsizing. Balance performance, cost, and reliability.",
                "source": "optimization_guide",
                "metadata": {
                    "category": "optimization",
                    "difficulty": "intermediate",
                    "version": "1.20+",
                    "tags": "resources,optimization,QoS,capacity,cost"
                }
            },
            {
                "title": "Kubernetes Cluster Upgrade Strategies",
                "content": "Safe cluster upgrade approach: 1) Review release notes and breaking changes, 2) Test in non-production environments, 3) Backup etcd and critical data, 4) Use rolling updates for control plane, 5) Upgrade nodes in phases, 6) Monitor application health during upgrades, 7) Have rollback procedures ready, 8) Update CNI and CSI plugins. Plan for downtime and communicate with stakeholders.",
                "source": "upgrade_guide",
                "metadata": {
                    "category": "maintenance",
                    "difficulty": "advanced",
                    "version": "all",
                    "tags": "upgrade,maintenance,rollback,testing,backup"
                }
            },
            {
                "title": "Monitoring and Observability Setup",
                "content": "Comprehensive monitoring stack: 1) Prometheus for metrics collection, 2) Grafana for visualization and dashboards, 3) AlertManager for notifications, 4) Jaeger/Zipkin for distributed tracing, 5) ELK/EFK stack for logging, 6) Service mesh observability (Istio/Linkerd), 7) Custom metrics and SLI/SLO definitions. Implement the four golden signals: latency, traffic, errors, saturation.",
                "source": "monitoring_guide",
                "metadata": {
                    "category": "monitoring",
                    "difficulty": "intermediate",
                    "version": "1.22+",
                    "tags": "monitoring,prometheus,grafana,observability,metrics"
                }
            },
            {
                "title": "Disaster Recovery and Backup Strategies",
                "content": "Kubernetes disaster recovery: 1) Regular etcd backups with encryption, 2) Persistent volume snapshots, 3) Application-level backups, 4) Multi-region cluster strategies, 5) GitOps for configuration recovery, 6) Runbook documentation and testing, 7) RTO/RPO definitions and monitoring, 8) Cross-cloud migration capabilities. Test recovery procedures regularly.",
                "source": "disaster_recovery_guide",
                "metadata": {
                    "category": "disaster_recovery",
                    "difficulty": "advanced",
                    "version": "1.20+",
                    "tags": "backup,disaster_recovery,etcd,volumes,migration"
                }
            }
        ]
        
        documents = []
        for doc_data in sample_documents:
            doc_id = str(uuid.uuid4())
            document = Document(
                id=doc_id,
                title=doc_data["title"],
                content=doc_data["content"],
                source=doc_data["source"],
                metadata=doc_data["metadata"],
                timestamp=datetime.now()
            )
            documents.append(document)
        
        await self.add_documents(documents)
        logger.info(f"Initialized ChromaDB with {len(documents)} sample documents")
    
    async def add_document(self, document: Document) -> bool:
        """Add a single document to the vector database
        
        Args:
            document: Document to add
            
        Returns:
            bool: Success status
        """
        try:
            if not self.collection:
                raise RuntimeError("ChromaDB not initialized")
            
            self.collection.add(
                documents=[document.content],
                metadatas=[{
                    "title": document.title,
                    "source": document.source,
                    "timestamp": document.timestamp.isoformat(),
                    **document.metadata
                }],
                ids=[document.id]
            )
            
            logger.debug(f"Added document: {document.title}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to add document: {e}")
            return False
    
    async def add_documents(self, documents: List[Document]) -> int:
        """Add multiple documents to the vector database
        
        Args:
            documents: List of documents to add
            
        Returns:
            int: Number of documents successfully added
        """
        if not documents:
            return 0
        
        try:
            if not self.collection:
                raise RuntimeError("ChromaDB not initialized")
            
            doc_contents = []
            doc_metadatas = []
            doc_ids = []
            
            for document in documents:
                doc_contents.append(document.content)
                doc_metadatas.append({
                    "title": document.title,
                    "source": document.source,
                    "timestamp": document.timestamp.isoformat(),
                    **document.metadata
                })
                doc_ids.append(document.id)
            
            self.collection.add(
                documents=doc_contents,
                metadatas=doc_metadatas,
                ids=doc_ids
            )
            
            logger.info(f"Added {len(documents)} documents to ChromaDB")
            return len(documents)
            
        except Exception as e:
            logger.error(f"Failed to add documents: {e}")
            return 0
    
    async def search(self, query: str, limit: int = 10, filters: Optional[Dict[str, Any]] = None) -> List[SearchResult]:
        """Search for documents using semantic similarity
        
        Args:
            query: Search query
            limit: Maximum number of results
            filters: Optional metadata filters
            
        Returns:
            List[SearchResult]: Search results
        """
        try:
            if not self.collection:
                raise RuntimeError("ChromaDB not initialized")
            
            # Prepare where clause for filters
            where_clause = {}
            if filters:
                for key, value in filters.items():
                    if isinstance(value, list):
                        # Handle list filters (e.g., tags)
                        where_clause[key] = {"$in": value}
                    else:
                        where_clause[key] = {"$eq": value}
            
            # Perform the search
            results = self.collection.query(
                query_texts=[query],
                n_results=limit,
                where=where_clause if where_clause else None
            )
            
            # Parse results
            search_results = []
            if results["documents"] and len(results["documents"]) > 0:
                documents = results["documents"][0]
                metadatas = results["metadatas"][0]
                distances = results["distances"][0]
                ids = results["ids"][0]
                
                for i, (doc_content, metadata, distance, doc_id) in enumerate(
                    zip(documents, metadatas, distances, ids)
                ):
                    # Create document object
                    document_metadata = {k: v for k, v in metadata.items() 
                                       if k not in ["title", "source", "timestamp"]}
                    
                    document = Document(
                        id=doc_id,
                        title=metadata.get("title", "Untitled"),
                        content=doc_content,
                        source=metadata.get("source", "unknown"),
                        metadata=document_metadata,
                        timestamp=datetime.fromisoformat(metadata.get("timestamp", datetime.now().isoformat()))
                    )
                    
                    # Calculate similarity score (inverse of distance)
                    score = max(0, 1 - distance)
                    
                    search_result = SearchResult(
                        document=document,
                        score=score,
                        distance=distance
                    )
                    
                    search_results.append(search_result)
            
            logger.debug(f"Search for '{query}' returned {len(search_results)} results")
            return search_results
            
        except Exception as e:
            logger.error(f"Search failed: {e}")
            return []
    
    async def delete_document(self, document_id: str) -> bool:
        """Delete a document from the vector database
        
        Args:
            document_id: ID of document to delete
            
        Returns:
            bool: Success status
        """
        try:
            if not self.collection:
                raise RuntimeError("ChromaDB not initialized")
            
            self.collection.delete(ids=[document_id])
            logger.debug(f"Deleted document: {document_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to delete document: {e}")
            return False
    
    async def get_collection_stats(self) -> Dict[str, Any]:
        """Get statistics about the collection
        
        Returns:
            Dict[str, Any]: Collection statistics
        """
        try:
            if not self.collection:
                return {"error": "ChromaDB not initialized"}
            
            count = self.collection.count()
            
            return {
                "collection_name": self.collection_name,
                "document_count": count,
                "persist_directory": self.persist_directory,
                "embedding_function": "DefaultEmbeddingFunction",
                "last_updated": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Failed to get collection stats: {e}")
            return {"error": str(e)}
    
    async def update_document(self, document: Document) -> bool:
        """Update an existing document
        
        Args:
            document: Updated document
            
        Returns:
            bool: Success status
        """
        try:
            # Delete existing document and add updated one
            await self.delete_document(document.id)
            return await self.add_document(document)
            
        except Exception as e:
            logger.error(f"Failed to update document: {e}")
            return False
    
    def close(self):
        """Close the database connection"""
        try:
            if self.client:
                # ChromaDB doesn't have an explicit close method
                # Data is automatically persisted
                logger.info("ChromaDB connection closed")
        except Exception as e:
            logger.error(f"Error closing ChromaDB: {e}")

# Global instance
chroma_manager = ChromaDBManager()

async def initialize_vector_db() -> bool:
    """Initialize the global vector database instance"""
    return await chroma_manager.initialize()

async def search_knowledge_base(query: str, limit: int = 10, filters: Optional[Dict[str, Any]] = None) -> List[SearchResult]:
    """Search the knowledge base"""
    return await chroma_manager.search(query, limit, filters)

async def add_knowledge(document: Document) -> bool:
    """Add knowledge to the database"""
    return await chroma_manager.add_document(document)

async def get_knowledge_stats() -> Dict[str, Any]:
    """Get knowledge base statistics"""
    return await chroma_manager.get_collection_stats()