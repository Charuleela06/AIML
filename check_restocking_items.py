"""
Quick analysis of inventory data to find top 5 items needing restocking
"""
import pandas as pd
import os

def analyze_restocking_items():
    """Analyze inventory data to find items needing restocking"""
    print("📦 Analyzing Inventory for Restocking Items")
    print("=" * 50)
    
    try:
        # Load inventory data
        inventory_file = 'data/inventory_data.csv'
        if not os.path.exists(inventory_file):
            print(f"❌ Inventory file not found: {inventory_file}")
            return
        
        inventory_df = pd.read_csv(inventory_file)
        print(f"✅ Loaded inventory data: {len(inventory_df)} records")
        
        # Map column names
        column_mapping = {
            'city_name': 'city',
            'product_name': 'product',
            'stock_quantity': 'current_stock',
            'store_name': 'supplier'
        }
        
        for old_col, new_col in column_mapping.items():
            if old_col in inventory_df.columns:
                inventory_df[new_col] = inventory_df[old_col]
        
        # Create reorder level (20% of average stock, minimum 10)
        avg_stock = inventory_df['current_stock'].mean()
        reorder_threshold = max(10, avg_stock * 0.2)
        inventory_df['reorder_level'] = reorder_threshold
        
        # Filter low stock items
        low_stock = inventory_df[inventory_df['current_stock'] < inventory_df['reorder_level']]
        
        print(f"\n📊 Inventory Analysis:")
        print(f"   Total items: {len(inventory_df)}")
        print(f"   Items needing restocking: {len(low_stock)}")
        print(f"   Reorder threshold: {reorder_threshold:.0f} units")
        
        if len(low_stock) > 0:
            # Get top 5 items with lowest stock
            top_5_low_stock = low_stock.nsmallest(5, 'current_stock')
            
            print(f"\n🔴 TOP 5 ITEMS NEEDING RESTOCKING:")
            print("-" * 60)
            
            for i, (idx, row) in enumerate(top_5_low_stock.iterrows(), 1):
                city = row.get('city', 'N/A')
                product = row.get('product', 'N/A')
                current_stock = row.get('current_stock', 0)
                supplier = row.get('supplier', 'N/A')
                
                print(f"{i}. {product}")
                print(f"   📍 City: {city}")
                print(f"   📦 Current Stock: {current_stock} units")
                print(f"   🏪 Supplier: {supplier}")
                print(f"   ⚠️  Status: CRITICAL (below {reorder_threshold:.0f} units)")
                print()
            
            # Summary by city
            print("🌍 RESTOCKING BY CITY:")
            print("-" * 40)
            city_summary = low_stock.groupby('city').agg({
                'product': 'count',
                'current_stock': 'sum'
            }).rename(columns={'product': 'items_needing_restock', 'current_stock': 'total_low_stock'})
            
            city_summary = city_summary.sort_values('items_needing_restock', ascending=False)
            
            for city, row in city_summary.head(10).iterrows():
                print(f"{city}: {row['items_needing_restock']} items, {row['total_low_stock']} total low stock")
            
            # Summary by product
            print(f"\n🏷️  RESTOCKING BY PRODUCT:")
            print("-" * 40)
            product_summary = low_stock.groupby('product').agg({
                'city': 'count',
                'current_stock': 'sum'
            }).rename(columns={'city': 'cities_affected', 'current_stock': 'total_low_stock'})
            
            product_summary = product_summary.sort_values('cities_affected', ascending=False)
            
            for product, row in product_summary.head(10).iterrows():
                print(f"{product}: {row['cities_affected']} cities, {row['total_low_stock']} total low stock")
                
        else:
            print("✅ All items are well stocked!")
            
    except Exception as e:
        print(f"❌ Error analyzing inventory: {e}")

if __name__ == "__main__":
    analyze_restocking_items()
