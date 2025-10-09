#!/bin/bash

# KubeGenie Step 2 - Launch Chat Interface
# Starts the Gradio chat interface for testing

echo "🚀 KubeGenie - Step 2: Basic Gradio Interface"
echo "=============================================="

# Check if virtual environment exists
if [ ! -d ".venv" ]; then
    echo "📦 Creating virtual environment..."
    python -m venv .venv
fi

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source .venv/bin/activate

# Install requirements
echo "📥 Installing dependencies..."
pip install -r requirements.txt

# Launch the chat interface
echo ""
echo "🤖 Starting KubeGenie Chat Interface..."
echo "🌐 Opening at: http://localhost:7860"
echo ""
echo "💡 Try these commands:"
echo "   - 'Hello!' or 'Hi there'"
echo "   - 'What can you do?'"
echo "   - 'Show me your status'"
echo "   - 'Tell me about Crossplane'"
echo ""

# Run the chat interface
python src/ui/chat_interface.py