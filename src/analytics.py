"""Build a validated analysis table and calculate retail KPIs."""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = PROJECT_ROOT / "data" / "processed"


def load_sales_data() -> pd.DataFrame:
    categories = pd.read_csv(DATA_DIR / "categories.csv")
    products = pd.read_csv(DATA_DIR / "products.csv")
    customers = pd.read_csv(DATA_DIR / "customers.csv")
    orders = pd.read_csv(DATA_DIR / "orders.csv", parse_dates=["order_date"])
    items = pd.read_csv(DATA_DIR / "order_items.csv")

    sales = (
        items.merge(orders, on="order_id", validate="many_to_one")
        .merge(products, on="product_id", validate="many_to_one")
        .merge(categories, on="category_id", validate="many_to_one")
        .merge(customers[["customer_id", "customer_segment"]], on="customer_id", validate="many_to_one")
    )
    status_sign = sales["order_status"].map({"Completed": 1, "Returned": -1, "Cancelled": 0})
    sales["net_revenue"] = sales["line_revenue"] * status_sign
    sales["gross_profit"] = (sales["line_revenue"] - sales["line_cost"]) * status_sign
    sales["net_units"] = sales["quantity"] * status_sign
    sales["month"] = sales["order_date"].dt.to_period("M").dt.to_timestamp()
    return sales


def compute_kpis(sales: pd.DataFrame) -> dict[str, float | int]:
    order_level = sales[["order_id", "order_status"]].drop_duplicates()
    completed_orders = order_level["order_status"].eq("Completed").sum()
    returned_orders = order_level["order_status"].eq("Returned").sum()
    eligible_orders = completed_orders + returned_orders
    net_revenue = float(sales["net_revenue"].sum())
    return {
        "net_revenue": net_revenue,
        "gross_profit": float(sales["gross_profit"].sum()),
        "gross_margin_pct": float(100 * sales["gross_profit"].sum() / net_revenue) if net_revenue else np.nan,
        "net_units": int(sales["net_units"].sum()),
        "orders": int(order_level["order_id"].nunique()),
        "average_order_value": float(net_revenue / completed_orders) if completed_orders else np.nan,
        "return_rate_pct": float(100 * returned_orders / eligible_orders) if eligible_orders else np.nan,
    }

