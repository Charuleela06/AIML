@echo off
echo 🚀 EQREV Hackathon - Quick Commerce AI Operations Manager
echo ============================================================
echo Starting the application...
echo.
echo 📊 This will open your browser automatically
echo 🌐 App URL: http://localhost:8502
echo.
echo Press Ctrl+C to stop the application
echo ============================================================
echo.

cd /d "%~dp0"
call venv\Scripts\activate
python -m streamlit run frontend/simple_app.py --server.port 8502

pause
