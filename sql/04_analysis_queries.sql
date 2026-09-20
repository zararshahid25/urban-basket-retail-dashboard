-- 1. Monthly sales and gross profit trend
SELECT
    order_month,
    ROUND(SUM(net_revenue), 2) AS net_revenue,
    ROUND(SUM(gross_profit), 2) AS gross_profit,
    COUNT(DISTINCT order_id) AS orders
FROM vw_sales_enriched
GROUP BY order_month
ORDER BY order_month;

-- 2. Category performance with contribution and margin
SELECT
    category_name,
    ROUND(SUM(net_revenue), 2) AS net_revenue,
    ROUND(SUM(gross_profit), 2) AS gross_profit,
    ROUND(100.0 * SUM(gross_profit) / NULLIF(SUM(net_revenue), 0), 2) AS gross_margin_pct,
    ROUND(100.0 * SUM(net_revenue) / NULLIF(SUM(SUM(net_revenue)) OVER (), 0), 2) AS revenue_share_pct
FROM vw_sales_enriched
GROUP BY category_name
ORDER BY net_revenue DESC;

-- 3. Top products by net revenue
SELECT
    product_id,
    product_name,
    category_name,
    SUM(net_units) AS net_units,
    ROUND(SUM(net_revenue), 2) AS net_revenue,
    ROUND(SUM(gross_profit), 2) AS gross_profit
FROM vw_sales_enriched
GROUP BY product_id, product_name, category_name
HAVING SUM(net_revenue) > 0
ORDER BY net_revenue DESC
LIMIT 15;

-- 4. Sales by city and channel
SELECT
    shipping_city,
    sales_channel,
    COUNT(DISTINCT order_id) AS orders,
    ROUND(SUM(net_revenue), 2) AS net_revenue,
    ROUND(SUM(gross_profit), 2) AS gross_profit
FROM vw_sales_enriched
GROUP BY shipping_city, sales_channel
ORDER BY shipping_city, net_revenue DESC;

-- 5. Return rate by category; rates use order counts, not item percentages
WITH category_orders AS (
    SELECT DISTINCT category_name, order_id, order_status
    FROM vw_sales_enriched
    WHERE order_status IN ('Completed', 'Returned')
)
SELECT
    category_name,
    COUNT(*) FILTER (WHERE order_status = 'Returned') AS returned_orders,
    COUNT(*) AS eligible_orders,
    ROUND(
        100.0 * COUNT(*) FILTER (WHERE order_status = 'Returned') / NULLIF(COUNT(*), 0),
        2
    ) AS return_rate_pct
FROM category_orders
GROUP BY category_name
ORDER BY return_rate_pct DESC;

-- 6. Customer segment summary
SELECT
    customer_segment,
    COUNT(DISTINCT customer_id) AS customers,
    COUNT(DISTINCT order_id) AS orders,
    ROUND(SUM(net_revenue), 2) AS net_revenue,
    ROUND(SUM(net_revenue) / NULLIF(COUNT(DISTINCT order_id), 0), 2) AS revenue_per_order
FROM vw_sales_enriched
GROUP BY customer_segment
ORDER BY net_revenue DESC;

-- 7. Products selling below their category average
WITH product_sales AS (
    SELECT
        category_name,
        product_id,
        product_name,
        SUM(net_revenue) AS product_revenue
    FROM vw_sales_enriched
    GROUP BY category_name, product_id, product_name
), category_benchmark AS (
    SELECT category_name, AVG(product_revenue) AS average_product_revenue
    FROM product_sales
    GROUP BY category_name
)
SELECT
    p.category_name,
    p.product_name,
    ROUND(p.product_revenue, 2) AS product_revenue,
    ROUND(b.average_product_revenue, 2) AS category_average
FROM product_sales p
JOIN category_benchmark b USING (category_name)
WHERE p.product_revenue < b.average_product_revenue
ORDER BY p.category_name, p.product_revenue;

