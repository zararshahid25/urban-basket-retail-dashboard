-- All queries should return zero rows or a zero count after the load.

SELECT order_id, COUNT(*)
FROM orders
GROUP BY order_id
HAVING COUNT(*) > 1;

SELECT order_item_id, quantity
FROM order_items
WHERE quantity NOT BETWEEN 1 AND 20;

SELECT oi.order_item_id
FROM order_items oi
LEFT JOIN orders o ON o.order_id = oi.order_id
WHERE o.order_id IS NULL;

SELECT oi.order_item_id
FROM order_items oi
LEFT JOIN products p ON p.product_id = oi.product_id
WHERE p.product_id IS NULL;

SELECT order_item_id, line_revenue,
       ROUND(quantity * unit_price * (1 - discount_pct / 100.0), 2) AS expected_revenue
FROM order_items
WHERE ABS(line_revenue - ROUND(quantity * unit_price * (1 - discount_pct / 100.0), 2)) > 0.01;

