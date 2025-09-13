"""
FastAPI Backend for EQREV Hackathon - Agentic AI for Quick Commerce
"""
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Dict, Any, Optional
import uvicorn
import os
from datetime import datetime

from ai_agent import QuickCommerceAgent
from models import DatabaseManager

app = FastAPI(title="Quick Commerce AI Agent", version="1.0.0")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global agent instance
agent = None

@app.on_event("startup")
async def startup_event():
    """Initialize the AI agent on startup"""
    global agent
    agent = QuickCommerceAgent()
    print("AI Agent initialized successfully")

@app.on_event("shutdown")
async def shutdown_event():
    """Clean up on shutdown"""
    global agent
    if agent:
        agent.close()

class QueryRequest(BaseModel):
    query: str
    user_id: Optional[str] = None

class QueryResponse(BaseModel):
    response: str
    timestamp: str
    query: str

class InsightsResponse(BaseModel):
    insights: Dict[str, Any]
    timestamp: str

class AllocationRequest(BaseModel):
    product: str
    total_units: int
    strategy: str = "demand_based"

class RestockRequest(BaseModel):
    city: str
    product: str
    quantity: int

class AlertRequest(BaseModel):
    message: str
    priority: str = "medium"
    recipients: list = ["operations@company.com"]

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Quick Commerce AI Agent API",
        "version": "1.0.0",
        "status": "running",
        "endpoints": {
            "query": "/query - Send natural language queries to the AI agent",
            "insights": "/insights - Get current business insights",
            "allocate": "/allocate - Allocate inventory to cities",
            "restock": "/restock - Trigger restock orders",
            "alert": "/alert - Send alert notifications",
            "health": "/health - Health check"
        }
    }

@app.post("/query", response_model=QueryResponse)
async def process_query(request: QueryRequest):
    """Process natural language queries using the AI agent"""
    try:
        if not agent:
            raise HTTPException(status_code=500, detail="AI Agent not initialized")
        
        response = agent.process_query(request.query)
        
        return QueryResponse(
            response=response,
            timestamp=datetime.now().isoformat(),
            query=request.query
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing query: {str(e)}")

@app.get("/insights", response_model=InsightsResponse)
async def get_insights():
    """Get current business insights"""
    try:
        if not agent:
            raise HTTPException(status_code=500, detail="AI Agent not initialized")
        
        insights = agent.get_insights()
        
        return InsightsResponse(
            insights=insights,
            timestamp=datetime.now().isoformat()
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting insights: {str(e)}")

@app.post("/allocate")
async def allocate_inventory(request: AllocationRequest):
    """Allocate inventory to cities"""
    try:
        if not agent:
            raise HTTPException(status_code=500, detail="AI Agent not initialized")
        
        allocation_input = {
            "product": request.product,
            "total_units": request.total_units,
            "strategy": request.strategy
        }
        
        result = agent._allocate_inventory(str(allocation_input).replace("'", '"'))
        
        return {
            "message": "Allocation completed",
            "result": result,
            "timestamp": datetime.now().isoformat()
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error allocating inventory: {str(e)}")

@app.post("/restock")
async def trigger_restock(request: RestockRequest):
    """Trigger restock order"""
    try:
        if not agent:
            raise HTTPException(status_code=500, detail="AI Agent not initialized")
        
        restock_input = {
            "city": request.city,
            "product": request.product,
            "quantity": request.quantity
        }
        
        result = agent._trigger_restock(str(restock_input).replace("'", '"'))
        
        return {
            "message": "Restock order triggered",
            "result": result,
            "timestamp": datetime.now().isoformat()
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error triggering restock: {str(e)}")

@app.post("/alert")
async def send_alert(request: AlertRequest):
    """Send alert notification"""
    try:
        if not agent:
            raise HTTPException(status_code=500, detail="AI Agent not initialized")
        
        alert_input = {
            "message": request.message,
            "priority": request.priority,
            "recipients": request.recipients
        }
        
        result = agent._send_alert(str(alert_input).replace("'", '"'))
        
        return {
            "message": "Alert sent",
            "result": result,
            "timestamp": datetime.now().isoformat()
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error sending alert: {str(e)}")

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "agent_initialized": agent is not None
    }

@app.get("/data/sales")
async def get_sales_data():
    """Get sales data"""
    try:
        if not agent:
            raise HTTPException(status_code=500, detail="AI Agent not initialized")
        
        sales_data = agent.db.get_sales_analytics(7)
        return sales_data.to_dict('records')
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting sales data: {str(e)}")

@app.get("/data/inventory")
async def get_inventory_data():
    """Get inventory data"""
    try:
        if not agent:
            raise HTTPException(status_code=500, detail="AI Agent not initialized")
        
        inventory_data = agent.db.get_inventory_status()
        return inventory_data.to_dict('records')
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting inventory data: {str(e)}")

@app.get("/data/cities")
async def get_city_performance():
    """Get city performance data"""
    try:
        if not agent:
            raise HTTPException(status_code=500, detail="AI Agent not initialized")
        
        city_data = agent.db.get_city_performance(7)
        return city_data.to_dict('records')
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting city data: {str(e)}")

if __name__ == "__main__":
    # Load environment variables
    from dotenv import load_dotenv
    load_dotenv()
    
    # Run the server
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
