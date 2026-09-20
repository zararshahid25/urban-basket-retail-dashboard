"""Generate deterministic synthetic retail data for Urban Basket."""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd


SEED = 2026
PROJECT_ROOT = Path(__file__).resolve().parents[1]
RAW_DIR = PROJECT_ROOT / "data" / "raw"

CATEGORY_PRODUCTS = {
    "Fresh Produce": ["Apples", "Bananas", "Tomatoes", "Potatoes", "Onions", "Spinach"],
    "Dairy & Eggs": ["Fresh Milk", "Yogurt", "Cheddar Cheese", "Butter", "Eggs", "Cream"],
    "Bakery": ["White Bread", "Brown Bread", "Croissants", "Cupcakes", "Burger Buns", "Cookies"],
    "Beverages": ["Orange Juice", "Mineral Water", "Green Tea", "Coffee", "Cola", "Mango Drink"],
    "Pantry": ["Basmati Rice", "Cooking Oil", "Flour", "Sugar", "Lentils", "Spices"],
    "Snacks": ["Potato Chips", "Mixed Nuts", "Chocolate", "Popcorn", "Crackers", "Granola Bars"],
    "Household": ["Dish Soap", "Laundry Powder", "Tissues", "Trash Bags", "Floor Cleaner", "Foil"],
    "Personal Care": ["Shampoo", "Soap", "Toothpaste", "Face Wash", "Hand Wash", "Lotion"],
}

CITIES = ["Islamabad", "Rawalpindi", "Lahore", "Karachi", "Peshawar", "Faisalabad"]


def build_categories() -> pd.DataFrame:
    return pd.DataFrame(
        {
            "category_id": range(1, len(CATEGORY_PRODUCTS) + 1),
            "category_name": list(CATEGORY_PRODUCTS),
        }
    )


def build_products(rng: np.random.Generator, categories: pd.DataFrame) -> pd.DataFrame:
    records: list[dict[str, object]] = []
    product_id = 1
    for category in categories.itertuples(index=False):
        base_names = CATEGORY_PRODUCTS[category.category_name]
        for variant in range(1, 4):
            for base_name in base_names:
                unit_cost = round(float(rng.uniform(60, 900)), 2)
                markup = float(rng.uniform(1.18, 1.62))
                records.append(
                    {
                        "product_id": product_id,
                        "category_id": category.category_id,
                        "product_name": f"{base_name} {variant}",
                        "brand": rng.choice(["Urban Choice", "Daily Best", "Home Select", "Value Mart"]),
                        "unit_cost": unit_cost,
                        "list_price": round(unit_cost * markup, 2),
                        "active_flag": True,
                    }
                )
                product_id += 1
    return pd.DataFrame(records)


def build_customers(rng: np.random.Generator) -> pd.DataFrame:
    n_customers = 1_600
    signup_dates = pd.to_datetime(
        rng.choice(pd.date_range("2023-01-01", "2025-11-30"), n_customers)
    )
    cities = rng.choice(CITIES, n_customers, p=[0.22, 0.23, 0.18, 0.17, 0.10, 0.10]).astype(object)
    dirty_rows = rng.choice(np.arange(n_customers), 48, replace=False)
    cities[dirty_rows[:12]] = "ISB"
    cities[dirty_rows[12:24]] = "Rwp"
    cities[dirty_rows[24:36]] = "Lahore "
    cities[dirty_rows[36:]] = "karachi"
    return pd.DataFrame(
        {
            "customer_id": [f"C{i:05d}" for i in range(1, n_customers + 1)],
            "customer_segment": rng.choice(
                ["Regular", "Family", "Premium", "Small Business"],
                n_customers,
                p=[0.48, 0.27, 0.15, 0.10],
            ),
            "city": cities,
            "signup_date": signup_dates,
        }
    )


def build_orders_and_items(
    rng: np.random.Generator,
    customers: pd.DataFrame,
    products: pd.DataFrame,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    n_orders = 9_000
    order_dates = pd.to_datetime(
        rng.choice(pd.date_range("2024-01-01", "2025-12-31"), n_orders)
    )
    customer_ids = rng.choice(customers["customer_id"], n_orders)
    customer_city = customers.set_index("customer_id")["city"].to_dict()
    shipping_city = np.array([customer_city[value] for value in customer_ids], dtype=object)
    channels = rng.choice(["Web", "Mobile App", "Marketplace"], n_orders, p=[0.42, 0.46, 0.12])
    statuses = rng.choice(
        ["Completed", "Returned", "Cancelled"], n_orders, p=[0.895, 0.068, 0.037]
    )
    courier = rng.choice(
        ["SwiftEx", "BlueLine", "RapidGo", "Store Pickup"],
        n_orders,
        p=[0.34, 0.28, 0.25, 0.13],
    )
    payment = rng.choice(
        ["Cash on Delivery", "Card", "Bank Transfer", "Wallet"],
        n_orders,
        p=[0.43, 0.27, 0.12, 0.18],
    )
    promo = rng.choice(
        [None, "WELCOME10", "SAVE15", "APP5", "FREESHIP"],
        n_orders,
        p=[0.66, 0.08, 0.08, 0.10, 0.08],
    )

    orders = pd.DataFrame(
        {
            "order_id": [f"UB-{i:06d}" for i in range(1, n_orders + 1)],
            "customer_id": customer_ids,
            "order_date": order_dates,
            "order_status": statuses,
            "sales_channel": channels,
            "shipping_city": shipping_city,
            "courier_name": courier,
            "payment_method": payment,
            "promo_code": promo,
        }
    )

    product_lookup = products.set_index("product_id")
    item_records: list[dict[str, object]] = []
    order_item_id = 1
    for order in orders.itertuples(index=False):
        item_count = int(rng.choice([1, 2, 3, 4, 5], p=[0.33, 0.30, 0.21, 0.11, 0.05]))
        product_ids = rng.choice(products["product_id"], item_count, replace=False)
        for product_id in product_ids:
            product = product_lookup.loc[product_id]
            quantity = int(rng.choice([1, 2, 3, 4, 5], p=[0.54, 0.27, 0.12, 0.05, 0.02]))
            discount_pct = float(rng.choice([0, 5, 10, 15, 20], p=[0.54, 0.16, 0.16, 0.09, 0.05]))
            unit_price = round(float(product["list_price"] * rng.uniform(0.97, 1.03)), 2)
            line_revenue = round(quantity * unit_price * (1 - discount_pct / 100), 2)
            line_cost = round(quantity * float(product["unit_cost"]), 2)
            item_records.append(
                {
                    "order_item_id": order_item_id,
                    "order_id": order.order_id,
                    "product_id": int(product_id),
                    "quantity": quantity,
                    "unit_price": unit_price,
                    "discount_pct": discount_pct,
                    "line_revenue": line_revenue,
                    "line_cost": line_cost,
                }
            )
            order_item_id += 1

    items = pd.DataFrame(item_records)

    # Controlled source issues: duplicate orders and implausible quantities.
    orders = pd.concat([orders, orders.sample(4, random_state=SEED)], ignore_index=True)
    anomaly_rows = rng.choice(items.index, 6, replace=False)
    items.loc[anomaly_rows[:3], "quantity"] = 0
    items.loc[anomaly_rows[3:], "quantity"] = 99
    # Keep original revenue/cost so the anomaly is detectable through reconciliation.
    return orders, items


def main() -> None:
    RAW_DIR.mkdir(parents=True, exist_ok=True)
    rng = np.random.default_rng(SEED)
    categories = build_categories()
    products = build_products(rng, categories)
    customers = build_customers(rng)
    orders, items = build_orders_and_items(rng, customers, products)

    categories.to_csv(RAW_DIR / "categories.csv", index=False)
    products.to_csv(RAW_DIR / "products.csv", index=False)
    customers.to_csv(RAW_DIR / "customers_raw.csv", index=False)
    orders.to_csv(RAW_DIR / "orders_raw.csv", index=False)
    items.to_csv(RAW_DIR / "order_items_raw.csv", index=False)
    print(f"Generated {len(orders):,} order rows and {len(items):,} item rows.")


if __name__ == "__main__":
    main()

