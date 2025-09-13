"""
Standalone Streamlit Frontend for EQREV Hackathon - Agentic AI for Quick Commerce
This version works without the FastAPI backend - uses direct database access
"""
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import json
import sys
import os

# Add backend to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'backend'))

from ai_agent import QuickCommerceAgent

# Configuration
st.set_page_config(
    page_title="Quick Commerce AI Agent",
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #1f77b4;
    }
    .alert-card {
        background-color: #fff2cc;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #ff6b6b;
    }
    .success-card {
        background-color: #d4edda;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #28a745;
    }
</style>
""", unsafe_allow_html=True)

def get_agent():
    """Get AI agent instance"""
    try:
        # Change to the project root directory for database access
        original_cwd = os.getcwd()
        project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        os.chdir(project_root)
        
        agent = QuickCommerceAgent()
        
        # Restore original working directory
        os.chdir(original_cwd)
        
        return agent
    except Exception as e:
        st.error(f"Error initializing agent: {e}")
        return None

def display_metrics(insights):
    """Display key metrics"""
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            label="7-Day Revenue",
            value=f"₹{insights.get('total_revenue_7d', 0):,.0f}",
            delta=f"vs previous week"
        )
    
    with col2:
        st.metric(
            label="Units Sold (7D)",
            value=f"{insights.get('total_units_sold_7d', 0):,}",
            delta=f"units"
        )
    
    with col3:
        st.metric(
            label="Low Stock Items",
            value=insights.get('low_stock_count', 0),
            delta="need attention" if insights.get('low_stock_count', 0) > 0 else None
        )
    
    with col4:
        st.metric(
            label="Critical Alerts",
            value=insights.get('critical_alerts', 0),
            delta="urgent" if insights.get('critical_alerts', 0) > 0 else None
        )

def display_sales_chart():
    """Display sales performance chart"""
    st.subheader("📊 Sales Performance (Last 7 Days)")
    
    try:
        agent = get_agent()
        if agent is None:
            st.error("Unable to initialize AI agent. Please check the system.")
            return
        sales_data = agent.db.get_sales_analytics(7)
        
        if not sales_data.empty:
            # Create city performance chart
            city_performance = sales_data.groupby('city').agg({
                'total_units': 'sum',
                'total_revenue': 'sum'
            }).reset_index()
            
            col1, col2 = st.columns(2)
            
            with col1:
                fig_units = px.bar(
                    city_performance, 
                    x='city', 
                    y='total_units',
                    title="Units Sold by City",
                    color='total_units',
                    color_continuous_scale='Blues'
                )
                fig_units.update_layout(showlegend=False)
                st.plotly_chart(fig_units, use_container_width=True)
            
            with col2:
                fig_revenue = px.bar(
                    city_performance, 
                    x='city', 
                    y='total_revenue',
                    title="Revenue by City",
                    color='total_revenue',
                    color_continuous_scale='Greens'
                )
                fig_revenue.update_layout(showlegend=False)
                st.plotly_chart(fig_revenue, use_container_width=True)
        else:
            st.warning("No sales data available")
    except Exception as e:
        st.error(f"Error loading sales data: {e}")

def display_inventory_status():
    """Display inventory status"""
    st.subheader("📦 Inventory Status")
    
    try:
        agent = get_agent()
        if agent is None:
            st.error("Unable to initialize AI agent. Please check the system.")
            return
        inventory_data = agent.db.get_inventory_status()
        
        if not inventory_data.empty:
            # Filter for low stock items
            low_stock = inventory_data[inventory_data['stock_status'] == 'LOW_STOCK']
            
            if not low_stock.empty:
                st.warning(f"⚠️ {len(low_stock)} items need immediate restocking!")
                
                # Display low stock items
                for _, item in low_stock.head(10).iterrows():
                    with st.container():
                        col1, col2, col3, col4 = st.columns([2, 2, 1, 1])
                        with col1:
                            st.write(f"**{item['product']}** in {item['city']}")
                        with col2:
                            st.write(f"Stock: {item['current_stock']}/{item['max_capacity']}")
                        with col3:
                            st.write(f"Reorder: {item['reorder_level']}")
                        with col4:
                            if st.button("Restock", key=f"restock_{item['product']}_{item['city']}"):
                                st.success("Restock order triggered!")
            else:
                st.success("✅ All items are well-stocked!")
            
            # Display inventory chart
            col1, col2 = st.columns(2)
            
            with col1:
                # Stock status distribution
                status_counts = inventory_data['stock_status'].value_counts()
                fig_status = px.pie(
                    values=status_counts.values,
                    names=status_counts.index,
                    title="Stock Status Distribution",
                    color_discrete_map={
                        'LOW_STOCK': '#ff6b6b',
                        'MEDIUM_STOCK': '#ffd93d',
                        'HIGH_STOCK': '#6bcf7f'
                    }
                )
                st.plotly_chart(fig_status, use_container_width=True)
            
            with col2:
                # Top products by stock
                top_products = inventory_data.nlargest(10, 'current_stock')
                fig_products = px.bar(
                    top_products,
                    x='current_stock',
                    y='product',
                    title="Top 10 Products by Stock",
                    orientation='h'
                )
                st.plotly_chart(fig_products, use_container_width=True)
        else:
            st.warning("No inventory data available")
    except Exception as e:
        st.error(f"Error loading inventory data: {e}")

def chat_interface():
    """Chat interface with the AI agent"""
    st.subheader("🤖 AI Operations Manager")
    
    # Initialize chat history
    if "messages" not in st.session_state:
        st.session_state.messages = []
    
    # Display chat messages
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
    
    # Chat input
    if prompt := st.chat_input("Ask the AI agent about inventory, allocation, or operations..."):
        # Add user message to chat history
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)
        
        # Get AI response
        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                try:
                    agent = get_agent()
                    response = agent.process_query(prompt)
                except Exception as e:
                    response = f"Sorry, I encountered an error: {e}"
            
            st.markdown(response)
        
        # Add assistant response to chat history
        st.session_state.messages.append({"role": "assistant", "content": response})

def quick_actions():
    """Quick action buttons"""
    st.subheader("⚡ Quick Actions")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("**Inventory Allocation**")
        product = st.selectbox("Product", ["Smartphone", "Laptop", "Headphones", "Tablet", "Smart Watch"])
        units = st.number_input("Units to Allocate", min_value=1, max_value=10000, value=1000)
        if st.button("Allocate Inventory"):
            try:
                agent = get_agent()
                query = f"Allocate {units} units of {product}"
                response = agent.process_query(query)
                st.success("Inventory allocation completed!")
                st.text_area("Allocation Result", response, height=100)
            except Exception as e:
                st.error(f"Error: {e}")
    
    with col2:
        st.markdown("**Send Alert**")
        alert_message = st.text_area("Alert Message", "Stock levels are critically low!")
        priority = st.selectbox("Priority", ["low", "medium", "high", "critical"])
        if st.button("Send Alert"):
            try:
                agent = get_agent()
                query = f"Send {priority} priority alert: {alert_message}"
                response = agent.process_query(query)
                st.success("Alert sent successfully!")
                st.text_area("Alert Result", response, height=100)
            except Exception as e:
                st.error(f"Error: {e}")
    
    with col3:
        st.markdown("**System Status**")
        try:
            agent = get_agent()
            insights = agent.get_insights()
            st.success("✅ System Healthy")
            st.write(f"**Database Records:** {insights.get('total_units_sold_7d', 0):,}")
            st.write(f"**Low Stock Items:** {insights.get('low_stock_count', 0)}")
        except Exception as e:
            st.error(f"❌ System Error: {e}")

def main():
    """Main application"""
    # Header
    st.markdown('<h1 class="main-header">🚀 Quick Commerce AI Operations Manager</h1>', unsafe_allow_html=True)
    
    # Sidebar
    with st.sidebar:
        st.header("🎛️ Dashboard Controls")
        
        # Refresh button
        if st.button("🔄 Refresh Data"):
            st.rerun()
        
        # Quick stats
        st.subheader("📈 Quick Stats")
        try:
            agent = get_agent()
            insights = agent.get_insights()
            st.write(f"**Revenue (7D):** ₹{insights.get('total_revenue_7d', 0):,.0f}")
            st.write(f"**Units Sold:** {insights.get('total_units_sold_7d', 0):,}")
            st.write(f"**Low Stock:** {insights.get('low_stock_count', 0)} items")
            st.write(f"**Critical:** {insights.get('critical_alerts', 0)} alerts")
        except Exception as e:
            st.error(f"Error loading stats: {e}")
        
        # Navigation
        st.subheader("🧭 Navigation")
        page = st.selectbox(
            "Select Page",
            ["Dashboard", "AI Chat", "Inventory", "Analytics", "Actions"]
        )
    
    # Main content based on navigation
    if page == "Dashboard":
        st.header("📊 Operations Dashboard")
        
        # Display metrics
        try:
            agent = get_agent()
            if agent is None:
                st.error("Unable to initialize AI agent. Please check the system.")
            else:
                insights = agent.get_insights()
                display_metrics(insights)
        except Exception as e:
            st.error(f"Error loading insights: {e}")
        
        # Display charts
        display_sales_chart()
        display_inventory_status()
        
        # Recent actions (mock data)
        st.subheader("📋 Recent Actions")
        recent_actions = [
            {"time": "2 min ago", "action": "Allocated 500 units of Smartphone to Mumbai", "status": "completed"},
            {"time": "15 min ago", "action": "Triggered restock for Headphones in Delhi", "status": "pending"},
            {"time": "1 hour ago", "action": "Sent alert for low stock in Chennai", "status": "completed"},
        ]
        
        for action in recent_actions:
            col1, col2, col3 = st.columns([2, 4, 1])
            with col1:
                st.write(action["time"])
            with col2:
                st.write(action["action"])
            with col3:
                if action["status"] == "completed":
                    st.success("✓")
                else:
                    st.warning("⏳")
    
    elif page == "AI Chat":
        st.header("🤖 AI Operations Manager Chat")
        chat_interface()
    
    elif page == "Inventory":
        st.header("📦 Inventory Management")
        display_inventory_status()
    
    elif page == "Analytics":
        st.header("📈 Analytics & Insights")
        display_sales_chart()
        
        # Additional analytics
        st.subheader("🏙️ City Performance")
        try:
            agent = get_agent()
            city_data = agent.db.get_city_performance(7)
            if not city_data.empty:
                fig = px.scatter(
                    city_data,
                    x='total_units',
                    y='total_revenue',
                    size='products_sold',
                    color='avg_order_value',
                    hover_name='city',
                    title="City Performance Scatter Plot",
                    labels={
                        'total_units': 'Total Units Sold',
                        'total_revenue': 'Total Revenue',
                        'products_sold': 'Products Sold',
                        'avg_order_value': 'Avg Order Value'
                    }
                )
                st.plotly_chart(fig, use_container_width=True)
        except Exception as e:
            st.error(f"Error loading city data: {e}")
    
    elif page == "Actions":
        st.header("⚡ Quick Actions")
        quick_actions()

if __name__ == "__main__":
    main()
