SET search_path=retail,public;
BEGIN;
TRUNCATE order_items,orders,customers,data_issues;
-- Unknown city keys stop the load rather than silently discarding customers/orders.
DO $$ BEGIN
 ASSERT NOT EXISTS(SELECT 1 FROM raw_customers c LEFT JOIN city_mapping m ON lower(trim(c.city))=m.source_city WHERE m.source_city IS NULL),'Unmapped customer city';
 ASSERT NOT EXISTS(SELECT 1 FROM raw_orders o LEFT JOIN city_mapping m ON lower(trim(o.shipping_city))=m.source_city WHERE m.source_city IS NULL),'Unmapped shipping city';
END $$;
INSERT INTO customers SELECT customer_id,customer_segment,m.canonical_city,signup_date
 FROM raw_customers c JOIN city_mapping m ON lower(trim(c.city))=m.source_city;
CREATE TEMP TABLE ranked_orders ON COMMIT DROP AS
 SELECT *,row_number() OVER(PARTITION BY order_id ORDER BY source_row) AS rn FROM raw_orders;
INSERT INTO orders SELECT order_id,customer_id,order_date,order_status,sales_channel,m.canonical_city,courier_name,payment_method,promo_code
 FROM ranked_orders o JOIN city_mapping m ON lower(trim(o.shipping_city))=m.source_city WHERE rn=1;
INSERT INTO data_issues
 SELECT 'order',order_id,'Duplicate order ID','Excluded; first source occurrence retained' FROM ranked_orders WHERE rn>1
 UNION ALL SELECT 'customer',customer_id,'City formatting','Mapped to canonical city' FROM raw_customers c JOIN city_mapping m ON lower(trim(c.city))=m.source_city WHERE c.city<>m.canonical_city
 UNION ALL SELECT 'order',order_id,'Shipping city formatting','Mapped to canonical city' FROM raw_orders o JOIN city_mapping m ON lower(trim(o.shipping_city))=m.source_city WHERE o.shipping_city<>m.canonical_city
 UNION ALL SELECT 'item',order_item_id::text,'Quantity outside scenario range 1-20','Quarantined; retained in raw source' FROM raw_items WHERE quantity NOT BETWEEN 1 AND 20
 UNION ALL SELECT 'item',order_item_id::text,'Line revenue recalculated','Decimal rounding, half away from zero to two places' FROM raw_items
 WHERE quantity BETWEEN 1 AND 20 AND line_revenue<>round(quantity*unit_price*(1-discount_pct/100),2)
 UNION ALL SELECT 'item',i.order_item_id::text,'Line cost recalculated','Quantity multiplied by reference unit cost' FROM raw_items i JOIN products p USING(product_id)
 WHERE quantity BETWEEN 1 AND 20 AND line_cost<>round(quantity*p.unit_cost,2);
INSERT INTO order_items
 SELECT i.order_item_id,i.order_id,i.product_id,i.quantity,i.unit_price,i.discount_pct,
 round(i.quantity*i.unit_price*(1-i.discount_pct/100),2),round(i.quantity*p.unit_cost,2)
 FROM raw_items i JOIN products p USING(product_id) WHERE quantity BETWEEN 1 AND 20;
DO $$ BEGIN
 ASSERT NOT EXISTS(SELECT 1 FROM raw_items i LEFT JOIN products p USING(product_id) WHERE p.product_id IS NULL),'Unknown product';
 ASSERT NOT EXISTS(SELECT 1 FROM orders o LEFT JOIN order_items i USING(order_id) WHERE i.order_id IS NULL),'Order has no valid lines; define reporting treatment before publishing';
END $$;
COMMIT;
