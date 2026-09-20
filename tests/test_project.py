from __future__ import annotations

import sqlite3
from pathlib import Path

import pandas as pd
import sqlglot
from streamlit.testing.v1 import AppTest

from src.analytics import compute_kpis, load_sales_data


PROJECT_ROOT = Path(__file__).resolve().parents[1]


def test_clean_data_keys_quantities_and_revenue_formula() -> None:
    data_dir = PROJECT_ROOT / "data" / "processed"
    orders = pd.read_csv(data_dir / "orders.csv")
    items = pd.read_csv(data_dir / "order_items.csv")

    expected = (items["quantity"] * items["unit_price"] * (1 - items["discount_pct"] / 100)).round(2)
    assert orders["order_id"].is_unique
    assert items["order_item_id"].is_unique
    assert items["quantity"].between(1, 20).all()
    assert (items["line_revenue"] - expected).abs().max() <= 0.01
    assert set(items["order_id"]).issubset(set(orders["order_id"]))


def test_postgres_sql_files_parse_in_postgres_dialect() -> None:
    sql_dir = PROJECT_ROOT / "sql"
    for path in sorted(sql_dir.glob("*.sql")):
        statements = sqlglot.parse(path.read_text(encoding="utf-8"), read="postgres")
        assert statements, f"No SQL statements parsed from {path.name}"
        assert all(statement is not None for statement in statements)


def test_schema_accepts_processed_tables_in_relational_order() -> None:
    connection = sqlite3.connect(":memory:")
    connection.execute("PRAGMA foreign_keys = ON")
    connection.executescript((PROJECT_ROOT / "sql" / "01_schema.sql").read_text(encoding="utf-8"))
    for table in ["categories", "products", "customers", "orders", "order_items"]:
        frame = pd.read_csv(PROJECT_ROOT / "data" / "processed" / f"{table}.csv")
        frame.to_sql(table, connection, if_exists="append", index=False)
    assert connection.execute("SELECT COUNT(*) FROM orders").fetchone()[0] == 9000
    assert connection.execute("SELECT COUNT(*) FROM order_items").fetchone()[0] > 18000
    connection.close()


def test_kpis_reconcile_to_signed_line_values() -> None:
    sales = load_sales_data()
    kpis = compute_kpis(sales)
    status_sign = sales["order_status"].map({"Completed": 1, "Returned": -1, "Cancelled": 0})
    independent_revenue = (sales["line_revenue"] * status_sign).sum()
    independent_profit = ((sales["line_revenue"] - sales["line_cost"]) * status_sign).sum()
    assert abs(kpis["net_revenue"] - independent_revenue) < 0.01
    assert abs(kpis["gross_profit"] - independent_profit) < 0.01
    assert 0 < kpis["gross_margin_pct"] < 100
    assert 0 < kpis["return_rate_pct"] < 20


def test_dashboard_loads_and_category_filter_updates_results() -> None:
    app = AppTest.from_file(str(PROJECT_ROOT / "app.py")).run(timeout=30)
    assert not app.exception
    assert app.title[0].value == "Urban Basket Retail Sales Dashboard"
    assert len(app.metric) == 6
    all_orders = app.metric[3].value
    app.multiselect[0].set_value(["Bakery"]).run(timeout=30)
    assert not app.exception
    assert app.metric[3].value != all_orders

