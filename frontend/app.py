"""
Streamlit Frontend for EQREV Hackathon - Agentic AI for Quick Commerce
"""
import streamlit as st
import requests
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import json

# Configuration
st.set_page_config(
    page_title="Quick Commerce AI Agent",
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="expanded"
)

# API Configuration
API_BASE_URL = "http://localhost:8000"

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

def call_api(endpoint, method="GET", data=None):
    """Call the FastAPI backend"""
    try:
        url = f"{API_BASE_URL}{endpoint}"
        if method == "GET":
            response = requests.get(url)
        elif method == "POST":
            response = requests.post(url, json=data)
        
        response.raise_for_status()
        return response.json()
    except Exception as e:
        st.error(f"API Error: {str(e)}")
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
    
    sales_data = call_api("/data/sales")
    if sales_data:
        df = pd.DataFrame(sales_data)
        
        # Create city performance chart
        city_performance = df.groupby('city').agg({
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

def display_inventory_status():
    """Display inventory status"""
    st.subheader("📦 Inventory Status")
    
    inventory_data = call_api("/data/inventory")
    if inventory_data:
        df = pd.DataFrame(inventory_data)
        
        # Filter for low stock items
        low_stock = df[df['stock_status'] == 'LOW_STOCK']
        
        if not low_stock.empty:
            st.warning(f"⚠️ {len(low_stock)} items need immediate restocking!")
            
            # Display low stock items
            for _, item in low_stock.iterrows():
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
                            restock_data = {
                                "city": item['city'],
                                "product": item['product'],
                                "quantity": item['reorder_level'] * 2
                            }
                            result = call_api("/restock", "POST", restock_data)
                            if result:
                                st.success("Restock order triggered!")
                                st.rerun()
        
        # Display inventory chart
        col1, col2 = st.columns(2)
        
        with col1:
            # Stock status distribution
            status_counts = df['stock_status'].value_counts()
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
            top_products = df.nlargest(10, 'current_stock')
            fig_products = px.bar(
                top_products,
                x='current_stock',
                y='product',
                title="Top 10 Products by Stock",
                orientation='h'
            )
            st.plotly_chart(fig_products, use_container_width=True)

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
                response_data = call_api("/query", "POST", {"query": prompt})
                if response_data:
                    response = response_data["response"]
                else:
                    response = "Sorry, I encountered an error. Please try again."
            
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
            allocation_data = {
                "product": product,
                "total_units": units,
                "strategy": "demand_based"
            }
            result = call_api("/allocate", "POST", allocation_data)
            if result:
                st.success("Inventory allocation completed!")
                st.json(result)
    
    with col2:
        st.markdown("**Send Alert**")
        alert_message = st.text_area("Alert Message", "Stock levels are critically low!")
        priority = st.selectbox("Priority", ["low", "medium", "high", "critical"])
        if st.button("Send Alert"):
            alert_data = {
                "message": alert_message,
                "priority": priority,
                "recipients": ["operations@company.com"]
            }
            result = call_api("/alert", "POST", alert_data)
            if result:
                st.success("Alert sent successfully!")
    
    with col3:
        st.markdown("**System Status**")
        health = call_api("/health")
        if health:
            if health["status"] == "healthy":
                st.success("✅ System Healthy")
            else:
                st.error("❌ System Issues")
        else:
            st.error("❌ Cannot connect to backend")

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
        insights = call_api("/insights")
        if insights and "insights" in insights:
            insights_data = insights["insights"]
            st.write(f"**Revenue (7D):** ₹{insights_data.get('total_revenue_7d', 0):,.0f}")
            st.write(f"**Units Sold:** {insights_data.get('total_units_sold_7d', 0):,}")
            st.write(f"**Low Stock:** {insights_data.get('low_stock_count', 0)} items")
            st.write(f"**Critical:** {insights_data.get('critical_alerts', 0)} alerts")
        
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
        if insights and "insights" in insights:
            display_metrics(insights["insights"])
        
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
        city_data = call_api("/data/cities")
        if city_data:
            df = pd.DataFrame(city_data)
            fig = px.scatter(
                df,
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
    
    elif page == "Actions":
        st.header("⚡ Quick Actions")
        quick_actions()

if __name__ == "__main__":
    main()
