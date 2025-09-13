# 🚀 EQREV Hackathon: Agentic AI for Quick Commerce

An intelligent AI system that acts as a virtual operations manager for quick commerce companies, providing autonomous decision-making, inventory allocation, and operational automation.

## 🎯 Problem Statement

Quick commerce companies deliver goods to consumers within minutes. This system addresses the need for:
- Wise inventory allocation across cities
- Demand prediction and analysis
- Timely stock fulfillment and restocking
- Automated operational tasks (supplier emails, alerts)

## 🤖 Agent Capabilities

### 1. Decision-Making
- **Natural Language Queries**: Understands complex operational questions
- **Data Analysis**: Queries structured data from databases
- **Actionable Insights**: Provides specific recommendations with reasoning
- **Autonomous Actions**: Makes decisions without human intervention

### 2. Action Execution
- **n8n Integration**: Triggers automated workflows via webhooks
- **Email Automation**: Sends supplier notifications and alerts
- **Database Updates**: Updates stock allocation and inventory data
- **Real-time Monitoring**: Tracks action status and outcomes

### 3. Insight Generation
- **Visualizations**: Interactive charts and dashboards
- **Trend Analysis**: Identifies patterns and growth opportunities
- **Performance Metrics**: City-wise and product-wise analytics
- **Predictive Analytics**: Forecasts demand and stock requirements

## 🏗️ Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Streamlit     │    │   FastAPI       │    │   SQLite DB     │
│   Frontend      │◄──►│   Backend       │◄──►│   Data Layer    │
│                 │    │                 │    │                 │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                                │
                                ▼
                       ┌─────────────────┐
                       │   n8n Workflows │
                       │   Automation    │
                       │                 │
                       └─────────────────┘
                                │
                                ▼
                       ┌─────────────────┐
                       │   External      │
                       │   Systems       │
                       │   (Email, APIs) │
                       └─────────────────┘
```

## 🛠️ Tech Stack

- **Backend**: Python + FastAPI + LangChain
- **Frontend**: Streamlit + Plotly
- **Database**: SQLite (with SQLAlchemy ORM)
- **AI/ML**: OpenAI GPT-3.5-turbo + Pandas + Scikit-learn
- **Automation**: n8n workflows
- **Deployment**: Hugging Face Spaces (recommended)

## 📋 Prerequisites

- Python 3.8+
- OpenAI API Key (optional - system works with mock responses)
- n8n instance (optional - for automation workflows)

## 🚀 Quick Start

### 1. Clone and Setup

```bash
git clone <repository-url>
cd AIML
```

### 2. Create Virtual Environment

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Generate Sample Data

```bash
python backend/data_generator.py
python backend/models.py
```

### 5. Start the Backend Server

```bash
cd backend
python main.py
```

### 6. Start the Frontend (in a new terminal)

```bash
cd frontend
streamlit run app.py
```

## 🔧 Configuration

### Environment Variables

Create a `.env` file in the root directory:

```env
# OpenAI API Key (optional)
OPENAI_API_KEY=your_openai_api_key_here

# n8n Webhook URL (optional)
N8N_WEBHOOK_URL=http://localhost:5678/webhook/quick-commerce

# Database Configuration
DATABASE_URL=sqlite:///data/quick_commerce.db
```

### n8n Setup (Optional)

1. Install n8n: `npm install -g n8n`
2. Start n8n: `n8n start`
3. Import workflows from `workflows/n8n_workflows.json`

## 📊 Sample Data

The system includes realistic sample data:
- **Sales Data**: 30 days of sales across 8 cities and 15 products
- **Inventory Data**: Current stock levels, reorder points, supplier info
- **Performance Metrics**: City-wise and product-wise analytics

## 🎮 Usage Examples

### Natural Language Queries

```
"Allocate 1000 units of Smartphone"
"Which cities are underperforming this week?"
"What items need urgent restocking?"
"Show me sales trends for Mumbai"
```

### API Endpoints

```bash
# Query the AI agent
curl -X POST "http://localhost:8000/query" \
  -H "Content-Type: application/json" \
  -d '{"query": "Allocate 500 units of Laptop"}'

# Get business insights
curl "http://localhost:8000/insights"

# Trigger restock order
curl -X POST "http://localhost:8000/restock" \
  -H "Content-Type: application/json" \
  -d '{"city": "Mumbai", "product": "Smartphone", "quantity": 100}'
```

## 🎯 Key Features

### 1. Intelligent Inventory Allocation
- Analyzes 7-day sales patterns
- Considers city performance metrics
- Provides optimal distribution recommendations
- Triggers automated warehouse notifications

### 2. Proactive Stock Management
- Monitors stock levels in real-time
- Identifies low-stock items automatically
- Triggers supplier restock orders
- Sends priority alerts for critical items

### 3. Performance Analytics
- City-wise performance tracking
- Product demand analysis
- Revenue and unit sales metrics
- Interactive visualizations

### 4. Automated Operations
- Email notifications to warehouse teams
- Supplier order automation
- Alert system for critical issues
- Action logging and tracking

## 📈 Evaluation Criteria Alignment

| Criteria | Weight | Implementation |
|----------|--------|----------------|
| **Core Functionality** | 30% | ✅ Data analysis, insights with reasoning |
| **Agentic Behavior** | 25% | ✅ Autonomous decisions and actions |
| **Data Handling** | 20% | ✅ Efficient queries, forecasting, allocation |
| **User Experience** | 15% | ✅ Interactive Streamlit UI |
| **Innovation** | 10% | ✅ n8n automation, multi-agent potential |

## 🚀 Deployment

### Hugging Face Spaces (Recommended)

1. Create a new Space on Hugging Face
2. Upload all files
3. Create `requirements.txt` with dependencies
4. Set environment variables in Space settings
5. Deploy!

### Local Development

```bash
# Terminal 1: Backend
cd backend && python main.py

# Terminal 2: Frontend
cd frontend && streamlit run app.py

# Access: http://localhost:8501
```

## 📱 Demo Scenarios

### Scenario 1: Inventory Allocation
```
User: "Allocate 1000 units of Product Y"
Agent: 
- Analyzes 7-day sales → City A (40%), City B (35%), City C (25%)
- Suggests: "Distribute: 400 units to City A, 350 to B, 250 to C"
- Sends email to warehouse team automatically
```

### Scenario 2: Urgent Restocking
```
User: "Which products need urgent restocking?"
Agent:
- Finds City D stock < 20% of 3-day average sales
- Responds: "City D is at risk. Raising purchase order of 500 units"
- Sends automated email alert to supplier
```

## 🔮 Future Enhancements

- **Multi-Agent System**: Specialized agents for different operations
- **Real-time Data**: Integration with live inventory systems
- **Advanced Forecasting**: Machine learning models for demand prediction
- **Mobile App**: React Native mobile interface
- **Voice Interface**: Voice-activated operations management

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📄 License

This project is created for the EQREV Hackathon and is open source.

## 🏆 Hackathon Submission

- **Live Demo**: [Hugging Face Space URL]
- **GitHub Repository**: [Repository URL]
- **Presentation**: [Presentation Link]
- **Video Demo**: [Demo Video URL]

---

**Built with ❤️ for EQREV Hackathon 2024**
