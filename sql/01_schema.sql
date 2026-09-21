CREATE SCHEMA IF NOT EXISTS retail;
SET search_path=retail,public;
BEGIN;

CREATE TABLE IF NOT EXISTS categories (
    category_id       INTEGER PRIMARY KEY,
    category_name     VARCHAR(80) NOT NULL UNIQUE
);

CREATE TABLE IF NOT EXISTS products (
    product_id        INTEGER PRIMARY KEY,
    category_id       INTEGER NOT NULL REFERENCES categories(category_id),
    product_name      VARCHAR(120) NOT NULL,
    brand             VARCHAR(80) NOT NULL,
    unit_cost         NUMERIC(12,2) NOT NULL CHECK (unit_cost >= 0),
    list_price        NUMERIC(12,2) NOT NULL CHECK (list_price >= unit_cost),
    active_flag       BOOLEAN NOT NULL DEFAULT TRUE,
    UNIQUE (product_name, brand)
);

CREATE TABLE IF NOT EXISTS customers (
    customer_id       VARCHAR(12) PRIMARY KEY,
    customer_segment  VARCHAR(40) NOT NULL,
    city              VARCHAR(80) NOT NULL,
    signup_date       DATE NOT NULL
);

CREATE TABLE IF NOT EXISTS orders (
    order_id          VARCHAR(14) PRIMARY KEY,
    customer_id       VARCHAR(12) NOT NULL REFERENCES customers(customer_id),
    order_date        DATE NOT NULL,
    order_status      VARCHAR(20) NOT NULL CHECK (order_status IN ('Completed', 'Returned', 'Cancelled')),
    sales_channel     VARCHAR(30) NOT NULL,
    shipping_city     VARCHAR(80) NOT NULL,
    courier_name      VARCHAR(40) NOT NULL,
    payment_method    VARCHAR(40) NOT NULL,
    promo_code        VARCHAR(30)
);

CREATE TABLE IF NOT EXISTS order_items (
    order_item_id     INTEGER PRIMARY KEY,
    order_id          VARCHAR(14) NOT NULL REFERENCES orders(order_id),
    product_id        INTEGER NOT NULL REFERENCES products(product_id),
    quantity          INTEGER NOT NULL CHECK (quantity BETWEEN 1 AND 20),
    unit_price        NUMERIC(12,2) NOT NULL CHECK (unit_price >= 0),
    discount_pct      NUMERIC(5,2) NOT NULL CHECK (discount_pct BETWEEN 0 AND 100),
    line_revenue      NUMERIC(14,2) NOT NULL CHECK (line_revenue >= 0),
    line_cost         NUMERIC(14,2) NOT NULL CHECK (line_cost >= 0),
    UNIQUE (order_id, product_id)
);

COMMIT;
