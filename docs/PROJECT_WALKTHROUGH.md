# Beginner-friendly walkthrough

## 1. Start with the business grain

An order can contain several products. That is why `orders` and `order_items` are separate tables. The order table stores information that occurs once per order; the item table stores quantity, price, discount, revenue, and cost for each product line.

## 2. Generate and inspect the raw CSVs

```bash
python -m src.generate_data
```

Open `data/raw/orders_raw.csv` and `data/raw/order_items_raw.csv`. Look for duplicate order IDs, city spelling variants, and the six quantity anomalies.

## 3. Prepare the PostgreSQL load files

```bash
python -m src.prepare_data
```

The preparation script standardises cities, removes duplicate orders, saves invalid item rows to an exceptions file, and recalculates line revenue consistently. It does not replace missing promotion codes because “no promotion” is valid.

## 4. Understand the schema

Read `sql/01_schema.sql` beside `docs/DATA_MODEL.md`. Practise explaining each relationship:

- one category has many products;
- one customer has many orders;
- one order has many order items;
- one product can appear in many order items.

## 5. Load and query PostgreSQL

Follow `docs/PGADMIN_SETUP.md`, then run one query at a time from `sql/04_analysis_queries.sql`. Before looking at the result, predict which columns will appear and why each `GROUP BY` field is required.

## 6. Check the financial sign policy

In `sql/03_views.sql`, completed revenue is positive, returned revenue is negative, and cancelled revenue is zero. This lets `SUM(net_revenue)` produce an interpretable sales result without deleting return history.

## 7. Use and explain the dashboard

```bash
streamlit run app.py
```

Change one filter at a time and verify that all KPIs and charts recalculate. Explain that gross margin is calculated from total gross profit divided by total net revenue; it is not the average of category margins.

## 8. Interview explanation

> I designed a normalised PostgreSQL retail database and loaded a reproducible synthetic dataset through Python. I wrote reporting views and business queries using joins, grouped aggregations, a window calculation, CTEs, filters, and a benchmark subquery. I reconciled revenue formulas and built an interactive dashboard with consistent return handling. The repository includes pgAdmin setup instructions and automated tests.

