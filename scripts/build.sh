#!/bin/bash

# Build and deployment script for KubeGenie

set -e

VERSION=${1:-latest}
REGISTRY=${REGISTRY:-"kubegenie"}

echo "🏗️  Building KubeGenie v${VERSION}..."

# Build backend
echo "📦 Building backend image..."
docker build -t ${REGISTRY}/backend:${VERSION} ./backend

# Build UI
echo "📦 Building UI image..."
docker build -t ${REGISTRY}/ui:${VERSION} ./ui

echo "✅ Build complete!"

if [ "$2" = "push" ]; then
    echo "🚀 Pushing images to registry..."
    docker push ${REGISTRY}/backend:${VERSION}
    docker push ${REGISTRY}/ui:${VERSION}
    echo "✅ Images pushed to registry"
fi

if [ "$2" = "deploy" ] || [ "$3" = "deploy" ]; then
    echo "🚀 Deploying to Kubernetes..."
    
    # Update image tags in deployment files
    sed -i.bak "s|kubegenie/backend:.*|${REGISTRY}/backend:${VERSION}|g" deployments/backend.yaml
    sed -i.bak "s|kubegenie/ui:.*|${REGISTRY}/ui:${VERSION}|g" deployments/ui.yaml
    
    # Apply deployments
    kubectl apply -f deployments/
    
    echo "✅ Deployment complete!"
    echo "📋 Check status with: kubectl get pods -n kubegenie"
fi