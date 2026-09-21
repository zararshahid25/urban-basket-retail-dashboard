SET search_path=retail,public;
CREATE OR REPLACE VIEW sales_enriched AS
 SELECT i.order_item_id,o.order_id,o.order_date,date_trunc('month',o.order_date)::date AS order_month,
 o.customer_id,p.product_id,o.order_status,o.sales_channel,o.shipping_city,c.customer_segment,
 p.product_name,k.category_name,i.quantity,i.unit_price,i.discount_pct,p.unit_cost,i.line_revenue,i.line_cost,
 i.line_revenue*(CASE o.order_status WHEN 'Completed' THEN 1 WHEN 'Returned' THEN -1 ELSE 0 END) AS net_revenue,
 (i.line_revenue-i.line_cost)*(CASE o.order_status WHEN 'Completed' THEN 1 WHEN 'Returned' THEN -1 ELSE 0 END) AS gross_profit,
 i.quantity*(CASE o.order_status WHEN 'Completed' THEN 1 WHEN 'Returned' THEN -1 ELSE 0 END) AS net_units
 FROM order_items i JOIN orders o USING(order_id) JOIN products p USING(product_id)
 JOIN categories k USING(category_id) JOIN customers c ON c.customer_id=o.customer_id;
CREATE OR REPLACE VIEW dim_products AS SELECT p.*,c.category_name FROM products p JOIN categories c USING(category_id);
CREATE OR REPLACE VIEW dim_date AS
 SELECT d::date AS date,date_trunc('month',d)::date AS month,to_char(d,'YYYY-MM') AS year_month,
 extract(month FROM d)::integer AS month_number,extract(year FROM d)::integer AS year
 FROM generate_series('2024-01-01'::date,'2025-12-31'::date,'1 day') d;
CREATE OR REPLACE VIEW kpi_summary AS
 SELECT sum(net_revenue) AS net_revenue,sum(gross_profit) AS gross_profit,
 sum(gross_profit)/nullif(sum(net_revenue),0) AS gross_margin,
 count(DISTINCT order_id) AS orders,
 sum(line_revenue) FILTER(WHERE order_status='Completed')/nullif(count(DISTINCT order_id) FILTER(WHERE order_status='Completed'),0) AS completed_aov,
 count(DISTINCT order_id) FILTER(WHERE order_status='Returned')::numeric/nullif(count(DISTINCT order_id) FILTER(WHERE order_status IN ('Completed','Returned')),0) AS return_rate
 FROM sales_enriched;
