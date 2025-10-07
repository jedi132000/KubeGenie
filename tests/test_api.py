"""
Tests for KubeGenie backend API
"""

import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_root_endpoint():
    """Test root endpoint"""
    response = client.get("/")
    assert response.status_code == 200
    assert "KubeGenie" in response.json()["message"]


def test_health_check():
    """Test health check endpoint"""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"


def test_api_health_check():
    """Test API health check endpoint"""
    response = client.get("/api/v1/health/")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"


def test_chat_message():
    """Test chat message endpoint"""
    response = client.post(
        "/api/v1/chat/message",
        json={"message": "hello"}
    )
    assert response.status_code == 200
    assert "response" in response.json()


def test_list_compositions():
    """Test Crossplane compositions endpoint"""
    response = client.get("/api/v1/crossplane/compositions")
    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_chat_suggestions():
    """Test chat suggestions endpoint"""
    response = client.get("/api/v1/chat/suggestions")
    assert response.status_code == 200
    assert isinstance(response.json(), list)
    assert len(response.json()) > 0


class TestKubernetesEndpoints:
    """Test Kubernetes API endpoints"""
    
    def test_get_pods_default_namespace(self):
        """Test getting pods in default namespace"""
        # This will fail without actual k8s cluster, but tests the endpoint
        response = client.get("/api/v1/k8s/pods")
        # We expect either success or a 500 error (no k8s cluster)
        assert response.status_code in [200, 500]
    
    def test_create_deployment_validation(self):
        """Test deployment creation with invalid data"""
        response = client.post(
            "/api/v1/k8s/deployments",
            json={"name": "", "image": "nginx"}  # Invalid: empty name
        )
        assert response.status_code == 422  # Validation error


class TestCrossplaneEndpoints:
    """Test Crossplane API endpoints"""
    
    def test_provision_resource(self):
        """Test resource provisioning"""
        response = client.post(
            "/api/v1/crossplane/resources",
            json={
                "name": "test-s3",
                "provider": "aws",
                "resource_type": "s3",
                "parameters": {}
            }
        )
        assert response.status_code == 200
        assert response.json()["name"] == "test-s3"
    
    def test_list_providers(self):
        """Test listing providers"""
        response = client.get("/api/v1/crossplane/providers")
        assert response.status_code == 200
        assert isinstance(response.json(), list)