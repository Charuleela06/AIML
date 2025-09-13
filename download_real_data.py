"""
Download real data from Google Sheets for EQREV Hackathon
Replaces synthetic data with actual competition datasets
"""
import pandas as pd
import os
import sys
from datetime import datetime
import requests
from io import StringIO

def download_google_sheet(sheet_id, sheet_name="Sheet1"):
    """Download Google Sheet data as CSV"""
    try:
        # Convert Google Sheets URL to CSV download URL
        csv_url = f"https://docs.google.com/spreadsheets/d/{sheet_id}/export?format=csv&gid=0"
        
        print(f"Downloading {sheet_name} from Google Sheets...")
        response = requests.get(csv_url)
        response.raise_for_status()
        
        # Read CSV data
        df = pd.read_csv(StringIO(response.text))
        print(f"✅ Downloaded {sheet_name}: {len(df)} rows, {len(df.columns)} columns")
        
        return df
    except Exception as e:
        print(f"❌ Error downloading {sheet_name}: {e}")
        return None

def process_sales_data(df):
    """Process and clean sales data"""
    print("\n📊 Processing Sales Data...")
    
    # Display column info
    print(f"Columns: {list(df.columns)}")
    print(f"Sample data:")
    print(df.head(3))
    
    # Check if we need to rename columns
    column_mapping = {}
    
    # Common column name variations
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
    
    # Common column name variations
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
    print("🚀 EQREV Hackathon - Real Data Integration")
    print("=" * 50)
    
    # Google Sheets IDs
    sales_sheet_id = "1rfFmpCVXs8N9Uc67pTEtYXP5OF0bc8qLhBiOLyUXGGA"
    inventory_sheet_id = "1kkHoYSV4dHmS2YOz2ki8KG0BJxP0Ywy48mrKXoTwSP8"
    
    # Create data directory if it doesn't exist
    os.makedirs('data', exist_ok=True)
    
    # Download Sales Data
    print("\n📊 Downloading Sales Data...")
    sales_df = download_google_sheet(sales_sheet_id, "Sales Data")
    
    if sales_df is not None:
        # Process sales data
        sales_df = process_sales_data(sales_df)
        
        # Save processed data
        sales_file = 'data/sales_data.csv'
        sales_df.to_csv(sales_file, index=False)
        print(f"✅ Saved sales data to: {sales_file}")
        
        # Create backup
        backup_file = f'data/sales_data_backup_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv'
        sales_df.to_csv(backup_file, index=False)
        print(f"✅ Created backup: {backup_file}")
    
    # Download Inventory Data
    print("\n📦 Downloading Inventory Data...")
    inventory_df = download_google_sheet(inventory_sheet_id, "Inventory Data")
    
    if inventory_df is not None:
        # Process inventory data
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
    print("\n" + "=" * 50)
    print("📋 Data Integration Summary:")
    
    if sales_df is not None:
        print(f"✅ Sales Data: {len(sales_df)} records")
        print(f"   Columns: {list(sales_df.columns)}")
        print(f"   Date Range: {sales_df['date'].min()} to {sales_df['date'].max()}")
        print(f"   Cities: {sales_df['city'].nunique()} unique cities")
        print(f"   Products: {sales_df['product'].nunique()} unique products")
    
    if inventory_df is not None:
        print(f"✅ Inventory Data: {len(inventory_df)} records")
        print(f"   Columns: {list(inventory_df.columns)}")
        print(f"   Cities: {inventory_df['city'].nunique()} unique cities")
        print(f"   Products: {inventory_df['product'].nunique()} unique products")
        print(f"   Suppliers: {inventory_df['supplier'].nunique()} unique suppliers")
    
    print("\n🎉 Real data integration completed!")
    print("🔄 Restart your Streamlit app to see the real data in action!")
    
    return sales_df, inventory_df

if __name__ == "__main__":
    main()
