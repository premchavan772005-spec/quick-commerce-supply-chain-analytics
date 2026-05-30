USE supply_chain_db;

-- Create an operational database view that mimics a live purchase trigger system
CREATE OR REPLACE VIEW view_inventory_deficit_alerts AS
SELECT 
    category_name,
    avg_daily_demand,
    calculated_safety_stock,
    reorder_point_threshold,
    current_warehouse_est_stock,
    forecasted_14day_demand,
    -- Step 1: Calculate the exact deficit quantity
    ROUND(reorder_point_threshold - current_warehouse_est_stock, 2) AS stock_deficit_qty,
    -- Step 2: Set an automated urgency status flag using conditional logic
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

-- Execute the view to see your live quick-commerce alerting grid
SELECT * FROM view_inventory_deficit_alerts;