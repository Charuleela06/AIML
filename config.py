"""
Configuration file for EQREV Hackathon - Agentic AI for Quick Commerce
"""
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# OpenAI Configuration
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY', '')

# n8n Webhook Configuration
N8N_WEBHOOK_URL = os.getenv('N8N_WEBHOOK_URL', 'http://localhost:5678/webhook/quick-commerce')

# Database Configuration
DATABASE_URL = os.getenv('DATABASE_URL', 'sqlite:///data/quick_commerce.db')

# API Configuration
API_HOST = os.getenv('API_HOST', '0.0.0.0')
API_PORT = int(os.getenv('API_PORT', 8000))

# Streamlit Configuration
STREAMLIT_SERVER_PORT = int(os.getenv('STREAMLIT_SERVER_PORT', 8501))

# Application Configuration
APP_NAME = "Quick Commerce AI Agent"
APP_VERSION = "1.0.0"
APP_DESCRIPTION = "Agentic AI System for Quick Commerce Operations Management"

# Mock data configuration (for demo purposes)
USE_MOCK_DATA = os.getenv('USE_MOCK_DATA', 'true').lower() == 'true'
