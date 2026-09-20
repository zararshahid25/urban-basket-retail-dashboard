"""Urban Basket interactive retail sales dashboard."""

from __future__ import annotations

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

from src.analytics import compute_kpis, load_sales_data


COLORS = {
    "forest": "#24543D",
    "green": "#3E8E63",
    "mint": "#9BC7AA",
    "orange": "#E58A35",
    "gold": "#F0B44D",
    "red": "#C85C5C",
    "ink": "#24362D",
}

st.set_page_config(page_title="Urban Basket Sales", page_icon="🛒", layout="wide")
st.markdown(
    """
    <style>
      .stApp { background: #F7F5EF; }
      [data-testid="stSidebar"] { background: #24543D; }
      [data-testid="stSidebar"] * { color: #FFFFFF; }
      [data-testid="stMetric"] {
        background: #FFFFFF; border: 1px solid #E5E1D7; border-radius: 14px;
        padding: 14px 16px; box-shadow: 0 2px 8px rgba(36, 84, 61, .06);
      }
      [data-testid="stMetricLabel"] { color: #68766E; }
      [data-testid="stMetricValue"] { color: #24543D; }
      .block-container { padding-top: 1.5rem; padding-bottom: 3rem; }
      .note { color: #68766E; font-size: .92rem; margin-top: -8px; }
      .scope { background:#E7F1E9; border-left:4px solid #3E8E63; color:#24543D;
               padding:10px 13px; border-radius:8px; margin-bottom:16px; }
    </style>
    """,
    unsafe_allow_html=True,
)


@st.cache_data
def get_data() -> pd.DataFrame:
    return load_sales_data()


def style_chart(fig: go.Figure, height: int = 360) -> go.Figure:
    fig.update_layout(
        height=height,
        margin=dict(l=20, r=20, t=55, b=20),
        paper_bgcolor="white",
        plot_bgcolor="white",
        font=dict(family="Inter, Arial, sans-serif", color=COLORS["ink"]),
        title_font=dict(size=17),
        hoverlabel=dict(bgcolor="white"),
        legend_title_text="",
    )
    fig.update_xaxes(showgrid=False, linecolor="#E5E1D7")
    fig.update_yaxes(gridcolor="#EEEAE1", zeroline=False)
    return fig


sales = get_data()

st.sidebar.markdown("## Urban Basket")
st.sidebar.caption("Retail sales intelligence")
st.sidebar.markdown("### Filters")

min_date, max_date = sales["order_date"].min().date(), sales["order_date"].max().date()
date_range = st.sidebar.date_input(
    "Order date", value=(min_date, max_date), min_value=min_date, max_value=max_date
)
start_date, end_date = (
    map(pd.Timestamp, date_range)
    if len(date_range) == 2
    else (pd.Timestamp(date_range[0]), pd.Timestamp(date_range[0]))
)

all_categories = sorted(sales["category_name"].unique())
all_cities = sorted(sales["shipping_city"].unique())
all_channels = ["Web", "Mobile App", "Marketplace"]
all_statuses = ["Completed", "Returned", "Cancelled"]

categories = st.sidebar.multiselect("Category", all_categories, default=all_categories)
cities = st.sidebar.multiselect("Shipping city", all_cities, default=all_cities)
channels = st.sidebar.multiselect("Sales channel", all_channels, default=all_channels)
statuses = st.sidebar.multiselect("Order status", all_statuses, default=all_statuses)

filtered = sales[
    sales["order_date"].between(start_date, end_date)
    & sales["category_name"].isin(categories)
    & sales["shipping_city"].isin(cities)
    & sales["sales_channel"].isin(channels)
    & sales["order_status"].isin(statuses)
].copy()

st.title("Urban Basket Retail Sales Dashboard")
st.caption(f"Reporting period: {start_date:%d %b %Y} – {end_date:%d %b %Y}")
st.markdown(
    '<div class="scope"><strong>Portfolio simulation:</strong> All orders, products, customers, and financial values are generated for this project.</div>',
    unsafe_allow_html=True,
)

if filtered.empty:
    st.warning("No sales records match the selected filters.")
    st.stop()

kpis = compute_kpis(filtered)
metrics = st.columns(6)
metrics[0].metric("Net revenue", f"PKR {kpis['net_revenue']/1_000_000:.2f}M")
metrics[1].metric("Gross profit", f"PKR {kpis['gross_profit']/1_000_000:.2f}M")
metrics[2].metric("Gross margin", f"{kpis['gross_margin_pct']:.1f}%")
metrics[3].metric("Orders", f"{kpis['orders']:,}")
metrics[4].metric("Average order value", f"PKR {kpis['average_order_value']:,.0f}")
metrics[5].metric("Return rate", f"{kpis['return_rate_pct']:.1f}%")

st.markdown("### Sales trend and mix")
st.markdown(
    '<p class="note">Net revenue reverses returned sales and excludes cancelled orders.</p>',
    unsafe_allow_html=True,
)
monthly = (
    filtered.groupby("month", as_index=False)
    .agg(net_revenue=("net_revenue", "sum"), gross_profit=("gross_profit", "sum"))
)
monthly_long = monthly.melt("month", var_name="measure", value_name="amount")
monthly_long["measure"] = monthly_long["measure"].map(
    {"net_revenue": "Net revenue", "gross_profit": "Gross profit"}
)

left, right = st.columns([1.55, 1])
fig_month = px.line(
    monthly_long,
    x="month",
    y="amount",
    color="measure",
    markers=True,
    title="Monthly revenue and gross profit",
    color_discrete_map={"Net revenue": COLORS["green"], "Gross profit": COLORS["orange"]},
)
fig_month.update_traces(line_width=3)
fig_month.update_xaxes(title=None, tickformat="%b\n%Y")
fig_month.update_yaxes(title="PKR", tickformat="~s")
left.plotly_chart(style_chart(fig_month), use_container_width=True)

category = (
    filtered.groupby("category_name", as_index=False)
    .agg(net_revenue=("net_revenue", "sum"), gross_profit=("gross_profit", "sum"))
    .sort_values("net_revenue")
)
fig_category = px.bar(
    category,
    x="net_revenue",
    y="category_name",
    orientation="h",
    title="Net revenue by category",
    color_discrete_sequence=[COLORS["green"]],
)
fig_category.update_xaxes(title="PKR", tickformat="~s")
fig_category.update_yaxes(title=None)
right.plotly_chart(style_chart(fig_category), use_container_width=True)

left, right = st.columns([1, 1])
city_channel = (
    filtered.groupby(["shipping_city", "sales_channel"], as_index=False)["net_revenue"].sum()
)
fig_city = px.bar(
    city_channel,
    x="shipping_city",
    y="net_revenue",
    color="sales_channel",
    barmode="group",
    title="Net revenue by city and channel",
    color_discrete_sequence=[COLORS["green"], COLORS["orange"], COLORS["gold"]],
)
fig_city.update_xaxes(title=None)
fig_city.update_yaxes(title="PKR", tickformat="~s")
left.plotly_chart(style_chart(fig_city), use_container_width=True)

category_orders = filtered[["category_name", "order_id", "order_status"]].drop_duplicates()
category_orders = category_orders[category_orders["order_status"].isin(["Completed", "Returned"])]
returns = (
    category_orders.assign(is_returned=category_orders["order_status"].eq("Returned").astype(int))
    .groupby("category_name", as_index=False)
    .agg(eligible_orders=("order_id", "nunique"), returned_orders=("is_returned", "sum"))
)
returns["return_rate_pct"] = 100 * returns["returned_orders"] / returns["eligible_orders"]
returns = returns.sort_values("return_rate_pct", ascending=False)
fig_returns = px.bar(
    returns,
    x="category_name",
    y="return_rate_pct",
    title="Return rate by category",
    color_discrete_sequence=[COLORS["orange"]],
    text_auto=".1f",
)
fig_returns.update_xaxes(title=None)
fig_returns.update_yaxes(title="Return rate (%)", rangemode="tozero")
right.plotly_chart(style_chart(fig_returns), use_container_width=True)

st.markdown("### Product detail")
product_table = (
    filtered.groupby(["product_name", "category_name"], as_index=False)
    .agg(net_units=("net_units", "sum"), net_revenue=("net_revenue", "sum"), gross_profit=("gross_profit", "sum"))
)
product_table["gross_margin_pct"] = 100 * product_table["gross_profit"] / product_table["net_revenue"]
product_table = product_table.sort_values("net_revenue", ascending=False).head(15)
st.dataframe(
    product_table.rename(
        columns={
            "product_name": "Product",
            "category_name": "Category",
            "net_units": "Net units",
            "net_revenue": "Net revenue",
            "gross_profit": "Gross profit",
            "gross_margin_pct": "Margin %",
        }
    ),
    hide_index=True,
    use_container_width=True,
    column_config={
        "Net revenue": st.column_config.NumberColumn(format="PKR %,.0f"),
        "Gross profit": st.column_config.NumberColumn(format="PKR %,.0f"),
        "Margin %": st.column_config.NumberColumn(format="%.1f%%"),
    },
)

with st.expander("Metric definitions and reporting policy"):
    st.markdown(
        """
        - **Net revenue:** completed line revenue minus returned line revenue; cancelled lines contribute zero.
        - **Gross profit:** signed net revenue minus signed line cost.
        - **Gross margin:** total gross profit divided by total net revenue; category margins are not averaged.
        - **Average order value:** total net revenue divided by completed orders.
        - **Return rate:** returned orders divided by completed plus returned orders. Cancelled orders are excluded.
        """
    )

