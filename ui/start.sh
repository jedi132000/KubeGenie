#!/bin/bash

# KubeGenie Gradio UI startup script

set -e

echo "🧞‍♂️ Starting KubeGenie with Gradio UI..."

# Check prerequisites
command -v python3 >/dev/null 2>&1 || { echo "❌ Python 3 is required but not installed. Aborting." >&2; exit 1; }

# Default configuration
API_URL=${KUBEGENIE_API_URL:-"http://localhost:8000"}
UI_PORT=${KUBEGENIE_UI_PORT:-7860}
UI_HOST=${KUBEGENIE_UI_HOST:-"0.0.0.0"}

echo "📦 Setting up environment..."

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "Creating Python virtual environment..."
    python3 -m venv venv
fi

echo "Activating virtual environment..."
source venv/bin/activate

# Install dependencies
echo "Installing dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

# Set environment variables
export KUBEGENIE_API_URL=$API_URL

echo "🚀 Starting KubeGenie Gradio UI..."
echo "   • UI will be available at: http://localhost:$UI_PORT"
echo "   • Connecting to API at: $API_URL"
echo "   • Press Ctrl+C to stop"
echo ""

# Start the Gradio app
python gradio_app.py