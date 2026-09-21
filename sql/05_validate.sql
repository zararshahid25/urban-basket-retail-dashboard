SET search_path=retail,public;
DO $$ BEGIN
 ASSERT (SELECT count(*) FROM raw_orders)=9004,'Raw order count';
 ASSERT (SELECT count(*) FROM orders)=9000,'Clean order count';
 ASSERT (SELECT count(*) FROM order_items)=20124,'Accepted item count';
 ASSERT (SELECT count(*) FROM raw_items WHERE quantity NOT BETWEEN 1 AND 20)=6,'Quantity exceptions';
 ASSERT (SELECT count(*) FROM data_issues WHERE issue='Duplicate order ID')=4,'Duplicate orders';
 ASSERT (SELECT count(*) FROM sales_enriched)=(SELECT count(*) FROM order_items),'Join multiplication or loss';
 ASSERT NOT EXISTS(SELECT 1 FROM sales_enriched WHERE order_status='Cancelled' AND (net_revenue<>0 OR gross_profit<>0 OR net_units<>0)),'Cancelled contribution';
 ASSERT NOT EXISTS(SELECT 1 FROM order_items WHERE line_revenue<>round(quantity*unit_price*(1-discount_pct/100),2)),'Revenue arithmetic';
 ASSERT round(1.005::numeric,2)=1.01,'Decimal half-away rounding';
 ASSERT (SELECT count(*) FROM dim_date)=731,'Complete calendar including leap day';
 ASSERT NOT EXISTS(SELECT 1 FROM orders o LEFT JOIN dim_date d ON d.date=o.order_date WHERE d.date IS NULL),'Calendar coverage';
END $$;
CREATE TEMP TABLE expected AS SELECT * FROM sales_enriched WITH NO DATA;
\copy expected FROM 'data/reference/sales_enriched.csv' WITH(FORMAT csv,HEADER true)
DO $$ BEGIN
 ASSERT NOT EXISTS((SELECT * FROM expected EXCEPT ALL SELECT * FROM sales_enriched)
 UNION ALL (SELECT * FROM sales_enriched EXCEPT ALL SELECT * FROM expected)),'Full-row reconciliation failed';
 ASSERT (SELECT count(DISTINCT order_id) FROM sales_enriched)=9000,'Orders without reportable items';
END $$;
SELECT 'PASS: counts, all enriched rows, signed activity and decimal arithmetic' AS validation;
SELECT * FROM kpi_summary;
