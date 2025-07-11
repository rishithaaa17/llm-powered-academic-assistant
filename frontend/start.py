#!/usr/bin/env python3
"""
Startup script for the Question Paper Generator & Evaluator Frontend
"""

import subprocess
import sys
import os
from pathlib import Path

def main():
    """Start the Streamlit frontend"""
    frontend_dir = Path(__file__).parent
    
    print("🚀 Starting Question Paper Generator & Evaluator Frontend")
    print("📍 Frontend: http://localhost:8501")
    print("🔧 Make sure the backend is running on http://localhost:8000")
    
    # Change to frontend directory
    os.chdir(frontend_dir)
    
    # Start Streamlit
    try:
        subprocess.run([
            sys.executable, "-m", "streamlit", "run", "main.py",
            "--server.port", "8501",
            "--server.address", "localhost"
        ], check=True)
    except KeyboardInterrupt:
        print("\n👋 Frontend stopped by user")
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to start frontend: {e}")

if __name__ == "__main__":
    main() 