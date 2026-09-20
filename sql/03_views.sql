CREATE OR REPLACE VIEW vw_sales_enriched AS
SELECT
    o.order_id,
    o.order_date,
    DATE_TRUNC('month', o.order_date)::date AS order_month,
    o.order_status,
    o.sales_channel,
    o.shipping_city,
    o.courier_name,
    o.payment_method,
    o.promo_code,
    c.customer_id,
    c.customer_segment,
    p.product_id,
    p.product_name,
    p.brand,
    cat.category_name,
    oi.quantity,
    oi.unit_price,
    oi.discount_pct,
    oi.line_revenue,
    oi.line_cost,
    CASE o.order_status
        WHEN 'Completed' THEN oi.line_revenue
        WHEN 'Returned' THEN -oi.line_revenue
        ELSE 0
    END AS net_revenue,
    CASE o.order_status
        WHEN 'Completed' THEN oi.line_revenue - oi.line_cost
        WHEN 'Returned' THEN -(oi.line_revenue - oi.line_cost)
        ELSE 0
    END AS gross_profit,
    CASE o.order_status
        WHEN 'Completed' THEN oi.quantity
        WHEN 'Returned' THEN -oi.quantity
        ELSE 0
    END AS net_units
FROM order_items oi
JOIN orders o ON o.order_id = oi.order_id
JOIN customers c ON c.customer_id = o.customer_id
JOIN products p ON p.product_id = oi.product_id
JOIN categories cat ON cat.category_id = p.category_id;

CREATE OR REPLACE VIEW vw_monthly_sales AS
SELECT
    order_month,
    ROUND(SUM(net_revenue), 2) AS net_revenue,
    ROUND(SUM(gross_profit), 2) AS gross_profit,
    SUM(net_units) AS net_units,
    COUNT(DISTINCT order_id) AS orders
FROM vw_sales_enriched
GROUP BY order_month;

