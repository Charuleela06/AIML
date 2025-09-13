"""
Use specific Excel files for Sales and Inventory data
Converts Excel files to CSV format for the Streamlit app
"""
import pandas as pd
import os
from datetime import datetime

def convert_excel_to_csv():
    """Convert specific Excel files to CSV format"""
    print("🚀 Converting specific Excel files to CSV format")
    print("=" * 50)
    
    # File paths
    sales_excel = "data/results-20250913-100155.xlsx"
    inventory_excel = "data/results-20250913-100342.xlsx"
    
    sales_csv = "data/sales_data.csv"
    inventory_csv = "data/inventory_data.csv"
    
    # Create data directory if it doesn't exist
    os.makedirs('data', exist_ok=True)
    
    # Convert Sales Data
    print(f"\n📊 Converting Sales Data: {sales_excel}")
    try:
        if os.path.exists(sales_excel):
            # Read Excel file
            sales_df = pd.read_excel(sales_excel)
            print(f"✅ Loaded sales data: {len(sales_df)} rows, {len(sales_df.columns)} columns")
            print(f"   Columns: {list(sales_df.columns)}")
            
            # Display sample data
            print(f"   Sample data:")
            print(sales_df.head(3))
            
            # Save as CSV
            sales_df.to_csv(sales_csv, index=False)
            print(f"✅ Saved sales data to: {sales_csv}")
            
            # Create backup
            backup_file = f'data/sales_data_backup_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv'
            sales_df.to_csv(backup_file, index=False)
            print(f"✅ Created backup: {backup_file}")
            
        else:
            print(f"❌ Sales Excel file not found: {sales_excel}")
            
    except Exception as e:
        print(f"❌ Error processing sales data: {e}")
    
    # Convert Inventory Data
    print(f"\n📦 Converting Inventory Data: {inventory_excel}")
    try:
        if os.path.exists(inventory_excel):
            # Read Excel file
            inventory_df = pd.read_excel(inventory_excel)
            print(f"✅ Loaded inventory data: {len(inventory_df)} rows, {len(inventory_df.columns)} columns")
            print(f"   Columns: {list(inventory_df.columns)}")
            
            # Display sample data
            print(f"   Sample data:")
            print(inventory_df.head(3))
            
            # Save as CSV
            inventory_df.to_csv(inventory_csv, index=False)
            print(f"✅ Saved inventory data to: {inventory_csv}")
            
            # Create backup
            backup_file = f'data/inventory_data_backup_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv'
            inventory_df.to_csv(backup_file, index=False)
            print(f"✅ Created backup: {backup_file}")
            
        else:
            print(f"❌ Inventory Excel file not found: {inventory_excel}")
            
    except Exception as e:
        print(f"❌ Error processing inventory data: {e}")
    
    print("\n" + "=" * 50)
    print("🎉 Data conversion completed!")
    print("🔄 Restart your Streamlit app to see the updated data!")
    
    return True

if __name__ == "__main__":
    convert_excel_to_csv()
