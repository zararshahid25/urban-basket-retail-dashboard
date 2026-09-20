"""Clean Urban Basket source files and produce load-ready PostgreSQL tables."""

from __future__ import annotations

import json
from pathlib import Path

import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[1]
RAW_DIR = PROJECT_ROOT / "data" / "raw"
PROCESSED_DIR = PROJECT_ROOT / "data" / "processed"
SAMPLE_DIR = PROJECT_ROOT / "data" / "sample"
REPORTS_DIR = PROJECT_ROOT / "reports"

CITY_MAP = {
    "isb": "Islamabad",
    "islamabad": "Islamabad",
    "rwp": "Rawalpindi",
    "rawalpindi": "Rawalpindi",
    "lahore": "Lahore",
    "karachi": "Karachi",
    "peshawar": "Peshawar",
    "faisalabad": "Faisalabad",
}


def normalise_city(series: pd.Series) -> pd.Series:
    return series.astype("string").str.strip().str.casefold().map(CITY_MAP)


def main() -> None:
    for directory in [PROCESSED_DIR, SAMPLE_DIR, REPORTS_DIR]:
        directory.mkdir(parents=True, exist_ok=True)

    categories = pd.read_csv(RAW_DIR / "categories.csv")
    products = pd.read_csv(RAW_DIR / "products.csv")
    customers = pd.read_csv(RAW_DIR / "customers_raw.csv", parse_dates=["signup_date"])
    orders = pd.read_csv(RAW_DIR / "orders_raw.csv", parse_dates=["order_date"])
    items = pd.read_csv(RAW_DIR / "order_items_raw.csv")

    duplicate_orders = int(orders.duplicated("order_id").sum())
    inconsistent_customer_cities = int((~customers["city"].isin(CITY_MAP.values())).sum())
    inconsistent_shipping_cities = int((~orders["shipping_city"].isin(CITY_MAP.values())).sum())
    invalid_items_mask = ~items["quantity"].between(1, 20)

    orders = orders.drop_duplicates("order_id", keep="first").copy()
    customers["city"] = normalise_city(customers["city"])
    orders["shipping_city"] = normalise_city(orders["shipping_city"])

    exceptions = items.loc[invalid_items_mask].copy()
    exceptions["issue"] = "Quantity outside accepted range 1–20"
    items = items.loc[~invalid_items_mask].copy()

    items["expected_revenue"] = (
        items["quantity"] * items["unit_price"] * (1 - items["discount_pct"] / 100)
    ).round(2)
    reconciliation_variance = (items["line_revenue"] - items["expected_revenue"]).abs()
    rounding_rows_recalculated = int((reconciliation_variance >= 0.009).sum())
    items["line_revenue"] = items["expected_revenue"]
    revenue_mismatches = int(
        ((items["line_revenue"] - items["expected_revenue"]).abs() > 0.001).sum()
    )
    if revenue_mismatches:
        raise ValueError("Unexpected revenue mismatches remained after anomaly exclusion.")
    items = items.drop(columns="expected_revenue")

    if customers["customer_id"].duplicated().any() or orders["order_id"].duplicated().any():
        raise ValueError("Duplicate business keys remain after cleaning.")
    if customers["city"].isna().any() or orders["shipping_city"].isna().any():
        raise ValueError("Unmapped city values remain after standardisation.")
    if not set(items["order_id"]).issubset(set(orders["order_id"])):
        raise ValueError("Order items contain unmatched order IDs.")
    if not set(items["product_id"]).issubset(set(products["product_id"])):
        raise ValueError("Order items contain unmatched product IDs.")

    tables = {
        "categories": categories,
        "products": products,
        "customers": customers,
        "orders": orders,
        "order_items": items,
    }
    for name, frame in tables.items():
        frame.to_csv(PROCESSED_DIR / f"{name}.csv", index=False)

    sample = (
        items.head(300)
        .merge(orders, on="order_id", how="left")
        .merge(products[["product_id", "category_id", "product_name"]], on="product_id", how="left")
        .merge(categories, on="category_id", how="left")
    )
    sample.to_csv(SAMPLE_DIR / "sales_sample.csv", index=False)
    exceptions.to_csv(REPORTS_DIR / "data_quality_exceptions.csv", index=False)

    quality = {
        "raw_order_rows": int(len(pd.read_csv(RAW_DIR / "orders_raw.csv"))),
        "clean_orders": int(len(orders)),
        "duplicate_order_ids_removed": duplicate_orders,
        "customer_city_values_standardised": inconsistent_customer_cities,
        "shipping_city_values_standardised": inconsistent_shipping_cities,
        "invalid_quantity_rows_excluded": int(invalid_items_mask.sum()),
        "line_revenue_rounding_rows_recalculated": rounding_rows_recalculated,
        "clean_order_items": int(len(items)),
        "revenue_formula_mismatches": revenue_mismatches,
    }
    with (REPORTS_DIR / "data_quality_summary.json").open("w", encoding="utf-8") as file:
        json.dump(quality, file, indent=2)
    pd.DataFrame([{"check": key, "value": value} for key, value in quality.items()]).to_csv(
        REPORTS_DIR / "data_quality_summary.csv", index=False
    )
    print(f"Prepared {len(orders):,} orders and {len(items):,} valid order items.")


if __name__ == "__main__":
    main()
