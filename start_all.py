import subprocess
import time
import threading
import webbrowser

def start_api():
    """Start FastAPI server"""
    print("🚀 Starting API server...")
    subprocess.run([
        "python", "-m", "uvicorn", 
        "app.main:app", "--reload", 
        "--host", "127.0.0.1", "--port", "8000"
    ])

def start_dashboard():
    """Start Streamlit dashboard"""
    print("📊 Starting dashboard...")
    time.sleep(5)  # Wait for API
    subprocess.run([
        "streamlit", "run", "dashboard.py", 
        "--server.port", "8501"
    ])

if __name__ == "__main__":
    print("=" * 50)
    print("  FinanceFlow - Starting All Services")
    print("  Built by Nabhi")
    print("=" * 50)
    
    # Start API in background thread
    api_thread = threading.Thread(target=start_api, daemon=True)
    api_thread.start()
    
    # Wait a bit then open browser
    time.sleep(8)
    print("🌐 Opening browser...")
    webbrowser.open("http://localhost:8501")
    
    # Start dashboard (this will block)
    start_dashboard()
