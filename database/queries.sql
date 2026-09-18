-- Highest-risk products
SELECT p.product_name, p.category, mp.risk_score, mp.stockout_probability
FROM model_predictions AS mp
JOIN products AS p USING (product_id)
ORDER BY mp.risk_score DESC
LIMIT 10;

-- Category stockout rates
SELECT p.category, AVG(di.stockout_event) AS stockout_rate
FROM daily_inventory AS di
JOIN products AS p USING (product_id)
GROUP BY p.category
ORDER BY stockout_rate DESC;

-- Warehouse stockout event volume
SELECT warehouse, SUM(stockout_event) AS stockout_events
FROM daily_inventory
GROUP BY warehouse
ORDER BY stockout_events DESC;

-- Products requiring immediate replenishment
SELECT p.product_name, mp.risk_level, mp.units_required, mp.expected_stockout_date
FROM model_predictions AS mp
JOIN products AS p USING (product_id)
WHERE mp.risk_level IN ('HIGH', 'CRITICAL')
ORDER BY mp.risk_score DESC;

-- Average supplier lead time by category
SELECT category, AVG(supplier_lead_time) AS average_lead_time
FROM supplier_information
GROUP BY category
ORDER BY average_lead_time DESC;

