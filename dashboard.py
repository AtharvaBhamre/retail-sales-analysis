from pathlib import Path

import numpy as np
import pandas as pd
import plotly.express as px
import streamlit as st

st.set_page_config(
    page_title="Retail Sales Analytics",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)

BASE_DIR = Path(__file__).resolve().parent
DATA_FILE = BASE_DIR / "data" / "sales.csv"

st.markdown(
    """
    <style>
    :root { --ink:#000000; --muted:#222222; --line:#d6d6d6; --accent:#16734f; --accent-soft:#eaf5ef; }
    .stApp, [data-testid="stAppViewContainer"] { background:#ffffff !important; color:#000000 !important; }
    [data-testid="stHeader"], [data-testid="stToolbar"] { background:#ffffff !important; }
    [data-testid="stSidebar"] { background:#ffffff !important; border-right:1px solid #d6d6d6; }
    [data-testid="stSidebar"] *, .stApp * { color:#000000; }
    [data-testid="stSidebar"] [data-baseweb="select"] > div,
    [data-testid="stSidebar"] [data-baseweb="input"] > div,
    [data-baseweb="select"] > div, [data-baseweb="input"] > div,
    textarea, input { background:#ffffff !important; color:#000000 !important; border-color:#bdbdbd !important; }
    [data-testid="stSidebar"] button, div[data-testid="stButton"] > button,
    div[data-testid="stDownloadButton"] > button { background:#ffffff !important; color:#000000 !important; border:1px solid #8c8c8c !important; border-radius:9px; font-weight:650; }
    .block-container { max-width:1500px; padding-top:2rem; padding-bottom:3rem; }
    [data-testid="stMetric"] { background:#ffffff !important; color:#000000 !important; border:1px solid #d6d6d6; padding:19px 20px; border-radius:15px; box-shadow:0 2px 8px rgba(0,0,0,.04); }
    [data-testid="stMetricLabel"], [data-testid="stMetricValue"], [data-testid="stMetricDelta"] { color:#000000 !important; }
    [data-testid="stMetricLabel"] { font-size:.86rem; font-weight:650; }
    [data-testid="stMetricValue"] { font-size:1.7rem; font-weight:750; }
    .eyebrow { color:#000000 !important; font-size:.72rem; font-weight:800; letter-spacing:.14em; text-transform:uppercase; margin-bottom:.45rem; }
    .main-title { font-size:2.35rem; line-height:1.15; font-weight:780; color:#000000 !important; letter-spacing:-.055em; margin:0; }
    .subtitle, .stCaption, small, label, p, span, li { color:#000000; }
    h1, h2, h3, h4, h5, h6 { color:#000000 !important; }
    [data-testid="stPlotlyChart"] { background:#ffffff !important; border:1px solid #d6d6d6; border-radius:15px; padding:8px 8px 0; }
    [data-testid="stDataFrame"] { border:1px solid #d6d6d6; border-radius:12px; overflow:hidden; }
    .insight { border:1px solid #d6d6d6; border-left:4px solid #16734f; border-radius:12px; padding:15px 17px; background:#ffffff !important; margin-bottom:9px; }
    .insight-title, .insight-body { color:#000000 !important; }
    .insight-title { font-weight:750; margin-bottom:4px; }
    .insight-body { font-size:.93rem; }
    hr { border-color:#d6d6d6 !important; }
    @media (max-width: 800px) { .main-title { font-size:1.8rem; } .block-container { padding-top:1.2rem; } }
    </style>
    """,
    unsafe_allow_html=True,
)

GREEN = "#16836b"
BLUE = "#4263a5"
TEAL = "#56a99a"
SLATE = "#000000"
GRID = "#d6d6d6"
TEXT = "#000000"


def money(value):
    return f"${value:,.2f}"


@st.cache_data(show_spinner="Loading retail sales data…")
def load_data(path_string, modified_time):
    path = Path(path_string)
    try:
        frame = pd.read_csv(path, encoding="utf-8-sig")
    except UnicodeDecodeError:
        frame = pd.read_csv(path, encoding="latin1")

    frame.columns = frame.columns.astype(str).str.strip()
    for col in ["Sales", "Profit", "Quantity", "Discount"]:
        if col in frame.columns:
            frame[col] = pd.to_numeric(frame[col], errors="coerce")
    for col in ["Order Date", "Ship Date", "Date"]:
        if col in frame.columns:
            frame[col] = pd.to_datetime(frame[col], errors="coerce")
    return frame


def style_chart(fig, height=340):
    fig.update_layout(
        height=height,
        margin=dict(l=8, r=8, t=38, b=8),
        paper_bgcolor="white",
        plot_bgcolor="white",
        font=dict(family="Arial, sans-serif", color=TEXT, size=12),
        title=dict(font=dict(size=15, color="#000000"), x=.01, xanchor="left"),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1, title_text=""),
        hoverlabel=dict(bgcolor="white", font_color=TEXT),
    )
    fig.update_xaxes(showgrid=False, linecolor=GRID, zeroline=False)
    fig.update_yaxes(showgrid=True, gridcolor=GRID, zeroline=False)
    return fig


def section_title(title, note=None):
    st.markdown(f"### {title}")
    if note:
        st.caption(note)


if not DATA_FILE.exists():
    st.error(f"Dataset not found: `{DATA_FILE}`")
    st.info("Place your existing sales.csv file inside the project's data folder.")
    st.stop()

try:
    df = load_data(str(DATA_FILE), DATA_FILE.stat().st_mtime)
except Exception as exc:
    st.error(f"Could not read the dataset: {exc}")
    st.stop()

if df.empty:
    st.warning("The dataset is empty.")
    st.stop()
if "Sales" not in df.columns:
    st.error("The dataset must contain a 'Sales' column.")
    st.write("Columns found:", df.columns.tolist())
    st.stop()
if "Profit" not in df.columns:
    df["Profit"] = 0.0
if "Order ID" not in df.columns:
    df["Order ID"] = [f"ROW-{i + 1}" for i in range(len(df))]

st.markdown('<div class="eyebrow">BUSINESS INTELLIGENCE</div>', unsafe_allow_html=True)
st.markdown('<p class="main-title">Retail Sales Analytics</p>', unsafe_allow_html=True)
st.markdown('<p class="subtitle">Explore revenue, profitability, product performance, and sales trends.</p>', unsafe_allow_html=True)
st.markdown("<div style='display:flex;gap:8px;flex-wrap:wrap;margin:16px 0 4px;'><span style='background:#e8f5f0;color:#116c58;padding:6px 11px;border-radius:7px;font-size:12px;font-weight:700;'>● LIVE DATA VIEW</span><span style='background:#e9eef9;color:#35548e;padding:6px 11px;border-radius:7px;font-size:12px;font-weight:700;'>SALES PERFORMANCE</span></div>", unsafe_allow_html=True)
st.divider()

# Sidebar filters
st.sidebar.markdown("## Filters")
st.sidebar.caption("Adjust selections to explore the dataset.")
filtered = df.copy()
date_col = "Order Date" if "Order Date" in filtered.columns else ("Date" if "Date" in filtered.columns else None)

if date_col:
    valid_dates = filtered[date_col].dropna()
    if not valid_dates.empty:
        min_date, max_date = valid_dates.min().date(), valid_dates.max().date()
        selected_dates = st.sidebar.date_input(
            "Order date range", value=(min_date, max_date),
            min_value=min_date, max_value=max_date,
        )
        if isinstance(selected_dates, (tuple, list)) and len(selected_dates) == 2:
            start_date, end_date = selected_dates
            filtered = filtered[
                filtered[date_col].notna()
                & filtered[date_col].dt.date.between(start_date, end_date)
            ]
        elif isinstance(selected_dates, (tuple, list)) and len(selected_dates) == 1:
            chosen = selected_dates[0]
            filtered = filtered[filtered[date_col].dt.date == chosen]

for col, label in [
    ("Region", "Region"),
    ("Category", "Category"),
    ("Segment", "Customer segment"),
    ("State", "State"),
]:
    if col in filtered.columns:
        options = sorted(filtered[col].dropna().astype(str).unique().tolist())
        selected = st.sidebar.multiselect(label, options=options, default=options)
        if selected:
            filtered = filtered[filtered[col].astype(str).isin(selected)]
        else:
            filtered = filtered.iloc[0:0]

if st.sidebar.button("Reset filters", use_container_width=True):
    st.rerun()
st.sidebar.divider()
st.sidebar.caption(f"Source: `{DATA_FILE.name}`")
st.sidebar.caption(f"{len(filtered):,} of {len(df):,} records selected")

if filtered.empty:
    st.warning("No records match these filters. Adjust or reset the selections.")
    st.stop()

# KPI cards
sales_total = filtered["Sales"].sum(skipna=True)
profit_total = filtered["Profit"].sum(skipna=True)
profit_margin = profit_total / sales_total * 100 if sales_total else 0
order_count = filtered["Order ID"].nunique()
units = filtered["Quantity"].sum(skipna=True) if "Quantity" in filtered.columns else None
avg_order_value = sales_total / order_count if order_count else 0

kpi_cols = st.columns(5)
kpi_cols[0].metric("Total sales", money(sales_total))
kpi_cols[1].metric("Total profit", money(profit_total))
kpi_cols[2].metric("Profit margin", f"{profit_margin:.2f}%")
kpi_cols[3].metric("Orders", f"{order_count:,}")
kpi_cols[4].metric("Units sold", f"{units:,.0f}" if units is not None else "N/A")
st.caption(f"Average order value: **{money(avg_order_value)}** · Showing **{len(filtered):,}** records")

# Monthly trends
st.divider()
section_title("Sales & profit trends", "Monthly performance for the selected filters.")
if date_col:
    dated = filtered.dropna(subset=[date_col]).copy()
    if not dated.empty:
        dated["Month"] = dated[date_col].dt.to_period("M").dt.to_timestamp()
        monthly = dated.groupby("Month", as_index=False).agg(Sales=("Sales", "sum"), Profit=("Profit", "sum"))
        monthly = monthly.sort_values("Month")
        left, right = st.columns([1.65, 1])
        with left:
            monthly_long = monthly.melt(id_vars="Month", value_vars=["Sales", "Profit"], var_name="Metric", value_name="Amount")
            fig = px.line(
                monthly_long, x="Month", y="Amount", color="Metric", markers=True,
                color_discrete_map={"Sales": GREEN, "Profit": BLUE},
                title="Monthly sales and profit",
                labels={"Month": "Month", "Amount": "Amount (USD)"},
            )
            fig.update_traces(line=dict(width=2.5))
            st.plotly_chart(style_chart(fig, 370), use_container_width=True)
        with right:
            monthly["Previous month sales"] = monthly["Sales"].shift(1)
            monthly["MoM growth (%)"] = np.where(
                monthly["Previous month sales"] != 0,
                (monthly["Sales"] - monthly["Previous month sales"]) / monthly["Previous month sales"] * 100,
                np.nan,
            )
            growth = monthly.dropna(subset=["MoM growth (%)"])
            if not growth.empty:
                latest = growth.iloc[-1]
                st.metric("Latest month-over-month growth", f"{latest['MoM growth (%)']:+.1f}%")
                growth_fig = px.bar(
                    growth, x="Month", y="MoM growth (%)", title="Monthly sales growth",
                    labels={"Month": "Month", "MoM growth (%)": "Growth (%)"},
                    color="MoM growth (%)", color_continuous_scale=["#c76b6b", "#f5f7f6", GREEN],
                )
                growth_fig.add_hline(y=0, line_color=SLATE, line_width=1)
                st.plotly_chart(style_chart(growth_fig, 300), use_container_width=True)
            else:
                st.info("At least two months are needed to calculate monthly growth.")
    else:
        st.info("No valid dates are available for the selected records.")
else:
    st.info("Add an Order Date or Date column to see monthly trends.")

# Category and regional performance
st.divider()
section_title("Where sales come from", "Compare revenue and profit across product categories and regions.")
col1, col2 = st.columns(2)
with col1:
    if "Category" in filtered.columns:
        cat = filtered.groupby("Category", as_index=False).agg(Sales=("Sales", "sum"), Profit=("Profit", "sum")).sort_values("Sales", ascending=True)
        fig = px.bar(cat, x="Sales", y="Category", orientation="h", title="Sales by category", color_discrete_sequence=[GREEN], labels={"Sales": "Sales (USD)", "Category": ""})
        fig.update_traces(hovertemplate="%{y}<br>Sales: $%{x:,.2f}<extra></extra>")
        st.plotly_chart(style_chart(fig, 330), use_container_width=True)
    else:
        st.info("Category column not found.")
with col2:
    if "Region" in filtered.columns:
        reg = filtered.groupby("Region", as_index=False).agg(Sales=("Sales", "sum"), Profit=("Profit", "sum")).sort_values("Sales", ascending=False)
        fig = px.pie(reg, names="Region", values="Sales", hole=.62, title="Sales mix by region", color_discrete_sequence=[GREEN, BLUE, TEAL, "#b8c9c3"])
        fig.update_traces(textposition="inside", textinfo="percent+label", hovertemplate="%{label}<br>Sales: $%{value:,.2f}<br>Share: %{percent}<extra></extra>")
        st.plotly_chart(style_chart(fig, 330), use_container_width=True)
    else:
        st.info("Region column not found.")

col3, col4 = st.columns(2)
with col3:
    if "Category" in filtered.columns:
        cat_profit = filtered.groupby("Category", as_index=False)["Profit"].sum()
        fig = px.bar(cat_profit, x="Category", y="Profit", title="Profit by category", color="Profit", color_continuous_scale=["#c76b6b", "#f5f7f6", GREEN], labels={"Category": "", "Profit": "Profit (USD)"})
        fig.add_hline(y=0, line_color=SLATE, line_width=1)
        st.plotly_chart(style_chart(fig, 310), use_container_width=True)
with col4:
    if "Region" in filtered.columns:
        region_profit = filtered.groupby("Region", as_index=False)["Profit"].sum().sort_values("Profit")
        fig = px.bar(region_profit, x="Profit", y="Region", orientation="h", title="Profit by region", color="Profit", color_continuous_scale=["#c76b6b", "#f5f7f6", GREEN], labels={"Region": "", "Profit": "Profit (USD)"})
        fig.add_vline(x=0, line_color=SLATE, line_width=1)
        st.plotly_chart(style_chart(fig, 310), use_container_width=True)

# Product and discount analysis
st.divider()
section_title("Product & discount analysis", "Find high-performing products and inspect discount-profit patterns.")
prod_col, discount_col = st.columns(2)
with prod_col:
    if "Product Name" in filtered.columns:
        top_n = st.slider("Number of products to show", 5, 20, 10, 5)
        products = filtered.groupby("Product Name", as_index=False).agg(Sales=("Sales", "sum"), Profit=("Profit", "sum")).nlargest(top_n, "Sales").sort_values("Sales", ascending=True)
        fig = px.bar(products, x="Sales", y="Product Name", orientation="h", title=f"Top {top_n} products by sales", hover_data={"Profit": ":,.2f", "Sales": ":,.2f"}, color_discrete_sequence=[BLUE], labels={"Sales": "Sales (USD)", "Product Name": ""})
        fig.update_traces(hovertemplate="%{y}<br>Sales: $%{x:,.2f}<extra></extra>")
        st.plotly_chart(style_chart(fig, max(360, top_n * 30)), use_container_width=True)
    else:
        st.info("Product Name column not found.")
with discount_col:
    if {"Discount", "Profit"}.issubset(filtered.columns):
        scatter_data = filtered.dropna(subset=["Discount", "Profit"]).copy()
        size_col = None
        if "Sales" in scatter_data.columns:
            scatter_data["Sales size"] = scatter_data["Sales"].clip(lower=0)
            size_col = "Sales size"
        fig = px.scatter(
            scatter_data, x="Discount", y="Profit", size=size_col, color="Profit",
            color_continuous_scale=["#c76b6b", "#f5f7f6", GREEN], opacity=.58,
            title="Discount vs. profit", labels={"Discount": "Discount rate", "Profit": "Profit (USD)"},
            hover_data=[c for c in ["Category", "Region", "Product Name", "Sales"] if c in scatter_data.columns],
        )
        fig.update_xaxes(tickformat=".0%")
        fig.add_hline(y=0, line_color=SLATE, line_width=1)
        st.plotly_chart(style_chart(fig, 380), use_container_width=True)
        corr = scatter_data["Discount"].corr(scatter_data["Profit"]) if len(scatter_data) > 1 else np.nan
        if pd.notna(corr):
            strength = "weak" if abs(corr) < .4 else ("moderate" if abs(corr) < .7 else "strong")
            direction = "negative" if corr < 0 else ("positive" if corr > 0 else "near-zero")
            st.caption(f"Pearson correlation: **{corr:.3f}** ({strength} {direction} linear association). Correlation does not establish causation.")
    else:
        st.info("Discount and Profit columns are required for this analysis.")

if {"Discount", "Profit"}.issubset(filtered.columns):
    discount_summary = filtered.dropna(subset=["Discount", "Profit"]).groupby("Discount", as_index=False).agg(AverageProfit=("Profit", "mean"), Records=("Profit", "size")).sort_values("Discount")
    with st.expander("View average profit by discount level"):
        discount_summary["Discount label"] = discount_summary["Discount"].map(lambda x: f"{x:.0%}")
        fig = px.bar(discount_summary, x="Discount label", y="AverageProfit", hover_data={"Records": True, "AverageProfit": ":,.2f"}, title="Average profit at each discount level", labels={"Discount label": "Discount", "AverageProfit": "Average profit (USD)"}, color="AverageProfit", color_continuous_scale=["#c76b6b", "#f5f7f6", GREEN])
        fig.add_hline(y=0, line_color=SLATE, line_width=1)
        st.plotly_chart(style_chart(fig, 320), use_container_width=True)
        st.dataframe(discount_summary[["Discount label", "AverageProfit", "Records"]].rename(columns={"Discount label": "Discount", "AverageProfit": "Average profit", "Records": "Records"}), use_container_width=True, hide_index=True)

# Dynamic insights
st.divider()
section_title("Insights for the current selection", "These statements update when filters change.")
insights = []
if "Category" in filtered.columns:
    by_category = filtered.groupby("Category")["Sales"].sum().sort_values(ascending=False)
    if len(by_category):
        insights.append(("Leading category", f"{by_category.index[0]} leads sales with {money(by_category.iloc[0])}."))
if "Region" in filtered.columns:
    by_region = filtered.groupby("Region")["Profit"].sum().sort_values(ascending=False)
    if len(by_region):
        insights.append(("Profit leader", f"{by_region.index[0]} has the highest total profit at {money(by_region.iloc[0])}."))
if "Product Name" in filtered.columns:
    by_product = filtered.groupby("Product Name")["Sales"].sum().sort_values(ascending=False)
    if len(by_product):
        insights.append(("Top product", f"{by_product.index[0]} has the highest sales at {money(by_product.iloc[0])}."))
if profit_margin < 0:
    insights.append(("Profitability alert", "Overall profit is negative for this selection. Review costs, pricing, and discount patterns."))
elif profit_margin < 5:
    insights.append(("Profitability watch", f"The overall profit margin is {profit_margin:.2f}%; review low-margin products and discounts."))
else:
    insights.append(("Profitability", f"The overall profit margin for this selection is {profit_margin:.2f}%."))

for title, body in insights:
    st.markdown(f'<div class="insight"><div class="insight-title">{title}</div><div class="insight-body">{body}</div></div>', unsafe_allow_html=True)

# Data explorer
st.divider()
section_title("Explore the data", "Inspect filtered records and export them for further analysis.")
search = st.text_input("Search visible records", placeholder="Search product, order ID, state, category…")
display_data = filtered.copy()
if search.strip():
    text_cols = display_data.select_dtypes(include=["object", "string"]).columns
    if len(text_cols):
        mask = display_data[text_cols].fillna("").astype(str).apply(lambda col: col.str.contains(search.strip(), case=False, regex=False)).any(axis=1)
        display_data = display_data[mask]
st.caption(f"{len(display_data):,} matching records")
st.dataframe(display_data, use_container_width=True, hide_index=True, height=360)
st.download_button("Download filtered data (CSV)", data=filtered.to_csv(index=False).encode("utf-8-sig"), file_name="retail_sales_filtered.csv", mime="text/csv")
st.caption("Built with Python, Pandas, Streamlit, and Plotly.")
