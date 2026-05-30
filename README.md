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
