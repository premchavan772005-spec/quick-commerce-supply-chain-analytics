import pandas as pd
from sqlalchemy import create_engine
import sys

def run_supply_chain_etl():
    print(" Starting Project 4 ETL Pipeline Operations...")
    
    # 1. Load the massive raw logistics dataset
    csv_filename = "DataCoSupplyChainDataset.csv"
    try:
        # Using latin-1 encoding because retail datasets often contain special currency/regional characters
        df = pd.read_csv(csv_filename, encoding='latin-1')
        print(f" Successfully ingested {df.shape[0]} rows from source CSV.")
    except FileNotFoundError:
        print(f" Error: Could not find '{csv_filename}' in your project-4 directory.")
        return

    # 2. Extract and rename specific operational columns to match our SQL Schema
    # Mapping data variables for retail optimization metrics
    col_mapping = {
        'Order Id': 'order_id',
        'Order Item Id': 'order_item_id',
        'Customer Id': 'customer_id',
        'Category Name': 'category_name',
        'Product Name': 'product_name',
        'Product Price': 'product_price',
        'Order Item Quantity': 'quantity_ordered',
        'Sales per customer': 'sales_per_order',
        'Order Profit Per Order': 'order_profit',
        'Delivery Status': 'delivery_status',
        'Late_delivery_risk': 'late_delivery_risk',
        'Shipping Mode': 'shipping_mode',
        'order date (DateOrders)': 'order_date',
        'Days for shipping (real)': 'days_for_shipping_real',
        'Days for shipment (scheduled)': 'days_for_shipment_scheduled'
    }
    
    # Keep only the columns we explicitly need for inventory deficit modeling
    available_cols = [col for col in col_mapping.keys() if col in df.columns]
    df_filtered = df[available_cols].rename(columns=col_mapping)
    
    # 3. Clean up date formats and handle missing records
    df_filtered = df_filtered.drop_duplicates(subset=['order_item_id'])
    df_filtered['order_date'] = pd.to_datetime(df_filtered['order_date']).dt.strftime('%Y-%m-%d')
    
    print(f" Data cleaning complete. Structured dataset down to {df_filtered.shape[1]} core operational columns.")

    # 4. Establish streaming pipeline to local MySQL relational warehouse
    try:
        # Creating engine using your standard local instance credentials
        engine = create_engine("mysql+pymysql://root:its_prem7725$67@localhost:3306/supply_chain_db")
        
        print(" Pumping structured records into 'fact_supply_chain_logs' table...")
        df_filtered.to_sql(
            name='fact_supply_chain_logs', 
            con=engine, 
            if_exists='append', 
            index=False, 
            chunksize=5000
        )
        print(" Success! Relational database ingestion layer is completely populated.")
        
    except Exception as e:
        print(f" Database Pipeline Error: {str(e)}")

if __name__ == "__main__":
    run_supply_chain_etl()