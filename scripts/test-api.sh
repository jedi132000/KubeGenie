#!/bin/bash

# Test KubeGenie API endpoints with authentication

set -e

API_URL="http://localhost:8000"

echo "🧞‍♂️ Testing KubeGenie API with Authentication..."
echo ""

# Test health endpoint
echo "1. Testing health endpoint..."
curl -s "${API_URL}/health" | jq . || echo "Health check failed"
echo ""

# Test login
echo "2. Testing login..."
LOGIN_RESPONSE=$(curl -s -X POST "${API_URL}/api/v1/auth/login" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "admin",
    "password": "admin123"
  }')

echo "$LOGIN_RESPONSE" | jq . || echo "Login failed"

# Extract token
TOKEN=$(echo "$LOGIN_RESPONSE" | jq -r '.access_token // empty')

if [ -z "$TOKEN" ]; then
  echo "❌ Failed to get authentication token"
  exit 1
fi

echo "✅ Got authentication token"
echo ""

# Test authenticated endpoints
echo "3. Testing authenticated chat endpoint..."
curl -s -X POST "${API_URL}/api/v1/chat/message" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "message": "deploy nginx with 3 replicas"
  }' | jq . || echo "Chat endpoint failed"
echo ""

echo "4. Testing Kubernetes endpoints..."
curl -s "${API_URL}/api/v1/k8s/pods" \
  -H "Authorization: Bearer $TOKEN" | jq . || echo "K8s pods endpoint failed"
echo ""

echo "5. Testing Crossplane endpoints..."
curl -s "${API_URL}/api/v1/crossplane/compositions" \
  -H "Authorization: Bearer $TOKEN" | jq . || echo "Crossplane endpoint failed"
echo ""

echo "6. Testing user profile..."
curl -s "${API_URL}/api/v1/auth/me" \
  -H "Authorization: Bearer $TOKEN" | jq . || echo "Profile endpoint failed"
echo ""

echo "✅ All API tests completed!"
echo ""
echo "🚀 You can now:"
echo "  • Start the Gradio UI: cd ui && ./start.sh"
echo "  • Use the CLI: cd cli && python main.py chat 'deploy nginx'"
echo "  • Access API docs: http://localhost:8000/api/docs"