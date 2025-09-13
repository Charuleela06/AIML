"""
Data downloader for EQREV Hackathon - Agentic AI for Quick Commerce
Downloads sales and inventory data from Google Sheets
"""
import pandas as pd
import requests
import os
from typing import Dict, Any
import json

class DataDownloader:
    def __init__(self):
        self.sales_url = "https://docs.google.com/spreadsheets/d/1rfFmpCVXs8N9Uc67pTEtYXP5OF0bc8qLhBiOLyUXGGA/export?format=csv"
        self.inventory_url = "https://docs.google.com/spreadsheets/d/1kkHoYSV4dHmS2YOz2ki8KG0BJxP0Ywy48mrKXoTwSP8/export?format=csv"
    
    def download_sales_data(self) -> pd.DataFrame:
        """Download sales data from Google Sheets"""
        try:
            response = requests.get(self.sales_url)
            response.raise_for_status()
            
            # Save to CSV first
            with open('data/sales_data.csv', 'w', encoding='utf-8') as f:
                f.write(response.text)
            
            # Read into DataFrame
            df = pd.read_csv('data/sales_data.csv')
            print(f"Downloaded sales data: {df.shape}")
            print(f"Columns: {df.columns.tolist()}")
            print(f"First few rows:\n{df.head()}")
            return df
            
        except Exception as e:
            print(f"Error downloading sales data: {e}")
            return pd.DataFrame()
    
    def download_inventory_data(self) -> pd.DataFrame:
        """Download inventory data from Google Sheets"""
        try:
            response = requests.get(self.inventory_url)
            response.raise_for_status()
            
            # Save to CSV first
            with open('data/inventory_data.csv', 'w', encoding='utf-8') as f:
                f.write(response.text)
            
            # Read into DataFrame
            df = pd.read_csv('data/inventory_data.csv')
            print(f"Downloaded inventory data: {df.shape}")
            print(f"Columns: {df.columns.tolist()}")
            print(f"First few rows:\n{df.head()}")
            return df
            
        except Exception as e:
            print(f"Error downloading inventory data: {e}")
            return pd.DataFrame()
    
    def download_all_data(self) -> Dict[str, pd.DataFrame]:
        """Download all data and return as dictionary"""
        data = {}
        
        # Create data directory if it doesn't exist
        os.makedirs('data', exist_ok=True)
        
        # Download sales data
        sales_df = self.download_sales_data()
        if not sales_df.empty:
            data['sales'] = sales_df
        
        # Download inventory data
        inventory_df = self.download_inventory_data()
        if not inventory_df.empty:
            data['inventory'] = inventory_df
        
        return data
    
    def save_data_summary(self, data: Dict[str, pd.DataFrame]):
        """Save data summary for analysis"""
        summary = {}
        
        for key, df in data.items():
            summary[key] = {
                'shape': df.shape,
                'columns': df.columns.tolist(),
                'dtypes': df.dtypes.to_dict(),
                'null_counts': df.isnull().sum().to_dict(),
                'sample_data': df.head(3).to_dict()
            }
        
        with open('data/data_summary.json', 'w') as f:
            json.dump(summary, f, indent=2, default=str)
        
        print("Data summary saved to data/data_summary.json")

if __name__ == "__main__":
    downloader = DataDownloader()
    data = downloader.download_all_data()
    downloader.save_data_summary(data)
