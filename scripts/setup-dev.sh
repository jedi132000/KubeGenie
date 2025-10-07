#!/bin/bash

# Development setup script for KubeGenie

set -e

echo "🚀 Setting up KubeGenie development environment..."

# Check prerequisites
command -v python3 >/dev/null 2>&1 || { echo "❌ Python 3 is required but not installed. Aborting." >&2; exit 1; }
command -v node >/dev/null 2>&1 || { echo "❌ Node.js is required but not installed. Aborting." >&2; exit 1; }
command -v docker >/dev/null 2>&1 || { echo "❌ Docker is required but not installed. Aborting." >&2; exit 1; }

echo "✅ Prerequisites check passed"

# Setup backend
echo "📦 Setting up backend..."
cd backend

if [ ! -d "venv" ]; then
    echo "Creating Python virtual environment..."
    python3 -m venv venv
fi

echo "Activating virtual environment..."
source venv/bin/activate

echo "Installing Python dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

echo "✅ Backend setup complete"

cd ..

# Setup UI
echo "📦 Setting up Gradio UI..."
cd ui

echo "Installing UI dependencies..."
pip install -r requirements.txt

echo "✅ UI setup complete"

cd ..

# Setup CLI
echo "📦 Setting up CLI..."
cd cli

echo "Installing CLI dependencies..."
pip install -r requirements.txt

echo "✅ CLI setup complete"

cd ..

# Create environment file if it doesn't exist
if [ ! -f ".env" ]; then
    echo "📝 Creating environment file..."
    cp .env.example .env
    echo "⚠️  Please update .env file with your configuration"
fi

echo "🎉 Development environment setup complete!"
echo ""
echo "📋 Next steps:"
echo "1. Update .env file with your configuration"
echo "2. Run 'docker-compose up -d' to start services"
echo "3. Run backend: cd backend && source venv/bin/activate && python main.py"
echo "4. Run UI: cd ui && ./start.sh"
echo "5. Test CLI: cd cli && python main.py --help"
echo "6. Access Gradio UI at: http://localhost:7860"