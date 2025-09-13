"""
Hugging Face Spaces Deployment - EQREV Hackathon - Agentic AI for Quick Commerce
This is the main entry point for the Streamlit app on Hugging Face Spaces
"""
import sys
import os

# Add backend to path
sys.path.append('backend')

# Import and run the Streamlit app
from frontend.app import main

if __name__ == "__main__":
    main()
