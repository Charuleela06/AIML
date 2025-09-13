"""
Download real data from Google Sheets for EQREV Hackathon
Using proper Google Sheets CSV export URLs
"""
import pandas as pd
import os
import sys
from datetime import datetime
import requests
from io import StringIO
import urllib.parse

def download_google_sheet_csv(sheet_id, sheet_name="Sheet1"):
    """Download Google Sheet data as CSV using different URL formats"""
    try:
        # Try multiple URL formats
        urls = [
            f"https://docs.google.com/spreadsheets/d/{sheet_id}/export?format=csv&gid=0",
            f"https://docs.google.com/spreadsheets/d/{sheet_id}/export?format=csv",
            f"https://docs.google.com/spreadsheets/d/{sheet_id}/gviz/tq?tqx=out:csv&gid=0",
            f"https://docs.google.com/spreadsheets/d/{sheet_id}/gviz/tq?tqx=out:csv"
        ]
        
        for i, url in enumerate(urls):
            try:
                print(f"Trying URL format {i+1}: {url}")
                response = requests.get(url, timeout=30)
                response.raise_for_status()
                
                # Check if we got valid CSV data
                if response.text.strip() and 'csv' in response.headers.get('content-type', '').lower():
                    df = pd.read_csv(StringIO(response.text))
                    print(f"✅ Downloaded {sheet_name} using URL format {i+1}: {len(df)} rows, {len(df.columns)} columns")
                    return df
                else:
                    print(f"❌ URL format {i+1} returned invalid data")
                    
            except Exception as e:
                print(f"❌ URL format {i+1} failed: {e}")
                continue
        
        print(f"❌ All URL formats failed for {sheet_name}")
        return None
        
    except Exception as e:
        print(f"❌ Error downloading {sheet_name}: {e}")
        return None

def create_sample_data_from_structure():
    """Create sample data that matches the expected structure"""
    print("\n📝 Creating sample data based on Google Sheets structure...")
    
    # Sample sales data
    cities = ['Mumbai', 'Delhi', 'Bangalore', 'Chennai', 'Kolkata', 'Hyderabad', 'Pune', 'Ahmedabad']
    products = ['Smartphone', 'Laptop', 'Tablet', 'Headphones', 'Keyboard', 'Mouse', 'Monitor', 'Power Bank']
    categories = ['Electronics', 'Gaming', 'Accessories', 'Computing']
    
    # Generate sales data
    sales_data = []
    for i in range(1000):  # Generate 1000 records
        date = datetime.now() - pd.Timedelta(days=i % 30)  # Last 30 days
        city = cities[i % len(cities)]
        product = products[i % len(products)]
        category = categories[i % len(categories)]
        units_sold = (i % 50) + 1
        revenue = units_sold * (1000 + (i % 5000))
        avg_order_value = revenue / units_sold
        
        sales_data.append({
            'date': date,
            'city': city,
            'product': product,
            'category': category,
            'units_sold': units_sold,
            'revenue': revenue,
            'avg_order_value': avg_order_value
        })
    
    sales_df = pd.DataFrame(sales_data)
    
    # Generate inventory data
    inventory_data = []
    for i, city in enumerate(cities):
        for j, product in enumerate(products):
            current_stock = (i * j + 10) % 500 + 50
            max_capacity = current_stock * 3
            reorder_level = current_stock * 0.3
            cost_per_unit = 500 + (i * j * 10)
            supplier = f"Supplier_{(i + j) % 5 + 1}"
            lead_time_days = (i + j) % 7 + 1
            last_restocked = datetime.now() - pd.Timedelta(days=(i + j) % 10)
            
            inventory_data.append({
                'city': city,
                'product': product,
                'category': categories[j % len(categories)],
                'current_stock': current_stock,
                'max_capacity': max_capacity,
                'reorder_level': reorder_level,
                'cost_per_unit': cost_per_unit,
                'supplier': supplier,
                'lead_time_days': lead_time_days,
                'last_restocked': last_restocked
            })
    
    inventory_df = pd.DataFrame(inventory_data)
    
    print(f"✅ Created sample sales data: {len(sales_df)} records")
    print(f"✅ Created sample inventory data: {len(inventory_df)} records")
    
    return sales_df, inventory_df

def process_sales_data(df):
    """Process and clean sales data"""
    print("\n📊 Processing Sales Data...")
    
    # Display column info
    print(f"Columns: {list(df.columns)}")
    print(f"Sample data:")
    print(df.head(3))
    
    # Check if we need to rename columns
    column_mapping = {}
    
    # Map Google Sheets columns to our expected format
    if 'date' in df.columns:
        column_mapping['date'] = 'date'
    if 'city_name' in df.columns:
        column_mapping['city_name'] = 'city'
    if 'product_name' in df.columns:
        column_mapping['product_name'] = 'product'
    if 'category' in df.columns:
        column_mapping['category'] = 'category'
    if 'units_sold' in df.columns:
        column_mapping['units_sold'] = 'units_sold'
    if 'gross_selling_value' in df.columns:
        column_mapping['gross_selling_value'] = 'revenue'
    if 'selling_price' in df.columns:
        column_mapping['selling_price'] = 'avg_order_value'
    
    # Fallback to common column name variations
    if 'Date' in df.columns:
        column_mapping['Date'] = 'date'
    if 'City' in df.columns:
        column_mapping['City'] = 'city'
    if 'Product' in df.columns:
        column_mapping['Product'] = 'product'
    if 'Category' in df.columns:
        column_mapping['Category'] = 'category'
    if 'Units Sold' in df.columns or 'Units_Sold' in df.columns:
        units_col = 'Units Sold' if 'Units Sold' in df.columns else 'Units_Sold'
        column_mapping[units_col] = 'units_sold'
    if 'Revenue' in df.columns:
        column_mapping['Revenue'] = 'revenue'
    if 'Average Order Value' in df.columns or 'Avg_Order_Value' in df.columns:
        avg_col = 'Average Order Value' if 'Average Order Value' in df.columns else 'Avg_Order_Value'
        column_mapping[avg_col] = 'avg_order_value'
    
    # Apply column mapping
    if column_mapping:
        df = df.rename(columns=column_mapping)
        print(f"✅ Renamed columns: {column_mapping}")
    
    # Ensure date column is datetime
    if 'date' in df.columns:
        df['date'] = pd.to_datetime(df['date'])
        print(f"✅ Converted date column to datetime")
    
    # Fill missing values
    df = df.fillna(0)
    
    print(f"✅ Processed sales data: {len(df)} records")
    return df

def process_inventory_data(df):
    """Process and clean inventory data"""
    print("\n📦 Processing Inventory Data...")
    
    # Display column info
    print(f"Columns: {list(df.columns)}")
    print(f"Sample data:")
    print(df.head(3))
    
    # Check if we need to rename columns
    column_mapping = {}
    
    # Map Google Sheets columns to our expected format
    if 'city_name' in df.columns:
        column_mapping['city_name'] = 'city'
    if 'product_name' in df.columns:
        column_mapping['product_name'] = 'product'
    if 'category' in df.columns:
        column_mapping['category'] = 'category'
    if 'stock_quantity' in df.columns:
        column_mapping['stock_quantity'] = 'current_stock'
    if 'store_name' in df.columns:
        column_mapping['store_name'] = 'supplier'
    
    # Fallback to common column name variations
    if 'City' in df.columns:
        column_mapping['City'] = 'city'
    if 'Product' in df.columns:
        column_mapping['Product'] = 'product'
    if 'Category' in df.columns:
        column_mapping['Category'] = 'category'
    if 'Current Stock' in df.columns or 'Current_Stock' in df.columns:
        stock_col = 'Current Stock' if 'Current Stock' in df.columns else 'Current_Stock'
        column_mapping[stock_col] = 'current_stock'
    if 'Max Capacity' in df.columns or 'Max_Capacity' in df.columns:
        capacity_col = 'Max Capacity' if 'Max Capacity' in df.columns else 'Max_Capacity'
        column_mapping[capacity_col] = 'max_capacity'
    if 'Reorder Level' in df.columns or 'Reorder_Level' in df.columns:
        reorder_col = 'Reorder Level' if 'Reorder Level' in df.columns else 'Reorder_Level'
        column_mapping[reorder_col] = 'reorder_level'
    if 'Cost Per Unit' in df.columns or 'Cost_Per_Unit' in df.columns:
        cost_col = 'Cost Per Unit' if 'Cost Per Unit' in df.columns else 'Cost_Per_Unit'
        column_mapping[cost_col] = 'cost_per_unit'
    if 'Supplier' in df.columns:
        column_mapping['Supplier'] = 'supplier'
    if 'Lead Time Days' in df.columns or 'Lead_Time_Days' in df.columns:
        lead_col = 'Lead Time Days' if 'Lead Time Days' in df.columns else 'Lead_Time_Days'
        column_mapping[lead_col] = 'lead_time_days'
    if 'Last Restocked' in df.columns or 'Last_Restocked' in df.columns:
        restock_col = 'Last Restocked' if 'Last Restocked' in df.columns else 'Last_Restocked'
        column_mapping[restock_col] = 'last_restocked'
    
    # Apply column mapping
    if column_mapping:
        df = df.rename(columns=column_mapping)
        print(f"✅ Renamed columns: {column_mapping}")
    
    # Ensure date column is datetime
    if 'last_restocked' in df.columns:
        df['last_restocked'] = pd.to_datetime(df['last_restocked'])
        print(f"✅ Converted last_restocked column to datetime")
    
    # Fill missing values
    df = df.fillna(0)
    
    # Ensure numeric columns are numeric
    numeric_cols = ['current_stock', 'max_capacity', 'reorder_level', 'cost_per_unit', 'lead_time_days']
    for col in numeric_cols:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)
    
    print(f"✅ Processed inventory data: {len(df)} records")
    return df

def main():
    """Main function to download and process real data"""
    print("🚀 EQREV Hackathon - Real Data Integration (V2)")
    print("=" * 55)
    
    # Google Sheets IDs
    sales_sheet_id = "1rfFmpCVXs8N9Uc67pTEtYXP5OF0bc8qLhBiOLyUXGGA"
    inventory_sheet_id = "1kkHoYSV4dHmS2YOz2ki8KG0BJxP0Ywy48mrKXoTwSP8"
    
    # Create data directory if it doesn't exist
    os.makedirs('data', exist_ok=True)
    
    # Download Sales Data
    print("\n📊 Downloading Sales Data...")
    sales_df = download_google_sheet_csv(sales_sheet_id, "Sales Data")
    
    # Download Inventory Data
    print("\n📦 Downloading Inventory Data...")
    inventory_df = download_google_sheet_csv(inventory_sheet_id, "Inventory Data")
    
    # If downloads failed, create sample data
    if sales_df is None or inventory_df is None:
        print("\n⚠️  Google Sheets download failed. Creating sample data...")
        sales_df, inventory_df = create_sample_data_from_structure()
    
    # Process the data
    if sales_df is not None:
        sales_df = process_sales_data(sales_df)
        
        # Save processed data
        sales_file = 'data/sales_data.csv'
        sales_df.to_csv(sales_file, index=False)
        print(f"✅ Saved sales data to: {sales_file}")
        
        # Create backup
        backup_file = f'data/sales_data_backup_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv'
        sales_df.to_csv(backup_file, index=False)
        print(f"✅ Created backup: {backup_file}")
    
    if inventory_df is not None:
        inventory_df = process_inventory_data(inventory_df)
        
        # Save processed data
        inventory_file = 'data/inventory_data.csv'
        inventory_df.to_csv(inventory_file, index=False)
        print(f"✅ Saved inventory data to: {inventory_file}")
        
        # Create backup
        backup_file = f'data/inventory_data_backup_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv'
        inventory_df.to_csv(backup_file, index=False)
        print(f"✅ Created backup: {backup_file}")
    
    # Summary
    print("\n" + "=" * 55)
    print("📋 Data Integration Summary:")
    
    if sales_df is not None:
        print(f"✅ Sales Data: {len(sales_df)} records")
        print(f"   Columns: {list(sales_df.columns)}")
        print(f"   Date Range: {sales_df['date'].min()} to {sales_df['date'].max()}")
        if 'city' in sales_df.columns:
            print(f"   Cities: {sales_df['city'].nunique()} unique cities")
        if 'product' in sales_df.columns:
            print(f"   Products: {sales_df['product'].nunique()} unique products")
    
    if inventory_df is not None:
        print(f"✅ Inventory Data: {len(inventory_df)} records")
        print(f"   Columns: {list(inventory_df.columns)}")
        if 'city' in inventory_df.columns:
            print(f"   Cities: {inventory_df['city'].nunique()} unique cities")
        if 'product' in inventory_df.columns:
            print(f"   Products: {inventory_df['product'].nunique()} unique products")
        if 'supplier' in inventory_df.columns:
            print(f"   Suppliers: {inventory_df['supplier'].nunique()} unique suppliers")
    
    print("\n🎉 Data integration completed!")
    print("🔄 Restart your Streamlit app to see the updated data!")
    
    return sales_df, inventory_df

if __name__ == "__main__":
    main()
