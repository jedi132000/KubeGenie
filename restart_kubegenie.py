#!/usr/bin/env python3
"""
Quick restart script for KubeGenie with fixed Gradio format
"""

import os
import sys
import subprocess

# Kill any existing KubeGenie processes
print("🔄 Restarting KubeGenie with fixed Gradio format...")

# Change to kubegenie directory
os.chdir('/Users/oladimejioladipo/kubegenie')

# Activate virtual environment and restart
try:
    # Run the main script
    subprocess.run([
        'bash', '-c', 
        'source .venv/bin/activate && python main.py'
    ])
except KeyboardInterrupt:
    print("\n👋 KubeGenie stopped by user")
except Exception as e:
    print(f"❌ Error: {e}")
    print("💡 Try running: source .venv/bin/activate && python main.py")