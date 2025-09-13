"""
Sample data generator for EQREV Hackathon - Agentic AI for Quick Commerce
Creates realistic sample data for sales and inventory
"""
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import random
import json

class DataGenerator:
    def __init__(self):
        self.cities = ['Mumbai', 'Delhi', 'Bangalore', 'Chennai', 'Kolkata', 'Hyderabad', 'Pune', 'Ahmedabad']
        self.products = [
            'Smartphone', 'Laptop', 'Headphones', 'Tablet', 'Smart Watch',
            'Power Bank', 'Bluetooth Speaker', 'Gaming Mouse', 'Keyboard', 'Monitor',
            'Webcam', 'Microphone', 'Router', 'Charger', 'Cable'
        ]
        self.categories = ['Electronics', 'Computers', 'Audio', 'Accessories', 'Gaming']
        
    def generate_sales_data(self, days=30) -> pd.DataFrame:
        """Generate realistic sales data"""
        sales_data = []
        base_date = datetime.now() - timedelta(days=days)
        
        for day in range(days):
            current_date = base_date + timedelta(days=day)
            
            for city in self.cities:
                for product in self.products:
                    # Base sales with some randomness and trends
                    base_sales = random.randint(5, 50)
                    
                    # Weekend effect
                    if current_date.weekday() >= 5:  # Weekend
                        base_sales = int(base_sales * 0.8)
                    
                    # City-specific multipliers
                    city_multiplier = {
                        'Mumbai': 1.3, 'Delhi': 1.2, 'Bangalore': 1.1, 'Chennai': 1.0,
                        'Kolkata': 0.9, 'Hyderabad': 0.95, 'Pune': 0.85, 'Ahmedabad': 0.8
                    }
                    
                    # Product-specific multipliers
                    product_multiplier = {
                        'Smartphone': 1.5, 'Laptop': 1.2, 'Headphones': 1.1, 'Tablet': 1.0,
                        'Smart Watch': 1.3, 'Power Bank': 0.9, 'Bluetooth Speaker': 0.8,
                        'Gaming Mouse': 0.7, 'Keyboard': 0.6, 'Monitor': 0.8
                    }
                    
                    final_sales = int(base_sales * city_multiplier.get(city, 1.0) * 
                                    product_multiplier.get(product, 1.0))
                    
                    # Add some noise
                    final_sales = max(0, final_sales + random.randint(-3, 5))
                    
                    sales_data.append({
                        'date': current_date.strftime('%Y-%m-%d'),
                        'city': city,
                        'product': product,
                        'category': random.choice(self.categories),
                        'units_sold': final_sales,
                        'revenue': final_sales * random.uniform(1000, 50000),  # Price range
                        'avg_order_value': random.uniform(1500, 2500)
                    })
        
        df = pd.DataFrame(sales_data)
        df['date'] = pd.to_datetime(df['date'])
        return df
    
    def generate_inventory_data(self) -> pd.DataFrame:
        """Generate current inventory data"""
        inventory_data = []
        
        for city in self.cities:
            for product in self.products:
                # Base stock with city and product variations
                base_stock = random.randint(50, 500)
                
                # City-specific stock levels
                city_stock_multiplier = {
                    'Mumbai': 1.2, 'Delhi': 1.1, 'Bangalore': 1.0, 'Chennai': 0.9,
                    'Kolkata': 0.8, 'Hyderabad': 0.85, 'Pune': 0.75, 'Ahmedabad': 0.7
                }
                
                # Product-specific stock levels
                product_stock_multiplier = {
                    'Smartphone': 1.3, 'Laptop': 0.8, 'Headphones': 1.5, 'Tablet': 1.0,
                    'Smart Watch': 1.2, 'Power Bank': 1.4, 'Bluetooth Speaker': 1.1,
                    'Gaming Mouse': 1.3, 'Keyboard': 1.2, 'Monitor': 0.9
                }
                
                current_stock = int(base_stock * city_stock_multiplier.get(city, 1.0) * 
                                  product_stock_multiplier.get(product, 1.0))
                
                # Add some stock variations (some items might be low)
                if random.random() < 0.1:  # 10% chance of low stock
                    current_stock = random.randint(5, 20)
                
                # Calculate reorder level (typically 20-30% of max capacity)
                max_capacity = current_stock * random.uniform(3, 5)
                reorder_level = int(max_capacity * 0.25)
                
                inventory_data.append({
                    'city': city,
                    'product': product,
                    'category': random.choice(self.categories),
                    'current_stock': current_stock,
                    'max_capacity': int(max_capacity),
                    'reorder_level': reorder_level,
                    'cost_per_unit': random.uniform(500, 30000),
                    'supplier': f'Supplier_{random.randint(1, 5)}',
                    'lead_time_days': random.randint(2, 7),
                    'last_restocked': (datetime.now() - timedelta(days=random.randint(1, 15))).strftime('%Y-%m-%d')
                })
        
        df = pd.DataFrame(inventory_data)
        return df
    
    def generate_all_data(self):
        """Generate and save all sample data"""
        print("Generating sales data...")
        sales_df = self.generate_sales_data()
        
        print("Generating inventory data...")
        inventory_df = self.generate_inventory_data()
        
        # Save to CSV files
        sales_df.to_csv('data/sales_data.csv', index=False)
        inventory_df.to_csv('data/inventory_data.csv', index=False)
        
        print(f"Sales data: {sales_df.shape}")
        print(f"Inventory data: {inventory_df.shape}")
        
        # Create data summary
        summary = {
            'sales': {
                'total_records': len(sales_df),
                'date_range': f"{sales_df['date'].min()} to {sales_df['date'].max()}",
                'cities': sales_df['city'].nunique(),
                'products': sales_df['product'].nunique(),
                'total_units_sold': sales_df['units_sold'].sum(),
                'total_revenue': sales_df['revenue'].sum()
            },
            'inventory': {
                'total_records': len(inventory_df),
                'cities': inventory_df['city'].nunique(),
                'products': inventory_df['product'].nunique(),
                'total_current_stock': inventory_df['current_stock'].sum(),
                'low_stock_items': len(inventory_df[inventory_df['current_stock'] <= inventory_df['reorder_level']])
            }
        }
        
        with open('data/data_summary.json', 'w') as f:
            json.dump(summary, f, indent=2, default=str)
        
        print("Sample data generated successfully!")
        return sales_df, inventory_df

if __name__ == "__main__":
    import os
    os.makedirs('data', exist_ok=True)
    
    generator = DataGenerator()
    sales_df, inventory_df = generator.generate_all_data()
    
    print("\nSales data sample:")
    print(sales_df.head())
    print("\nInventory data sample:")
    print(inventory_df.head())
