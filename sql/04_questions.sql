SET search_path=retail,public;
-- 1. Monthly signed sales and gross profit. Snapshot exercise; not a general ledger.
SELECT order_month,sum(net_revenue) AS net_revenue,sum(gross_profit) AS gross_profit FROM sales_enriched GROUP BY order_month ORDER BY order_month;
-- 2. Category contribution and weighted gross margin.
SELECT category_name,sum(net_revenue) AS net_revenue,sum(gross_profit)/nullif(sum(net_revenue),0) AS margin,
 sum(net_revenue)/nullif(sum(sum(net_revenue)) OVER(),0) AS revenue_share FROM sales_enriched GROUP BY category_name ORDER BY net_revenue DESC;
-- 3. Highest-revenue products, retaining ties through rank.
WITH r AS(SELECT product_id,product_name,category_name,sum(net_revenue) AS net_revenue,
 dense_rank() OVER(ORDER BY sum(net_revenue) DESC) AS position FROM sales_enriched GROUP BY product_id,product_name,category_name)
SELECT * FROM r WHERE position<=10 ORDER BY position,product_id;
-- 4. Channel / city opportunities. Orders must be counted distinctly.
SELECT sales_channel,shipping_city,count(DISTINCT order_id) AS orders,sum(net_revenue) AS net_revenue FROM sales_enriched GROUP BY sales_channel,shipping_city ORDER BY net_revenue DESC;
-- 5. Category return rate: multiple lines must not multiply the order denominator.
WITH category_orders AS(SELECT DISTINCT category_name,order_id,order_status FROM sales_enriched WHERE order_status IN('Completed','Returned'))
SELECT category_name,count(*) FILTER(WHERE order_status='Returned') AS returned_orders,count(*) AS eligible_orders,
 count(*) FILTER(WHERE order_status='Returned')::numeric/count(*) AS return_rate FROM category_orders GROUP BY category_name;
-- 6. Completed average order value by customer segment (matching numerator and denominator).
SELECT customer_segment,sum(line_revenue)/count(DISTINCT order_id) AS completed_aov
 FROM sales_enriched WHERE order_status='Completed' GROUP BY customer_segment;
-- 7. Products below the average of products in their category.
WITH p AS(SELECT product_id,product_name,category_name,sum(net_revenue) AS revenue FROM sales_enriched GROUP BY product_id,product_name,category_name)
SELECT * FROM p a WHERE revenue<(SELECT avg(revenue) FROM p b WHERE b.category_name=a.category_name) ORDER BY category_name,revenue;
-- 8. Month-over-month growth; the first period stays unavailable.
WITH m AS(SELECT order_month,sum(net_revenue) AS revenue FROM sales_enriched GROUP BY order_month),
 l AS(SELECT *,lag(revenue) OVER(ORDER BY order_month) AS previous FROM m)
SELECT *, (revenue-previous)/nullif(previous,0) AS growth FROM l ORDER BY order_month;
-- 9. Audit the cleaning actions. Issue rows may overlap; do not sum them as rejected transactions.
SELECT issue,action,count(*) FROM data_issues GROUP BY issue,action ORDER BY issue;
