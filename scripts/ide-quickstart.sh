#!/bin/bash

# Quick start script for local IDE development
# This script helps you get started with KubeGenie development quickly

set -e

echo "🧞‍♂️ KubeGenie - Local IDE Quick Start"
echo "======================================"
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Check if running in VS Code
if [ -n "$VSCODE_PID" ] || [ -n "$TERM_PROGRAM" ]; then
    echo -e "${GREEN}✓${NC} Detected IDE environment"
else
    echo -e "${YELLOW}⚠${NC} Not detected in IDE - consider opening with VS Code"
fi

# Check prerequisites
echo ""
echo "Checking prerequisites..."

command -v python3 >/dev/null 2>&1 || { 
    echo -e "${RED}✗${NC} Python 3 is required but not installed." 
    echo "   Install from: https://www.python.org/downloads/"
    exit 1
}
echo -e "${GREEN}✓${NC} Python 3: $(python3 --version)"

command -v docker >/dev/null 2>&1 && echo -e "${GREEN}✓${NC} Docker: $(docker --version)" || echo -e "${YELLOW}⚠${NC} Docker not found (optional but recommended)"

command -v kubectl >/dev/null 2>&1 && echo -e "${GREEN}✓${NC} kubectl: $(kubectl version --client --short 2>/dev/null || echo 'installed')" || echo -e "${YELLOW}⚠${NC} kubectl not found (optional)"

# Check if venv exists
if [ ! -d "venv" ]; then
    echo ""
    echo "Creating Python virtual environment..."
    python3 -m venv venv
    echo -e "${GREEN}✓${NC} Virtual environment created"
else
    echo -e "${GREEN}✓${NC} Virtual environment already exists"
fi

# Activate virtual environment
echo ""
echo "Activating virtual environment..."
source venv/bin/activate
echo -e "${GREEN}✓${NC} Virtual environment activated"

# Check and create .env file
if [ ! -f ".env" ]; then
    echo ""
    echo "Creating .env file from template..."
    cp .env.example .env
    echo -e "${GREEN}✓${NC} .env file created"
    echo -e "${YELLOW}⚠${NC} Please edit .env and add your OPENAI_API_KEY"
else
    echo -e "${GREEN}✓${NC} .env file already exists"
    
    # Check if OpenAI key is configured
    if grep -q "sk-proj-your-openai-api-key-here" .env || ! grep -q "OPENAI_API_KEY=sk-" .env; then
        echo -e "${YELLOW}⚠${NC} OpenAI API key not configured in .env"
        echo "   Please add your key: OPENAI_API_KEY=sk-proj-..."
    fi
fi

# Install dependencies
echo ""
echo "Installing dependencies..."

echo "  → Backend dependencies..."
pip install --quiet --upgrade pip
pip install --quiet -r backend/requirements.txt
echo -e "${GREEN}✓${NC} Backend dependencies installed"

echo "  → UI dependencies..."
pip install --quiet -r ui/requirements.txt
echo -e "${GREEN}✓${NC} UI dependencies installed"

if [ -f "cli/requirements.txt" ]; then
    echo "  → CLI dependencies..."
    pip install --quiet -r cli/requirements.txt
    echo -e "${GREEN}✓${NC} CLI dependencies installed"
fi

# Check if running in VS Code
echo ""
if command -v code >/dev/null 2>&1; then
    echo -e "${BLUE}💡 Tip:${NC} Open this project in VS Code for the best experience:"
    echo "   code KubeGenie.code-workspace"
    echo ""
    echo "   Or if already in VS Code, install recommended extensions when prompted"
fi

# Summary
echo ""
echo "======================================"
echo -e "${GREEN}✓${NC} Setup complete! You're ready to develop."
echo "======================================"
echo ""
echo "📋 Next steps:"
echo ""
echo "1. Configure your environment:"
echo "   ${BLUE}Edit .env and add your OPENAI_API_KEY${NC}"
echo ""
echo "2. Start development (choose one):"
echo ""
echo "   Option A - VS Code Debug (Recommended):"
echo "   • Press F5 in VS Code"
echo "   • Select 'Full Stack: Backend + UI'"
echo ""
echo "   Option B - VS Code Tasks:"
echo "   • Press Ctrl+Shift+B"
echo "   • Or Ctrl+Shift+P → Tasks: Run Task → Full Stack: Start All Services"
echo ""
echo "   Option C - Terminal:"
echo "   • Terminal 1: ${BLUE}cd backend && python main.py${NC}"
echo "   • Terminal 2: ${BLUE}cd ui && python simple_main.py${NC}"
echo ""
echo "3. Access the application:"
echo "   • Backend API: ${BLUE}http://localhost:8000${NC}"
echo "   • API Docs: ${BLUE}http://localhost:8000/api/docs${NC}"
echo "   • Gradio UI: ${BLUE}http://localhost:7875${NC}"
echo ""
echo "📚 Documentation:"
echo "   • Local IDE Setup: ${BLUE}docs/LOCAL_IDE_SETUP.md${NC}"
echo "   • Contributing: ${BLUE}docs/CONTRIBUTING.md${NC}"
echo "   • README: ${BLUE}README.md${NC}"
echo ""
echo "🐛 Debugging:"
echo "   • Use VS Code debug configurations (F5)"
echo "   • Set breakpoints in Python files"
echo "   • Check logs in integrated terminal"
echo ""
echo "🔧 Useful VS Code Tasks (Ctrl+Shift+P → Tasks: Run Task):"
echo "   • Setup: Install All Dependencies"
echo "   • Full Stack: Start All Services"
echo "   • Tests: Run All Backend Tests"
echo "   • Lint: Run Black (Format)"
echo "   • Docker: Start Services"
echo ""
echo "Happy coding! 🚀"
echo ""
