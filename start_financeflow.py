#!/usr/bin/env python3
"""
FinanceFlow Startup Script
Starts both the FastAPI backend and Streamlit dashboard
"""

import subprocess
import sys
import time
import webbrowser
from threading import Thread
import os

def start_api_server():
    """Start the FastAPI server"""
    print("🚀 Starting FinanceFlow API server...")
    try:
        subprocess.run([
            sys.executable, "-m", "uvicorn", 
            "app.main:app", 
            "--reload", 
            "--host", "0.0.0.0", 
            "--port", "8000"
        ], check=True)
    except KeyboardInterrupt:
        print("\n🛑 API server stopped.")
    except Exception as e:
        print(f"❌ Error starting API server: {e}")

def start_dashboard():
    """Start the Streamlit dashboard"""
    print("📊 Starting FinanceFlow Dashboard...")
    time.sleep(3)  # Wait for API to start
    try:
        subprocess.run([
            sys.executable, "-m", "streamlit", 
            "run", 
            "dashboard.py", 
            "--server.port", "8501",
            "--server.headless", "true"
        ], check=True)
    except KeyboardInterrupt:
        print("\n🛑 Dashboard stopped.")
    except Exception as e:
        print(f"❌ Error starting dashboard: {e}")

def main():
    """Main startup function"""
    print("=" * 60)
    print("🚀 FinanceFlow - Advanced Personal Wealth Management System")
    print("   Built by Nabhi - Full-Stack Financial Technology Developer")
    print("=" * 60)
    
    # Check if required packages are installed
    try:
        import fastapi
        import streamlit
        import requests
        import plotly
        import pandas
    except ImportError as e:
        print(f"❌ Missing required package: {e}")
        print("💡 Please install dependencies: pip install -r requirements.txt")
        return
    
    print("\n🔧 Starting services...")
    print("   API Server: http://localhost:8000")
    print("   Dashboard: http://localhost:8501")
    print("   API Docs: http://localhost:8000/docs")
    
    try:
        # Start API server in a separate thread
        api_thread = Thread(target=start_api_server, daemon=True)
        api_thread.start()
        
        # Wait a moment for API to initialize
        print("\n⏳ Waiting for API to initialize...")
        time.sleep(5)
        
        # Open dashboard in browser
        print("🌐 Opening dashboard in browser...")
        webbrowser.open("http://localhost:8501")
        
        # Start dashboard (this will block)
        start_dashboard()
        
    except KeyboardInterrupt:
        print("\n\n🛑 Shutting down FinanceFlow services...")
        print("   Thank you for using FinanceFlow!")
    except Exception as e:
        print(f"❌ Startup error: {e}")

if __name__ == "__main__":
    main()
