"""
Database models for EQREV Hackathon - Agentic AI for Quick Commerce
"""
from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, Boolean, Text, text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import pandas as pd
from datetime import datetime
import os

Base = declarative_base()

class SalesData(Base):
    __tablename__ = 'sales_data'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    date = Column(DateTime, nullable=False)
    city = Column(String(100), nullable=False)
    product = Column(String(100), nullable=False)
    category = Column(String(100), nullable=False)
    units_sold = Column(Integer, nullable=False)
    revenue = Column(Float, nullable=False)
    avg_order_value = Column(Float, nullable=False)

class InventoryData(Base):
    __tablename__ = 'inventory_data'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    city = Column(String(100), nullable=False)
    product = Column(String(100), nullable=False)
    category = Column(String(100), nullable=False)
    current_stock = Column(Integer, nullable=False)
    max_capacity = Column(Integer, nullable=False)
    reorder_level = Column(Integer, nullable=False)
    cost_per_unit = Column(Float, nullable=False)
    supplier = Column(String(100), nullable=False)
    lead_time_days = Column(Integer, nullable=False)
    last_restocked = Column(DateTime, nullable=False)

class ActionLog(Base):
    __tablename__ = 'action_log'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    timestamp = Column(DateTime, default=datetime.utcnow)
    action_type = Column(String(100), nullable=False)  # 'allocation', 'restock', 'alert'
    details = Column(Text, nullable=False)
    status = Column(String(50), default='pending')  # 'pending', 'completed', 'failed'
    n8n_webhook_url = Column(String(500))
    n8n_response = Column(Text)

class DatabaseManager:
    def __init__(self, db_path=None):
        if db_path is None:
            # Try to find the data directory relative to current working directory
            current_dir = os.getcwd()
            if current_dir.endswith('backend'):
                db_path = '../data/quick_commerce.db'
            else:
                db_path = 'data/quick_commerce.db'
        self.db_path = db_path
        self.engine = create_engine(f'sqlite:///{db_path}', echo=False)
        Base.metadata.create_all(self.engine)
        Session = sessionmaker(bind=self.engine)
        self.session = Session()
    
    def load_data_from_csv(self):
        """Load data from CSV files into database"""
        try:
            # Load sales data
            sales_df = pd.read_csv('data/sales_data.csv')
            sales_df['date'] = pd.to_datetime(sales_df['date'])
            
            for _, row in sales_df.iterrows():
                sales_record = SalesData(
                    date=row['date'],
                    city=row['city'],
                    product=row['product'],
                    category=row['category'],
                    units_sold=row['units_sold'],
                    revenue=row['revenue'],
                    avg_order_value=row['avg_order_value']
                )
                self.session.add(sales_record)
            
            # Load inventory data
            inventory_df = pd.read_csv('data/inventory_data.csv')
            inventory_df['last_restocked'] = pd.to_datetime(inventory_df['last_restocked'])
            
            for _, row in inventory_df.iterrows():
                inventory_record = InventoryData(
                    city=row['city'],
                    product=row['product'],
                    category=row['category'],
                    current_stock=row['current_stock'],
                    max_capacity=row['max_capacity'],
                    reorder_level=row['reorder_level'],
                    cost_per_unit=row['cost_per_unit'],
                    supplier=row['supplier'],
                    lead_time_days=row['lead_time_days'],
                    last_restocked=row['last_restocked']
                )
                self.session.add(inventory_record)
            
            self.session.commit()
            print("Data loaded successfully into database")
            
        except Exception as e:
            print(f"Error loading data: {e}")
            self.session.rollback()
    
    def get_sales_analytics(self, days=7):
        """Get sales analytics for the last N days"""
        from datetime import datetime, timedelta
        cutoff_date = datetime.now() - timedelta(days=days)
        
        query = """
        SELECT 
            city,
            product,
            SUM(units_sold) as total_units,
            SUM(revenue) as total_revenue,
            AVG(avg_order_value) as avg_order_value,
            COUNT(*) as days_with_sales
        FROM sales_data 
        WHERE date >= :cutoff_date
        GROUP BY city, product
        ORDER BY total_units DESC
        """
        
        result = self.session.execute(text(query), {"cutoff_date": cutoff_date}).fetchall()
        return pd.DataFrame(result, columns=[
            'city', 'product', 'total_units', 'total_revenue', 
            'avg_order_value', 'days_with_sales'
        ])
    
    def get_inventory_status(self):
        """Get current inventory status"""
        query = """
        SELECT 
            city,
            product,
            current_stock,
            max_capacity,
            reorder_level,
            cost_per_unit,
            supplier,
            lead_time_days,
            last_restocked,
            CASE 
                WHEN current_stock <= reorder_level THEN 'LOW_STOCK'
                WHEN current_stock <= reorder_level * 1.5 THEN 'MEDIUM_STOCK'
                ELSE 'HIGH_STOCK'
            END as stock_status
        FROM inventory_data
        ORDER BY stock_status, current_stock ASC
        """
        
        result = self.session.execute(text(query)).fetchall()
        return pd.DataFrame(result, columns=[
            'city', 'product', 'current_stock', 'max_capacity', 
            'reorder_level', 'cost_per_unit', 'supplier', 
            'lead_time_days', 'last_restocked', 'stock_status'
        ])
    
    def get_low_stock_items(self):
        """Get items that need restocking"""
        query = """
        SELECT *
        FROM inventory_data
        WHERE current_stock <= reorder_level
        ORDER BY current_stock ASC
        """
        
        result = self.session.execute(text(query)).fetchall()
        return pd.DataFrame(result, columns=[
            'id', 'city', 'product', 'category', 'current_stock', 
            'max_capacity', 'reorder_level', 'cost_per_unit', 
            'supplier', 'lead_time_days', 'last_restocked'
        ])
    
    def get_city_performance(self, days=7):
        """Get city performance metrics"""
        from datetime import datetime, timedelta
        cutoff_date = datetime.now() - timedelta(days=days)
        
        query = """
        SELECT 
            city,
            SUM(units_sold) as total_units,
            SUM(revenue) as total_revenue,
            COUNT(DISTINCT product) as products_sold,
            AVG(avg_order_value) as avg_order_value
        FROM sales_data 
        WHERE date >= :cutoff_date
        GROUP BY city
        ORDER BY total_revenue DESC
        """
        
        result = self.session.execute(text(query), {"cutoff_date": cutoff_date}).fetchall()
        return pd.DataFrame(result, columns=[
            'city', 'total_units', 'total_revenue', 
            'products_sold', 'avg_order_value'
        ])
    
    def log_action(self, action_type, details, n8n_webhook_url=None):
        """Log an action for tracking"""
        action_log = ActionLog(
            action_type=action_type,
            details=details,
            n8n_webhook_url=n8n_webhook_url
        )
        self.session.add(action_log)
        self.session.commit()
        return action_log.id
    
    def update_action_status(self, action_id, status, n8n_response=None):
        """Update action status"""
        action = self.session.query(ActionLog).filter(ActionLog.id == action_id).first()
        if action:
            action.status = status
            if n8n_response:
                action.n8n_response = n8n_response
            self.session.commit()
    
    def close(self):
        """Close database connection"""
        self.session.close()

if __name__ == "__main__":
    # Initialize database and load data
    db = DatabaseManager()
    db.load_data_from_csv()
    db.close()
