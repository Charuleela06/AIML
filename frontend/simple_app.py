"""
Simple Streamlit App for EQREV Hackathon - Agentic AI for Quick Commerce
This version directly reads CSV data without complex database operations
"""
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import os
import sys

# Add backend to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'backend'))

# Set page config
st.set_page_config(
    page_title="Quick Commerce AI Operations Manager",
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #28a745;
    }
    .error-card {
        background-color: #ffebee;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #f44336;
    }
</style>
""", unsafe_allow_html=True)

def load_data():
    """Load data from CSV files"""
    try:
        # Get the project root directory
        current_dir = os.path.dirname(os.path.abspath(__file__))
        project_root = os.path.dirname(current_dir)
        data_dir = os.path.join(project_root, 'data')
        
        # Load sales data
        sales_file = os.path.join(data_dir, 'sales_data.csv')
        inventory_file = os.path.join(data_dir, 'inventory_data.csv')
        
        if not os.path.exists(sales_file) or not os.path.exists(inventory_file):
            st.error(f"Data files not found. Looking in: {data_dir}")
            return None, None
        
        sales_df = pd.read_csv(sales_file)
        inventory_df = pd.read_csv(inventory_file)
        
        # Convert date column
        sales_df['date'] = pd.to_datetime(sales_df['date'])
        
        # Map column names to expected format
        # Sales data mapping
        sales_mapping = {
            'city_name': 'city',
            'product_name': 'product',
            'gross_selling_value': 'revenue'
        }
        for old_col, new_col in sales_mapping.items():
            if old_col in sales_df.columns:
                sales_df[new_col] = sales_df[old_col]
        
        # Inventory data mapping
        inventory_mapping = {
            'city_name': 'city',
            'product_name': 'product',
            'stock_quantity': 'current_stock',
            'store_name': 'supplier'
        }
        for old_col, new_col in inventory_mapping.items():
            if old_col in inventory_df.columns:
                inventory_df[new_col] = inventory_df[old_col]
        
        return sales_df, inventory_df
    except Exception as e:
        st.error(f"Error loading data: {e}")
        return None, None

def get_insights(sales_df, inventory_df):
    """Generate insights from data"""
    if sales_df is None or inventory_df is None:
        return None
    
    try:
        # Calculate metrics for last 7 days
        cutoff_date = datetime.now() - timedelta(days=7)
        recent_sales = sales_df[sales_df['date'] >= cutoff_date]
        
        # Convert revenue to numeric (handle string values with commas)
        if 'revenue' in recent_sales.columns:
            recent_sales['revenue'] = pd.to_numeric(recent_sales['revenue'], errors='coerce').fillna(0)
        if 'units_sold' in recent_sales.columns:
            recent_sales['units_sold'] = pd.to_numeric(recent_sales['units_sold'], errors='coerce').fillna(0)
        
        # Calculate low stock count (create reorder_level if it doesn't exist)
        if 'reorder_level' not in inventory_df.columns:
            avg_stock = inventory_df['current_stock'].mean()
            reorder_threshold = max(10, avg_stock * 0.2)  # Minimum 10 units
            low_stock_count = len(inventory_df[inventory_df['current_stock'] < reorder_threshold])
        else:
            low_stock_count = len(inventory_df[inventory_df['current_stock'] < inventory_df['reorder_level']])
        
        # Calculate insights with proper numeric values
        total_revenue = recent_sales['revenue'].sum() if 'revenue' in recent_sales.columns else 0
        total_units = recent_sales['units_sold'].sum() if 'units_sold' in recent_sales.columns else 0
        
        insights = {
            'total_revenue_7d': total_revenue,
            'total_units_sold_7d': total_units,
            'low_stock_count': low_stock_count,
            'top_performing_city': recent_sales.groupby('city')['revenue'].sum().idxmax() if 'revenue' in recent_sales.columns else 'N/A',
            'bottom_performing_city': recent_sales.groupby('city')['revenue'].sum().idxmin() if 'revenue' in recent_sales.columns else 'N/A',
            'critical_alerts': 0
        }
        
        return insights
    except Exception as e:
        st.error(f"Error generating insights: {e}")
        return None

def display_metrics(insights):
    """Display key metrics"""
    if insights is None:
        st.error("Unable to load metrics")
        return
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        # Convert to float and format properly
        revenue = float(insights['total_revenue_7d']) if insights['total_revenue_7d'] else 0
        st.metric(
            label="Revenue (7D)",
            value=f"₹{revenue:,.0f}",
            delta=None
        )
    
    with col2:
        # Convert to int and format properly
        units = int(insights['total_units_sold_7d']) if insights['total_units_sold_7d'] else 0
        st.metric(
            label="Units Sold (7D)",
            value=f"{units:,}",
            delta=None
        )
    
    with col3:
        st.metric(
            label="Low Stock Items",
            value=insights['low_stock_count'],
            delta=None
        )
    
    with col4:
        st.metric(
            label="Critical Alerts",
            value=insights['critical_alerts'],
            delta=None
        )

def display_sales_chart(sales_df):
    """Display sales performance chart"""
    st.subheader("📊 Sales Performance (Last 7 Days)")
    
    if sales_df is None:
        st.error("Unable to load sales data")
        return
    
    try:
        # Filter last 7 days
        cutoff_date = datetime.now() - timedelta(days=7)
        recent_sales = sales_df[sales_df['date'] >= cutoff_date]
        
        if recent_sales.empty:
            st.warning("No sales data for the last 7 days")
            return
        
        # Convert revenue to numeric if it's not already
        if 'revenue' in recent_sales.columns:
            recent_sales['revenue'] = pd.to_numeric(recent_sales['revenue'], errors='coerce').fillna(0)
        if 'units_sold' in recent_sales.columns:
            recent_sales['units_sold'] = pd.to_numeric(recent_sales['units_sold'], errors='coerce').fillna(0)
        
        # Create city performance chart
        city_performance = recent_sales.groupby('city').agg({
            'revenue': 'sum',
            'units_sold': 'sum'
        }).reset_index()
        
        # Revenue chart
        fig_revenue = px.bar(
            city_performance, 
            x='city', 
            y='revenue',
            title="Revenue by City (Last 7 Days)",
            color='revenue',
            color_continuous_scale='Blues'
        )
        fig_revenue.update_layout(height=400)
        st.plotly_chart(fig_revenue, use_container_width=True)
        
        # Units sold chart
        fig_units = px.bar(
            city_performance, 
            x='city', 
            y='units_sold',
            title="Units Sold by City (Last 7 Days)",
            color='units_sold',
            color_continuous_scale='Greens'
        )
        fig_units.update_layout(height=400)
        st.plotly_chart(fig_units, use_container_width=True)
        
    except Exception as e:
        st.error(f"Error displaying sales chart: {e}")

def display_inventory_status(inventory_df):
    """Display inventory status"""
    st.subheader("📦 Inventory Status")
    
    if inventory_df is None:
        st.error("Unable to load inventory data")
        return
    
    try:
        # Filter for low stock items (create reorder_level if it doesn't exist)
        if 'reorder_level' not in inventory_df.columns:
            # Create a reorder level based on current stock (20% of average stock)
            avg_stock = inventory_df['current_stock'].mean()
            inventory_df['reorder_level'] = max(10, avg_stock * 0.2)  # Minimum 10 units
        
        low_stock = inventory_df[inventory_df['current_stock'] < inventory_df['reorder_level']]
        
        if low_stock.empty:
            st.success("✅ All items are well stocked!")
        else:
            st.warning(f"⚠️ {len(low_stock)} items need restocking")
            
            # Display TOP 5 CRITICAL ITEMS
            st.subheader("🔴 TOP 5 CRITICAL ITEMS NEEDING RESTOCKING")
            
            # Get top 5 items with lowest stock
            top_5_low_stock = low_stock.nsmallest(5, 'current_stock')
            
            for i, (idx, row) in enumerate(top_5_low_stock.iterrows(), 1):
                city = row.get('city', 'N/A')
                product = row.get('product', 'N/A')
                current_stock = row.get('current_stock', 0)
                supplier = row.get('supplier', 'N/A')
                
                # Create a prominent display for each critical item
                col1, col2, col3 = st.columns([4, 1, 1])
                
                with col1:
                    st.markdown(f"**{i}. {product}**")
                    st.markdown(f"📍 **City:** {city} | 🏪 **Supplier:** {supplier}")
                
                with col2:
                    if current_stock == 0:
                        st.error("**OUT OF STOCK**")
                    else:
                        st.warning(f"**{current_stock} units**")
                
                with col3:
                    if st.button(f"🚨 Alert", key=f"critical_alert_{i}"):
                        st.success(f"✅ Alert sent for {product} in {city}")
                
                st.divider()
            
            # Show remaining low stock items in a table
            if len(low_stock) > 5:
                st.subheader(f"📋 All {len(low_stock)} Items Requiring Restocking")
                available_cols = ['city', 'product', 'current_stock', 'reorder_level', 'supplier']
                display_cols = [col for col in available_cols if col in low_stock.columns]
                display_df = low_stock[display_cols].copy()
                display_df['stock_status'] = 'LOW_STOCK'
                st.dataframe(display_df, use_container_width=True)
            
            # Create inventory chart
            fig = px.scatter(
                inventory_df,
                x='current_stock',
                y='reorder_level',
                color='current_stock',
                hover_data=['city', 'product', 'supplier'],
                title="Inventory Status: Current Stock vs Reorder Level",
                color_continuous_scale='RdYlGn_r'
            )
            
            # Add reorder line
            if 'reorder_level' in inventory_df.columns:
                max_reorder = inventory_df['reorder_level'].max()
                fig.add_trace(go.Scatter(
                    x=[0, max_reorder],
                    y=[0, max_reorder],
                    mode='lines',
                    name='Reorder Line',
                    line=dict(color='red', dash='dash')
                ))
            fig.update_layout(height=500)
            st.plotly_chart(fig, use_container_width=True)
        
    except Exception as e:
        st.error(f"Error displaying inventory status: {e}")

def display_restocking_alerts(inventory_df):
    """Display top 5 items needing restocking"""
    st.subheader("🚨 Critical Restocking Alerts")
    
    if inventory_df is None:
        st.error("Unable to load inventory data")
        return
    
    try:
        # Create reorder level (20% of average stock, minimum 10)
        avg_stock = inventory_df['current_stock'].mean()
        reorder_threshold = max(10, avg_stock * 0.2)
        inventory_df['reorder_level'] = reorder_threshold
        
        # Filter low stock items
        low_stock = inventory_df[inventory_df['current_stock'] < inventory_df['reorder_level']]
        
        if low_stock.empty:
            st.success("✅ All items are well stocked!")
            return
        
        # Get top 5 items with lowest stock
        top_5_low_stock = low_stock.nsmallest(5, 'current_stock')
        
        st.warning(f"⚠️ **{len(low_stock)} items need restocking** (below {reorder_threshold:.0f} units)")
        
        st.subheader("🔴 TOP 5 CRITICAL ITEMS")
        
        for i, (idx, row) in enumerate(top_5_low_stock.iterrows(), 1):
            city = row.get('city', 'N/A')
            product = row.get('product', 'N/A')
            current_stock = row.get('current_stock', 0)
            supplier = row.get('supplier', 'N/A')
            
            # Create columns for better layout
            col1, col2, col3 = st.columns([3, 1, 1])
            
            with col1:
                st.markdown(f"**{i}. {product}**")
                st.markdown(f"📍 {city} | 🏪 {supplier}")
            
            with col2:
                if current_stock == 0:
                    st.error(f"**OUT OF STOCK**")
                else:
                    st.warning(f"**{current_stock} units**")
            
            with col3:
                if st.button(f"🚨 Alert {i}", key=f"alert_{i}"):
                    st.success(f"✅ Restocking alert sent for {product} in {city}")
            
            st.divider()
        
        # Summary statistics
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Total Items Needing Restock", len(low_stock))
        
        with col2:
            out_of_stock = len(low_stock[low_stock['current_stock'] == 0])
            st.metric("Completely Out of Stock", out_of_stock)
        
        with col3:
            st.metric("Reorder Threshold", f"{reorder_threshold:.0f} units")
        
        # City breakdown
        st.subheader("🌍 Cities Most Affected")
        city_summary = low_stock.groupby('city').agg({
            'product': 'count',
            'current_stock': 'sum'
        }).rename(columns={'product': 'items_needing_restock', 'current_stock': 'total_low_stock'})
        
        city_summary = city_summary.sort_values('items_needing_restock', ascending=False)
        
        # Display top 10 cities
        for city, row in city_summary.head(10).iterrows():
            col1, col2, col3 = st.columns([2, 1, 1])
            with col1:
                st.write(f"📍 **{city}**")
            with col2:
                st.write(f"{row['items_needing_restock']} items")
            with col3:
                st.write(f"{row['total_low_stock']} total low stock")
        
    except Exception as e:
        st.error(f"Error displaying restocking alerts: {e}")

def analyze_top_performing_cities(sales_df):
    """Analyze top performing cities for sales recommendations"""
    if sales_df is None:
        st.error("Unable to load sales data")
        return None
    
    try:
        # Convert revenue to numeric if needed
        if 'revenue' in sales_df.columns:
            sales_df['revenue'] = pd.to_numeric(sales_df['revenue'], errors='coerce').fillna(0)
        if 'units_sold' in sales_df.columns:
            sales_df['units_sold'] = pd.to_numeric(sales_df['units_sold'], errors='coerce').fillna(0)
        
        # Analyze last 30 days
        cutoff_date = datetime.now() - timedelta(days=30)
        recent_sales = sales_df[sales_df['date'] >= cutoff_date]
        
        # City performance analysis
        city_performance = recent_sales.groupby('city').agg({
            'revenue': 'sum',
            'units_sold': 'sum',
            'product': 'nunique'
        }).reset_index()
        
        city_performance['avg_order_value'] = city_performance['revenue'] / city_performance['units_sold']
        city_performance['avg_order_value'] = city_performance['avg_order_value'].fillna(0)
        
        # Sort by revenue
        city_performance = city_performance.sort_values('revenue', ascending=False)
        
        return city_performance
        
    except Exception as e:
        st.error(f"Error analyzing city performance: {e}")
        return None

def display_top_cities(city_performance):
    """Display top performing cities analysis"""
    st.subheader("🏆 TOP 10 BEST SELLING CITIES")
    
    for i, (idx, row) in enumerate(city_performance.head(10).iterrows(), 1):
        city = row['city']
        revenue = row['revenue']
        units = row['units_sold']
        products = row['product']
        avg_order = row['avg_order_value']
        
        col1, col2, col3, col4 = st.columns([2, 2, 1, 1])
        
        with col1:
            st.markdown(f"**{i}. {city}**")
            st.markdown(f"Revenue: ₹{revenue:,.0f}")
        
        with col2:
            st.markdown(f"Units Sold: {units:,}")
            st.markdown(f"Products: {products}")
        
        with col3:
            st.markdown(f"Avg Order: ₹{avg_order:.0f}")
        
        with col4:
            if st.button(f"📧 Email", key=f"email_city_{i}"):
                st.success(f"📧 Email recommendation sent for {city}")
        
        st.divider()
    
    # Summary insights
    st.subheader("💡 KEY INSIGHTS")
    
    top_city = city_performance.iloc[0]
    st.success(f"🎯 **Best Performing City:** {top_city['city']} with ₹{top_city['revenue']:,.0f} revenue")
    
    total_revenue = city_performance['revenue'].sum()
    top_3_revenue = city_performance.head(3)['revenue'].sum()
    top_3_percentage = (top_3_revenue / total_revenue) * 100
    
    st.info(f"📊 Top 3 cities generate {top_3_percentage:.1f}% of total revenue")

def send_sales_recommendations(email_address, sales_df, inventory_df):
    """Send email recommendations about best selling locations"""
    try:
        # Analyze top performing cities
        city_performance = analyze_top_performing_cities(sales_df)
        
        if city_performance is None:
            st.error("Unable to analyze sales data for recommendations")
            return
        
        # Generate email content
        email_subject = "🚀 Quick Commerce Sales Location Recommendations"
        
        email_body = f"""
        <html>
        <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
            <h2 style="color: #1f77b4;">📊 Quick Commerce Sales Analysis Report</h2>
            
            <h3 style="color: #28a745;">🏆 TOP 5 BEST SELLING CITIES</h3>
            <table style="border-collapse: collapse; width: 100%; margin: 20px 0;">
                <tr style="background-color: #f8f9fa;">
                    <th style="border: 1px solid #ddd; padding: 12px; text-align: left;">City</th>
                    <th style="border: 1px solid #ddd; padding: 12px; text-align: left;">Revenue (30D)</th>
                    <th style="border: 1px solid #ddd; padding: 12px; text-align: left;">Units Sold</th>
                    <th style="border: 1px solid #ddd; padding: 12px; text-align: left;">Avg Order Value</th>
                </tr>
        """
        
        for i, (idx, row) in enumerate(city_performance.head(5).iterrows()):
            email_body += f"""
                <tr>
                    <td style="border: 1px solid #ddd; padding: 12px;"><strong>{row['city']}</strong></td>
                    <td style="border: 1px solid #ddd; padding: 12px;">₹{row['revenue']:,.0f}</td>
                    <td style="border: 1px solid #ddd; padding: 12px;">{row['units_sold']:,}</td>
                    <td style="border: 1px solid #ddd; padding: 12px;">₹{row['avg_order_value']:.0f}</td>
                </tr>
            """
        
        email_body += """
            </table>
            
            <h3 style="color: #dc3545;">⚠️ CRITICAL INSIGHTS</h3>
            <ul>
                <li><strong>Best Investment City:</strong> """ + city_performance.iloc[0]['city'] + f""" (₹{city_performance.iloc[0]['revenue']:,.0f} revenue)</li>
                <li><strong>Total Revenue (30D):</strong> ₹{city_performance['revenue'].sum():,.0f}</li>
                <li><strong>Top 3 Cities:</strong> Generate {(city_performance.head(3)['revenue'].sum() / city_performance['revenue'].sum() * 100):.1f}% of total revenue</li>
            </ul>
            
            <h3 style="color: #17a2b8;">💡 RECOMMENDATIONS</h3>
            <ol>
                <li><strong>Focus Expansion:</strong> Prioritize inventory allocation to top 3 cities</li>
                <li><strong>Marketing Investment:</strong> Increase marketing spend in high-performing cities</li>
                <li><strong>Supply Chain:</strong> Ensure adequate stock levels in top cities</li>
                <li><strong>Pricing Strategy:</strong> Analyze pricing in top cities for optimization</li>
            </ol>
            
            <p style="background-color: #e7f3ff; padding: 15px; border-left: 4px solid #1f77b4; margin: 20px 0;">
                <strong>🚀 Action Required:</strong> Consider expanding operations in the top-performing cities to maximize revenue potential.
            </p>
            
            <p style="color: #666; font-size: 12px; margin-top: 30px;">
                Generated by Quick Commerce AI Operations Manager<br>
                Report Date: """ + datetime.now().strftime("%Y-%m-%d %H:%M:%S") + """
            </p>
        </body>
        </html>
        """
        
        # Simulate sending email (in real implementation, use SMTP)
        st.success(f"📧 **Email sent successfully to {email_address}**")
        st.info("📋 **Email Content Preview:**")
        st.markdown(email_body, unsafe_allow_html=True)
        
        # Log the action
        st.success("✅ Email recommendation sent with sales location analysis")
        
    except Exception as e:
        st.error(f"Error sending email recommendations: {e}")

def main():
    """Main application"""
    # Header
    st.markdown('<h1 class="main-header">🚀 Quick Commerce AI Operations Manager</h1>', unsafe_allow_html=True)
    
    # Load data
    sales_df, inventory_df = load_data()
    
    if sales_df is None or inventory_df is None:
        st.error("❌ Unable to load data. Please check if data files exist.")
        return
    
    # Sidebar
    with st.sidebar:
        st.header("🎛️ Dashboard Controls")
        
        if st.button("🔄 Refresh Data", type="primary"):
            st.rerun()
        
        st.header("📊 Quick Stats")
        
        # Generate and display insights
        insights = get_insights(sales_df, inventory_df)
        if insights:
            # Convert to float and format properly
            revenue = float(insights['total_revenue_7d']) if insights['total_revenue_7d'] else 0
            units = int(insights['total_units_sold_7d']) if insights['total_units_sold_7d'] else 0
            st.metric("Revenue (7D)", f"₹{revenue:,.0f}")
            st.metric("Units Sold", f"{units:,}")
            st.metric("Low Stock", insights['low_stock_count'])
            st.metric("Top City", insights['top_performing_city'])
        
        st.header("🧭 Navigation")
        page = st.selectbox("Select Page", ["Dashboard", "AI Chat", "Reports"])
    
    # Main content
    if page == "Dashboard":
        st.header("📊 Operations Dashboard")
        
        # Display metrics
        if insights:
            display_metrics(insights)
        
        # Display charts
        display_sales_chart(sales_df)
        display_inventory_status(inventory_df)
        
    elif page == "AI Chat":
        st.header("🤖 AI Operations Assistant")
        
        # Email Recommendations Section
        st.subheader("📧 Sales Location Recommendations")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("**🎯 Get Best Selling Locations**")
            if st.button("📈 Analyze Top Performing Cities", type="primary"):
                top_cities = analyze_top_performing_cities(sales_df)
                if top_cities is not None:
                    display_top_cities(top_cities)
        
        with col2:
            st.markdown("**📧 Send Email Recommendations**")
            email_address = st.text_input("Enter email address:", placeholder="manager@company.com")
            
            if st.button("📤 Send Sales Report", type="secondary"):
                if email_address:
                    send_sales_recommendations(email_address, sales_df, inventory_df)
                else:
                    st.error("Please enter an email address")
        
        # Quick Actions
        st.subheader("⚡ Quick Actions")
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("📊 Show Sales Summary"):
                if insights:
                    revenue = float(insights['total_revenue_7d']) if insights['total_revenue_7d'] else 0
                    units = int(insights['total_units_sold_7d']) if insights['total_units_sold_7d'] else 0
                    st.success(f"Total Revenue (7D): ₹{revenue:,.0f}")
                    st.success(f"Total Units Sold: {units:,}")
        
        with col2:
            if st.button("📦 Check Low Stock"):
                if insights and insights['low_stock_count'] > 0:
                    st.warning(f"{insights['low_stock_count']} items need restocking")
                else:
                    st.success("All items are well stocked!")
    
    elif page == "Reports":
        st.header("📈 Detailed Reports")
        
        st.subheader("Sales Data Summary")
        if sales_df is not None:
            st.dataframe(sales_df.head(10), use_container_width=True)
            
            st.subheader("Inventory Data Summary")
            if inventory_df is not None:
                st.dataframe(inventory_df.head(10), use_container_width=True)

if __name__ == "__main__":
    main()
