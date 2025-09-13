#!/usr/bin/env python3
"""
Simple launcher for the Quick Commerce AI Operations Manager
This version uses CSV data directly without database complexity
"""

import subprocess
import sys
import os

def main():
    """Launch the simple Streamlit app"""
    print("🚀 EQREV Hackathon - Quick Commerce AI Operations Manager")
    print("=" * 60)
    print("Starting Simple Version (CSV-based)...")
    print("📊 This version reads data directly from CSV files")
    print("🌐 App will open at: http://localhost:8502")
    print("=" * 60)
    
    try:
        # Change to the project directory
        os.chdir(os.path.dirname(os.path.abspath(__file__)))
        
        # Run the simple Streamlit app
        cmd = [sys.executable, "-m", "streamlit", "run", "frontend/simple_app.py", "--server.port", "8502"]
        subprocess.run(cmd)
        
    except KeyboardInterrupt:
        print("\n👋 Shutting down...")
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    main()
