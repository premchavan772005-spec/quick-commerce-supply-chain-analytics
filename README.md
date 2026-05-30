# 📦 Quick-Commerce Supply Chain Optimization & Predictive Control Tower

## 📌 Project Overview
An end-to-end Data Engineering and Operations Research pipeline built to optimize quick-commerce logistics fulfillment. The system ingests raw multi-variant supply chain logs into a relational database warehouse, applies advanced exponential demand smoothing to compute dynamically adjusted reorder thresholds, and exposes live operational status anomalies through a professional executive control dashboard.

## 🛠️ Tech Stack & Architecture
* **Ingestion Layer:** Python (`pandas`, `SQLAlchemy`, `PyMySQL`)
* **Data Warehouse Engine:** MySQL Relational Database
* **Analytical Modeling:** Scientific Computing Core (`numpy`, `scipy`)
* **Presentation Layer:** Power BI Desktop Control Tower Dashboard

---

## ⚙️ Core Engineering Pipeline Steps

### 1. Database Initialization (`inventory_automation.sql`)
Sets up the central data repository layers and provisions an automated reporting view utilizing conditional operational status triggers:

```sql
-- Computes real-time stock deficits and flags logistical priorities
CREATE OR REPLACE VIEW view_inventory_deficit_alerts AS
SELECT 
    category_name,
    avg_daily_demand,
    calculated_safety_stock,
    reorder_point_threshold,
    current_warehouse_est_stock,
    forecasted_14day_demand,
    ROUND(reorder_point_threshold - current_warehouse_est_stock, 2) AS stock_deficit_qty,
    CASE 
        WHEN current_warehouse_est_stock < (reorder_point_threshold * 0.5) THEN 'CRITICAL STOCKOUT RISK'
        WHEN current_warehouse_est_stock < reorder_point_threshold THEN 'REORDER TRIGGERED'
        ELSE 'OPTIMAL REORDER WINDOW'
    END AS operational_status    
FROM 
    predictive_inventory_targets
WHERE 
    current_warehouse_est_stock < reorder_point_threshold
ORDER BY 
    stock_deficit_qty DESC;

### 2. ETL Data Ingestion Pipeline (`supply_chain_etl.py`)
Extracts massive raw transactional variables, strips duplicate entries down to distinct tracking parameters, maps business terms to standard database fields, and loads them into the local fact table storage.

### 3. Predictive Demand Engine (`predictive_forecasting.py`)
Pulls historical daily logs to process demand variances and lead times. Implements Operations Research mathematical formulations to establish inventory parameters:
* **Safety Stock Optimization:** Incorporates standard deviations across both consumption rates and supplier fulfillment variables with a 95% service-level target ($Z = 1.645$).
* **Reorder Point (ROP):** Calculated using the formula: $\text{ROP} = (\text{Average Daily Demand} \times \text{Average Lead Time}) + \text{Safety Stock}$

---

## 📊 Business Intelligence & Actionable Insights
The business presentation layer is divided into two operational core areas to deliver maximum value to logistical coordinators:

1. **Inventory Stockout Alerts:** A visual table ranking immediate replenishment necessities based on computed deficits, backed by an amber warning flag system to streamline daily ordering priorities.
2. **Logistics SLA Analysis:** Side-by-side analytical bar charts comparing historical shipping durations against supplier-promised arrival schedules to isolate delivery bottleneck nodes.
