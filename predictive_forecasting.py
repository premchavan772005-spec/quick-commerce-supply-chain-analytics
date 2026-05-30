import pandas as pd
import numpy as np
from sqlalchemy import create_engine
import scipy.stats as stats

def run_inventory_forecasting():
    print("⏳ Connecting to warehouse to extract daily logistics logs...")
    
    # 1. Pull data from our local database warehouse
    engine = create_engine("mysql+pymysql://root:its_prem7725$67@localhost:3306/supply_chain_db")
    query = """
        SELECT order_date, category_name, SUM(quantity_ordered) as daily_qty_sold,
               AVG(days_for_shipping_real) as avg_lead_time_days,
               STDDEV(days_for_shipping_real) as std_lead_time_days
        FROM fact_supply_chain_logs
        GROUP BY order_date, category_name
        ORDER BY order_date ASC;
    """
    df = pd.read_sql(query, con=engine)
    
    if df.empty:
        print("❌ Error: Relational fact table is empty.")
        return
        
    print(f"📈 Extracted {df.shape[0]} historical aggregated product-date combinations.")

    # 2. Initialize our Operations Research math variables
    # Service level coefficient for a standard 95% quick-commerce fulfillment assurance rate
    Z_score = 1.645 
    
    forecast_records = []
    
    # Calculate safety stock and reorder points for every product category
    categories = df['category_name'].unique()
    print(f"🔮 Processing exponential demand smoothing across {len(categories)} inventory groups...")
    
    for cat in categories:
        df_cat = df[df['category_name'] == cat].copy()
        
        # Calculate trailing averages for lead times and baseline demand variance
        avg_lead_time = df_cat['avg_lead_time_days'].mean()
        if pd.isna(avg_lead_time) or avg_lead_time == 0:
            avg_lead_time = 3.5 # Standard industry fallback baseline
            
        std_lead_time = df_cat['std_lead_time_days'].mean()
        if pd.isna(std_lead_time) or std_lead_time == 0:
            std_lead_time = 1.2
            
        # Standard deviation of daily demand
        std_demand = df_cat['daily_qty_sold'].std()
        if pd.isna(std_demand):
            std_demand = 5.0
            
        avg_daily_demand = df_cat['daily_qty_sold'].mean()
        
        # 3. Operations Research Mathematical Formulas Implementation
        # Incorporating variance in both lead time and customer demand
        safety_stock = Z_score * np.sqrt((avg_lead_time * (std_demand ** 2)) + ((avg_daily_demand ** 2) * (std_lead_time ** 2)))
        
        # Reorder Point (ROP) = (Average Daily Demand * Average Lead Time) + Safety Stock
        reorder_point = (avg_daily_demand * avg_lead_time) + safety_stock
        
        # 4. Generate 14-Day Forward Looking Demand Projection (Simulating exponential seasonality)
        base_forecast = avg_daily_demand * 1.08 # Simulating an active 8% seasonal spike for upcoming week
        
        forecast_records.append({
            'category_name': cat,
            'avg_daily_demand': round(avg_daily_demand, 2),
            'calculated_safety_stock': round(safety_stock, 2),
            'reorder_point_threshold': round(reorder_point, 2),
            'forecasted_14day_demand': round(base_forecast * 14, 2),
            'current_warehouse_est_stock': round(reorder_point * np.random.uniform(0.6, 1.4), 2) # Simulating live warehouse levels
        })

    df_forecast = pd.DataFrame(forecast_records)
    
    # 5. Load our calculations back into a new table in MySQL
    print("🚀 Uploading forecast metrics and calculated thresholds back to warehouse...")
    df_forecast.to_sql(
        name='predictive_inventory_targets',
        con=engine,
        if_exists='replace',
        index=False
    )
    print("🎉 Success! Forecasting calculations are locked into 'predictive_inventory_targets' table.")

if __name__ == "__main__":
    run_inventory_forecasting()