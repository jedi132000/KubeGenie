"""
KubeGenie - AI Kubernetes Assistant
Main application entry point

Step 1: Basic project structure with LangChain + Gradio
"""

import os
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    print("⚠️  python-dotenv not installed. Run: pip install -r requirements.txt")

def main():
    """Main application entry point"""
    print("🤖 KubeGenie - AI Kubernetes Assistant")
    print("📦 Step 2: Basic Gradio interface ready!")
    print("🔧 Tech Stack: LangChain + LangGraph + LangSmith + Gradio")
    
    # Check if OpenAI API key is set
    if not os.getenv("OPENAI_API_KEY"):
        print("⚠️  Note: OPENAI_API_KEY not set (will be needed for Step 4)")
        print("   Create a .env file with: OPENAI_API_KEY=your_key_here")
    else:
        print("✅ OpenAI API key configured")
    
    print("\n🚀 Launching Step 2: Basic Gradio chat interface")
    print("🌐 Opening at: http://localhost:7860")
    
    # Import and launch chat interface
    try:
        from src.ui.chat_interface import main as launch_chat
        launch_chat()
    except ImportError as e:
        print(f"❌ Error importing chat interface: {e}")
        print("💡 Try running: pip install -r requirements.txt")
        print("💡 Or use: ./run_step2.sh")

if __name__ == "__main__":
    main()