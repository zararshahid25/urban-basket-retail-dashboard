CREATE SCHEMA IF NOT EXISTS retail;
SET search_path=retail,public;
CREATE TABLE IF NOT EXISTS raw_customers (
 customer_id text,customer_segment text,city text,signup_date date
);
CREATE TABLE IF NOT EXISTS raw_orders (
 source_row bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
 order_id text,customer_id text,order_date date,order_status text,sales_channel text,
 shipping_city text,courier_name text,payment_method text,promo_code text
);
CREATE TABLE IF NOT EXISTS raw_items (
 order_item_id integer,order_id text,product_id integer,quantity integer,unit_price numeric,
 discount_pct numeric,line_revenue numeric,line_cost numeric
);
CREATE TABLE IF NOT EXISTS city_mapping (source_city text PRIMARY KEY,canonical_city text NOT NULL);
INSERT INTO city_mapping VALUES ('isb','Islamabad'),('islamabad','Islamabad'),('rwp','Rawalpindi'),('rawalpindi','Rawalpindi'),
 ('lahore','Lahore'),('karachi','Karachi'),('peshawar','Peshawar'),('faisalabad','Faisalabad')
 ON CONFLICT(source_city) DO UPDATE SET canonical_city=excluded.canonical_city;
CREATE TABLE IF NOT EXISTS data_issues (source_type text,record_id text,issue text,action text);
