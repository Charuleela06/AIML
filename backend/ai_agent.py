"""
AI Agent for EQREV Hackathon - Agentic AI for Quick Commerce
Uses LangChain to make intelligent decisions about inventory allocation and operations
"""
import os
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
import pandas as pd
import json
import requests

from langchain_openai import ChatOpenAI
from langchain.schema import HumanMessage, SystemMessage
from langchain.tools import Tool
from langchain.agents import AgentExecutor, create_react_agent
from langchain.prompts import PromptTemplate

from models import DatabaseManager

class QuickCommerceAgent:
    def __init__(self, openai_api_key: Optional[str] = None):
        self.db = DatabaseManager()
        
        # Initialize OpenAI model
        api_key = openai_api_key or os.getenv('OPENAI_API_KEY')
        if not api_key:
            # Use a mock model for demo purposes
            self.llm = None
            print("Warning: No OpenAI API key found. Using mock responses.")
        else:
            self.llm = ChatOpenAI(
                model="gpt-3.5-turbo",
                temperature=0.1,
                api_key=api_key
            )
        
        self.n8n_webhook_url = os.getenv('N8N_WEBHOOK_URL', 'http://localhost:5678/webhook/quick-commerce')
        
        # Define tools for the agent
        self.tools = self._create_tools()
        
        if self.llm:
            # Create agent with tools
            prompt = self._create_prompt_template()
            agent = create_react_agent(self.llm, self.tools, prompt)
            self.agent_executor = AgentExecutor(agent=agent, tools=self.tools, verbose=True)
        else:
            self.agent_executor = None
    
    def _create_tools(self) -> List[Tool]:
        """Create tools for the agent"""
        tools = [
            Tool(
                name="get_sales_analytics",
                description="Get sales analytics for the last N days. Input: number of days (e.g., '7')",
                func=self._get_sales_analytics
            ),
            Tool(
                name="get_inventory_status",
                description="Get current inventory status across all cities and products",
                func=self._get_inventory_status
            ),
            Tool(
                name="get_low_stock_items",
                description="Get items that are low on stock and need restocking",
                func=self._get_low_stock_items
            ),
            Tool(
                name="get_city_performance",
                description="Get city performance metrics for the last N days. Input: number of days (e.g., '7')",
                func=self._get_city_performance
            ),
            Tool(
                name="allocate_inventory",
                description="Allocate inventory units to cities. Input: JSON with product, total_units, and allocation strategy",
                func=self._allocate_inventory
            ),
            Tool(
                name="trigger_restock",
                description="Trigger restock order for low inventory items. Input: JSON with city, product, and quantity",
                func=self._trigger_restock
            ),
            Tool(
                name="send_alert",
                description="Send alert notification. Input: JSON with message, priority, and recipients",
                func=self._send_alert
            )
        ]
        return tools
    
    def _create_prompt_template(self) -> PromptTemplate:
        """Create prompt template for the agent"""
        template = """You are an intelligent operations manager for a quick commerce company. 
        Your role is to analyze data, make decisions, and take actions to optimize inventory allocation and operations.

        Available tools:
        {tools}

        Use the following format:

        Question: the input question you must answer
        Thought: you should always think about what to do
        Action: the action to take, should be one of [{tool_names}]
        Action Input: the input to the action
        Observation: the result of the action
        ... (this Thought/Action/Action Input/Observation can repeat N times)
        Thought: I now know the final answer
        Final Answer: the final answer to the original input question

        Guidelines:
        1. Always analyze data before making decisions
        2. Provide specific, actionable recommendations
        3. Consider city performance, stock levels, and demand patterns
        4. Take autonomous actions when appropriate (allocate inventory, trigger restocks, send alerts)
        5. Explain your reasoning clearly

        Question: {input}
        {agent_scratchpad}"""

        return PromptTemplate(
            template=template,
            input_variables=["input", "agent_scratchpad", "tools", "tool_names"]
        )
    
    # Tool functions
    def _get_sales_analytics(self, days: str) -> str:
        """Get sales analytics"""
        try:
            days_int = int(days)
            df = self.db.get_sales_analytics(days_int)
            return df.to_string()
        except Exception as e:
            return f"Error getting sales analytics: {e}"
    
    def _get_inventory_status(self, _: str = "") -> str:
        """Get inventory status"""
        try:
            df = self.db.get_inventory_status()
            return df.to_string()
        except Exception as e:
            return f"Error getting inventory status: {e}"
    
    def _get_low_stock_items(self, _: str = "") -> str:
        """Get low stock items"""
        try:
            df = self.db.get_low_stock_items()
            return df.to_string()
        except Exception as e:
            return f"Error getting low stock items: {e}"
    
    def _get_city_performance(self, days: str) -> str:
        """Get city performance"""
        try:
            days_int = int(days)
            df = self.db.get_city_performance(days_int)
            return df.to_string()
        except Exception as e:
            return f"Error getting city performance: {e}"
    
    def _allocate_inventory(self, allocation_input: str) -> str:
        """Allocate inventory to cities"""
        try:
            data = json.loads(allocation_input)
            product = data.get('product')
            total_units = data.get('total_units')
            strategy = data.get('strategy', 'demand_based')
            
            # Get sales data for allocation
            sales_df = self.db.get_sales_analytics(7)
            product_sales = sales_df[sales_df['product'] == product]
            
            if product_sales.empty:
                return f"No sales data found for product: {product}"
            
            # Calculate allocation based on strategy
            if strategy == 'demand_based':
                # Allocate based on recent sales volume
                total_sales = product_sales['total_units'].sum()
                allocations = []
                
                for _, row in product_sales.iterrows():
                    city = row['city']
                    sales_ratio = row['total_units'] / total_sales
                    allocated_units = int(total_units * sales_ratio)
                    allocations.append(f"{city}: {allocated_units} units")
                
                allocation_summary = "\n".join(allocations)
                
                # Log the action
                action_id = self.db.log_action(
                    'inventory_allocation',
                    f"Allocated {total_units} units of {product} based on demand: {allocation_summary}",
                    self.n8n_webhook_url
                )
                
                # Trigger n8n workflow for allocation
                self._call_n8n_webhook({
                    'action_type': 'inventory_allocation',
                    'product': product,
                    'total_units': total_units,
                    'allocations': allocations,
                    'action_id': action_id
                })
                
                return f"Allocated {total_units} units of {product}:\n{allocation_summary}\n\nAction logged with ID: {action_id}"
            
            return "Invalid allocation strategy"
            
        except Exception as e:
            return f"Error allocating inventory: {e}"
    
    def _trigger_restock(self, restock_input: str) -> str:
        """Trigger restock order"""
        try:
            data = json.loads(restock_input)
            city = data.get('city')
            product = data.get('product')
            quantity = data.get('quantity')
            
            # Log the action
            action_id = self.db.log_action(
                'restock_order',
                f"Triggered restock order for {city}: {quantity} units of {product}",
                self.n8n_webhook_url
            )
            
            # Trigger n8n workflow for restock
            self._call_n8n_webhook({
                'action_type': 'restock_order',
                'city': city,
                'product': product,
                'quantity': quantity,
                'action_id': action_id
            })
            
            return f"Triggered restock order: {quantity} units of {product} for {city}\nAction logged with ID: {action_id}"
            
        except Exception as e:
            return f"Error triggering restock: {e}"
    
    def _send_alert(self, alert_input: str) -> str:
        """Send alert notification"""
        try:
            data = json.loads(alert_input)
            message = data.get('message')
            priority = data.get('priority', 'medium')
            recipients = data.get('recipients', ['operations@company.com'])
            
            # Log the action
            action_id = self.db.log_action(
                'alert',
                f"Sent {priority} priority alert: {message}",
                self.n8n_webhook_url
            )
            
            # Trigger n8n workflow for alert
            self._call_n8n_webhook({
                'action_type': 'alert',
                'message': message,
                'priority': priority,
                'recipients': recipients,
                'action_id': action_id
            })
            
            return f"Sent {priority} priority alert: {message}\nAction logged with ID: {action_id}"
            
        except Exception as e:
            return f"Error sending alert: {e}"
    
    def _call_n8n_webhook(self, data: Dict[str, Any]) -> bool:
        """Call n8n webhook for automation"""
        try:
            response = requests.post(
                self.n8n_webhook_url,
                json=data,
                timeout=10
            )
            response.raise_for_status()
            print(f"n8n webhook called successfully: {response.status_code}")
            return True
        except Exception as e:
            print(f"Error calling n8n webhook: {e}")
            return False
    
    def process_query(self, query: str) -> str:
        """Process a user query using the agent"""
        if not self.agent_executor:
            # Fallback to mock responses when no OpenAI API key
            return self._mock_response(query)
        
        try:
            result = self.agent_executor.invoke({"input": query})
            return result['output']
        except Exception as e:
            return f"Error processing query: {e}"
    
    def _mock_response(self, query: str) -> str:
        """Provide mock responses when OpenAI API is not available"""
        query_lower = query.lower()
        
        if "allocate" in query_lower and "units" in query_lower:
            # Mock allocation response
            return """Based on sales analysis, I recommend the following allocation:
            
Mumbai: 400 units (40% - highest demand)
Delhi: 350 units (35% - strong performance)
Bangalore: 250 units (25% - steady growth)

This allocation is based on the last 7 days of sales data showing Mumbai leading in demand, followed by Delhi and Bangalore. The distribution ensures optimal inventory placement for quick commerce delivery."""
        
        elif "low stock" in query_lower or "restock" in query_lower:
            # Mock low stock response
            low_stock_df = self.db.get_low_stock_items()
            if not low_stock_df.empty:
                items = []
                for _, row in low_stock_df.head(5).iterrows():
                    items.append(f"- {row['city']}: {row['product']} ({row['current_stock']} units remaining)")
                
                return f"""Found {len(low_stock_df)} items with low stock:
                
{chr(10).join(items)}

Recommendation: Trigger immediate restock orders for these items to prevent stockouts. I'll send alerts to the warehouse team and suppliers."""
            else:
                return "All items are well-stocked. No immediate restock required."
        
        elif "performance" in query_lower or "underperforming" in query_lower:
            # Mock performance response
            performance_df = self.db.get_city_performance(7)
            if not performance_df.empty:
                bottom_cities = performance_df.tail(2)
                return f"""Cities that may need attention:
                
- {bottom_cities.iloc[-1]['city']}: {bottom_cities.iloc[-1]['total_revenue']:,.0f} revenue (lowest)
- {bottom_cities.iloc[-2]['city']}: {bottom_cities.iloc[-2]['total_revenue']:,.0f} revenue

Recommendation: Analyze marketing strategies and inventory allocation for these cities to improve performance."""
            else:
                return "All cities are performing well based on current metrics."
        
        else:
            return "I can help you with inventory allocation, stock analysis, city performance, and operational decisions. Please ask me about specific scenarios like 'allocate 1000 units of Product X' or 'which cities need attention?'"
    
    def get_insights(self) -> Dict[str, Any]:
        """Get current business insights"""
        try:
            # Get key metrics
            sales_analytics = self.db.get_sales_analytics(7)
            inventory_status = self.db.get_inventory_status()
            low_stock_items = self.db.get_low_stock_items()
            city_performance = self.db.get_city_performance(7)
            
            insights = {
                'total_revenue_7d': sales_analytics['total_revenue'].sum(),
                'total_units_sold_7d': sales_analytics['total_units'].sum(),
                'low_stock_count': len(low_stock_items),
                'top_performing_city': city_performance.iloc[0]['city'] if not city_performance.empty else None,
                'bottom_performing_city': city_performance.iloc[-1]['city'] if not city_performance.empty else None,
                'critical_alerts': len(low_stock_items[low_stock_items['current_stock'] <= 5])
            }
            
            return insights
            
        except Exception as e:
            return {'error': f"Error getting insights: {e}"}
    
    def close(self):
        """Close database connection"""
        self.db.close()

if __name__ == "__main__":
    # Test the agent
    agent = QuickCommerceAgent()
    
    # Test queries
    test_queries = [
        "Allocate 1000 units of Smartphone",
        "Which items need urgent restocking?",
        "Which cities are underperforming this week?"
    ]
    
    for query in test_queries:
        print(f"\nQuery: {query}")
        print(f"Response: {agent.process_query(query)}")
        print("-" * 50)
    
    agent.close()
