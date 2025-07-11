#!/usr/bin/env python3
"""
Main startup script for Question Paper Generator & Evaluator
Runs both backend and frontend services
"""

import subprocess
import sys
import os
import time
import signal
from pathlib import Path

def signal_handler(sig, frame):
    """Handle Ctrl+C to gracefully shutdown services"""
    print("\n🛑 Shutting down services...")
    sys.exit(0)

def main():
    """Start both backend and frontend services"""
    signal.signal(signal.SIGINT, signal_handler)
    
    print("🚀 Starting Question Paper Generator & Evaluator")
    print("=" * 50)
    
    # Check if we're in the right directory
    if not Path("backend").exists() or not Path("frontend").exists():
        print("❌ Error: Please run this script from the project root directory")
        print("   Make sure 'backend' and 'frontend' folders exist")
        sys.exit(1)
    
    # Start backend
    print("🔧 Starting Backend (FastAPI)...")
    backend_process = subprocess.Popen([
        sys.executable, "backend/start.py"
    ], cwd=os.getcwd())
    
    # Wait a moment for backend to start
    time.sleep(3)
    
    # Start frontend
    print("🎨 Starting Frontend (Streamlit)...")
    frontend_process = subprocess.Popen([
        sys.executable, "frontend/start.py"
    ], cwd=os.getcwd())
    
    print("\n✅ Services started successfully!")
    print("📍 Backend: http://localhost:8000")
    print("📍 Frontend: http://localhost:8501")
    print("📍 API Docs: http://localhost:8000/docs")
    print("\n🛑 Press Ctrl+C to stop all services")
    
    try:
        # Wait for processes to complete
        backend_process.wait()
        frontend_process.wait()
    except KeyboardInterrupt:
        print("\n🛑 Stopping services...")
        backend_process.terminate()
        frontend_process.terminate()
        
        # Wait for graceful shutdown
        try:
            backend_process.wait(timeout=5)
            frontend_process.wait(timeout=5)
        except subprocess.TimeoutExpired:
            backend_process.kill()
            frontend_process.kill()
        
        print("👋 Services stopped")

if __name__ == "__main__":
    main() 