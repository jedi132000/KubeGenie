#!/usr/bin/env python3
"""
KubeGenie Agent Interface Launcher
Loads environment and launches the agent-powered chat interface

Step 4: Complete agent integration with proper environment loading
"""

import os
import sys
from pathlib import Path

# Add src to Python path
project_root = Path(__file__).parent
src_path = project_root / "src"
sys.path.insert(0, str(src_path))

# Load environment variables
try:
    from dotenv import load_dotenv
    env_file = project_root / ".env"
    if env_file.exists():
        load_dotenv(env_file)
        print(f"✅ Environment loaded from {env_file}")
    else:
        print(f"⚠️ No .env file found at {env_file}")
except ImportError:
    print("⚠️ python-dotenv not available - install with: pip install python-dotenv")

def check_environment():
    """Check if all required environment variables are set"""
    print("\n🔍 Environment Check:")
    
    # Check OpenAI API key
    api_key = os.getenv("OPENAI_API_KEY")
    if api_key:
        print(f"✅ OPENAI_API_KEY: Set (length: {len(api_key)})")
        if api_key.startswith("sk-"):
            print("✅ API key format looks correct")
        else:
            print("⚠️ API key format might be incorrect")
    else:
        print("❌ OPENAI_API_KEY: Not set")
        print("💡 Add it to your .env file: OPENAI_API_KEY=your-key-here")
    
    # Check other variables
    other_vars = ["LANGSMITH_API_KEY", "LANGSMITH_PROJECT"]
    for var in other_vars:
        value = os.getenv(var)
        if value:
            print(f"✅ {var}: Set")
        else:
            print(f"⚠️ {var}: Optional (not set)")
    
    return bool(api_key)

def test_components():
    """Test that all components are working"""
    print("\n🧪 Component Tests:")
    
    # Test imports
    try:
        from agents.base_agent import KubeGenieAgent
        print("✅ KubeGenieAgent: Import successful")
    except ImportError as e:
        print(f"❌ KubeGenieAgent: Import failed - {e}")
        return False
    
    try:
        from ui.agent_chat_interface import KubeGenieAgentChat
        print("✅ KubeGenieAgentChat: Import successful")
    except ImportError as e:
        print(f"❌ KubeGenieAgentChat: Import failed - {e}")
        return False
    
    # Test agent creation
    try:
        agent = KubeGenieAgent()
        status = agent.get_connection_status()
        print(f"✅ Agent: Initialized successfully")
        print(f"📊 Status: {status}")
    except Exception as e:
        print(f"⚠️ Agent: Initialization issues - {e}")
    
    return True

def launch_interface():
    """Launch the agent interface"""
    print("\n🚀 Launching KubeGenie Agent Interface...")
    
    try:
        from ui.agent_chat_interface import KubeGenieAgentChat
        
        # Create and launch interface
        chat = KubeGenieAgentChat()
        interface = chat.create_interface()
        
        # Launch configuration
        interface.launch(
            server_name="0.0.0.0",
            server_port=7866,  # Changed port to avoid conflicts
            share=False,
            debug=True,
            show_error=True,
            inbrowser=True
        )
        
    except Exception as e:
        print(f"❌ Failed to launch interface: {e}")
        return False
    
    return True

def main():
    """Main launcher function"""
    print("🤖 KubeGenie Agent Interface Launcher")
    print("=" * 50)
    
    # Check environment
    env_ok = check_environment()
    
    # Test components
    components_ok = test_components()
    
    if not components_ok:
        print("\n❌ Component tests failed. Please fix issues before launching.")
        return 1
    
    if not env_ok:
        print("\n⚠️ Environment issues detected.")
        response = input("Continue anyway? (y/N): ").lower().strip()
        if response != 'y':
            print("Exiting...")
            return 1
    
    # Launch interface
    print("\n" + "=" * 50)
    success = launch_interface()
    
    if success:
        print("✅ Interface launched successfully!")
        return 0
    else:
        print("❌ Failed to launch interface")
        return 1

if __name__ == "__main__":
    exit(main())