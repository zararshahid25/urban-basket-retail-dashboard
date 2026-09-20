"""Generate dashboard preview and analysis exports for the portfolio."""

from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch
import pandas as pd
import seaborn as sns

from src.analytics import compute_kpis, load_sales_data


PROJECT_ROOT = Path(__file__).resolve().parents[1]
ASSETS_DIR = PROJECT_ROOT / "assets"
REPORTS_DIR = PROJECT_ROOT / "reports"
FOREST, GREEN, ORANGE, GOLD, INK, MUTED = "#24543D", "#3E8E63", "#E58A35", "#F0B44D", "#24362D", "#68766E"


def metric_card(fig: plt.Figure, x: float, title: str, value: str) -> None:
    fig.patches.append(
        FancyBboxPatch(
            (x, 0.80), 0.145, 0.085,
            boxstyle="round,pad=0.008,rounding_size=0.01",
            transform=fig.transFigure, facecolor="white", edgecolor="#E5E1D7", linewidth=1,
        )
    )
    fig.text(x + 0.012, 0.852, title, color=MUTED, fontsize=9)
    fig.text(x + 0.012, 0.817, value, color=FOREST, fontsize=16, weight="bold")


def main() -> None:
    ASSETS_DIR.mkdir(parents=True, exist_ok=True)
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    sales = load_sales_data()
    kpis = compute_kpis(sales)

    monthly = sales.groupby("month", as_index=False).agg(
        net_revenue=("net_revenue", "sum"), gross_profit=("gross_profit", "sum"), orders=("order_id", "nunique")
    )
    category = sales.groupby("category_name", as_index=False).agg(
        net_revenue=("net_revenue", "sum"), gross_profit=("gross_profit", "sum"), net_units=("net_units", "sum")
    )
    category["gross_margin_pct"] = 100 * category["gross_profit"] / category["net_revenue"]
    city_channel = sales.groupby(["shipping_city", "sales_channel"], as_index=False)["net_revenue"].sum()
    top_products = sales.groupby(["product_name", "category_name"], as_index=False).agg(
        net_revenue=("net_revenue", "sum"), gross_profit=("gross_profit", "sum"), net_units=("net_units", "sum")
    ).sort_values("net_revenue", ascending=False).head(15)

    monthly.to_csv(REPORTS_DIR / "monthly_sales.csv", index=False)
    category.sort_values("net_revenue", ascending=False).to_csv(REPORTS_DIR / "category_performance.csv", index=False)
    top_products.to_csv(REPORTS_DIR / "top_products.csv", index=False)

    sns.set_theme(style="whitegrid")
    fig = plt.figure(figsize=(16, 11), facecolor="#F7F5EF")
    grid = fig.add_gridspec(3, 2, left=0.06, right=0.96, bottom=0.07, top=0.71, hspace=0.80, wspace=0.27)
    fig.text(0.06, 0.95, "Urban Basket Retail Sales", color=FOREST, fontsize=25, weight="bold")
    fig.text(0.06, 0.918, "PostgreSQL-backed analysis · simulated 2024–2025 transactions", color=MUTED, fontsize=11)

    cards = [
        ("Net revenue", f"PKR {kpis['net_revenue']/1_000_000:.1f}M"),
        ("Gross profit", f"PKR {kpis['gross_profit']/1_000_000:.1f}M"),
        ("Gross margin", f"{kpis['gross_margin_pct']:.1f}%"),
        ("Orders", f"{kpis['orders']:,}"),
        ("Avg order value", f"PKR {kpis['average_order_value']:,.0f}"),
        ("Return rate", f"{kpis['return_rate_pct']:.1f}%"),
    ]
    for i, (title, value) in enumerate(cards):
        metric_card(fig, 0.06 + i * 0.152, title, value)

    ax1 = fig.add_subplot(grid[0, 0])
    ax1.plot(monthly["month"], monthly["net_revenue"], color=GREEN, marker="o", lw=2.6, label="Net revenue")
    ax1.plot(monthly["month"], monthly["gross_profit"], color=ORANGE, marker="o", lw=2.6, label="Gross profit")
    ax1.set_title("Monthly revenue and gross profit", loc="left", color=INK, weight="bold")
    ax1.set_ylabel("PKR")
    ax1.legend(frameon=False, ncol=2)
    ax1.tick_params(axis="x", rotation=35)

    ax2 = fig.add_subplot(grid[0, 1])
    cat_order = category.sort_values("net_revenue")
    ax2.barh(cat_order["category_name"], cat_order["net_revenue"], color=GREEN)
    ax2.set_title("Net revenue by category", loc="left", color=INK, weight="bold")
    ax2.set_xlabel("PKR")
    ax2.set_ylabel("")

    ax3 = fig.add_subplot(grid[1, 0])
    pivot = city_channel.pivot(index="shipping_city", columns="sales_channel", values="net_revenue").fillna(0)
    pivot.plot(kind="bar", ax=ax3, color=[GREEN, ORANGE, GOLD], width=0.78)
    ax3.set_title("Net revenue by city and channel", loc="left", color=INK, weight="bold")
    ax3.set_xlabel("")
    ax3.set_ylabel("PKR")
    ax3.legend(frameon=False, ncol=3, fontsize=8)
    ax3.tick_params(axis="x", rotation=25)

    ax4 = fig.add_subplot(grid[1, 1])
    margin_order = category.sort_values("gross_margin_pct", ascending=False)
    ax4.bar(margin_order["category_name"], margin_order["gross_margin_pct"], color=ORANGE)
    ax4.set_title("Gross margin by category", loc="left", color=INK, weight="bold")
    ax4.set_ylabel("Margin (%)")
    ax4.tick_params(axis="x", rotation=25)

    ax5 = fig.add_subplot(grid[2, :])
    top = top_products.head(10).sort_values("net_revenue")
    ax5.barh(top["product_name"], top["net_revenue"], color=GREEN)
    ax5.set_title("Top 10 products by net revenue", loc="left", color=INK, weight="bold")
    ax5.set_xlabel("PKR")
    ax5.set_ylabel("")

    for axis in [ax1, ax2, ax3, ax4, ax5]:
        axis.set_facecolor("white")
        axis.grid(axis="x" if axis in [ax2, ax5] else "y", color="#EEEAE1", linewidth=0.8)
        axis.spines[["top", "right", "left"]].set_visible(False)
        axis.tick_params(colors=MUTED)

    fig.text(0.06, 0.018, "Net revenue reverses returned sales and excludes cancelled orders. All values are synthetic.", color=MUTED, fontsize=9)
    fig.savefig(
        ASSETS_DIR / "urban_basket_dashboard_preview.jpg",
        dpi=110, bbox_inches="tight", facecolor=fig.get_facecolor(), pil_kwargs={"quality": 92},
    )
    plt.close(fig)
    print("Created Urban Basket preview and report exports.")


if __name__ == "__main__":
    main()

