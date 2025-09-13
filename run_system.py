"""
Simple startup script for EQREV Hackathon - Agentic AI for Quick Commerce
"""
import os
import sys
import subprocess
import time

def run_streamlit():
    """Run the Streamlit frontend"""
    print("🚀 Starting Streamlit Frontend...")
    try:
        # Run standalone version
        subprocess.run([
            sys.executable, "-m", "streamlit", "run", 
            "frontend/standalone_app.py",
            "--server.port=8501",
            "--server.address=0.0.0.0"
        ])
    except KeyboardInterrupt:
        print("\n👋 Shutting down...")
    except Exception as e:
        print(f"❌ Error: {e}")

def run_backend():
    """Run the FastAPI backend"""
    print("🔧 Starting FastAPI Backend...")
    try:
        os.chdir("backend")
        subprocess.run([sys.executable, "main.py"])
    except KeyboardInterrupt:
        print("\n👋 Shutting down...")
    except Exception as e:
        print(f"❌ Error: {e}")

def run_test():
    """Run system test"""
    print("🧪 Running System Test...")
    try:
        subprocess.run([sys.executable, "test_system.py"])
    except Exception as e:
        print(f"❌ Error: {e}")

def main():
    """Main menu"""
    print("🎯 EQREV Hackathon - Agentic AI for Quick Commerce")
    print("=" * 50)
    print("Choose an option:")
    print("1. 🚀 Run Streamlit Frontend (Recommended)")
    print("2. 🔧 Run FastAPI Backend")
    print("3. 🧪 Run System Test")
    print("4. 📊 Run Both Frontend & Backend")
    print("5. ❌ Exit")
    
    while True:
        try:
            choice = input("\nEnter your choice (1-5): ").strip()
            
            if choice == "1":
                run_streamlit()
                break
            elif choice == "2":
                run_backend()
                break
            elif choice == "3":
                run_test()
                break
            elif choice == "4":
                print("🚀 Starting both services...")
                print("Frontend: http://localhost:8501")
                print("Backend: http://localhost:8000")
                print("Press Ctrl+C to stop")
                
                # Start backend in background
                backend_process = subprocess.Popen([
                    sys.executable, "backend/main.py"
                ])
                
                time.sleep(3)  # Wait for backend to start
                
                # Start frontend
                try:
                    subprocess.run([
                        sys.executable, "-m", "streamlit", "run", 
                        "frontend/app.py",
                        "--server.port=8501"
                    ])
                except KeyboardInterrupt:
                    print("\n👋 Shutting down...")
                    backend_process.terminate()
                break
            elif choice == "5":
                print("👋 Goodbye!")
                break
            else:
                print("❌ Invalid choice. Please enter 1-5.")
                
        except KeyboardInterrupt:
            print("\n👋 Goodbye!")
            break
        except Exception as e:
            print(f"❌ Error: {e}")

if __name__ == "__main__":
    main()
