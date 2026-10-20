from pathlib import Path
from io import BytesIO
from urllib.parse import urlparse

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
DATA_DIR = BASE_DIR / "data"
DATA_DIR.mkdir(exist_ok=True)
GREEN, BLUE, TEAL, SLATE, GRID, TEXT = (
    "#16836b",
    "#4263a5",
    "#56a99a",
    "#748196",
    "#e8edf3",
    "#344054",
)

st.markdown(
    """
<style>
:root { --ink:#172033; --muted:#667085; --line:#e5eaf0; --accent:#16836b; }
.stApp { background:#f4f7fb; color:var(--ink); }
[data-testid="stHeader"] { background:rgba(244,247,251,.92); }
[data-testid="stSidebar"] { background:#111d2e; border-right:1px solid #253348; }
[data-testid="stSidebar"] * { color:#e8eef6; }
[data-testid="stSidebar"] [data-testid="stMarkdownContainer"] p, [data-testid="stSidebar"] label { color:#c7d2e1 !important; }
[data-testid="stSidebar"] [data-baseweb="select"] > div, [data-testid="stSidebar"] [data-baseweb="input"] > div { background:#1d2b40; border-color:#34445b; }
.block-container { max-width:1500px; padding-top:2rem; padding-bottom:3rem; }
[data-testid="stMetric"] { background:#fff; border:1px solid var(--line); padding:18px 20px; border-radius:15px; box-shadow:0 3px 12px rgba(20,36,56,.035); }
[data-testid="stMetricLabel"] { color:#667085; font-size:.86rem; font-weight:600; }
[data-testid="stMetricValue"] { color:#172033; font-size:1.6rem; font-weight:700; }
.eyebrow { color:#16836b; font-size:.72rem; font-weight:800; letter-spacing:.14em; text-transform:uppercase; margin-bottom:.45rem; }
.main-title { font-size:2.35rem; line-height:1.15; font-weight:780; color:#172033; letter-spacing:-.055em; margin:0; }
.subtitle { color:#667085; margin-top:.5rem; font-size:1rem; }
h2, h3 { color:#172033 !important; }
[data-testid="stPlotlyChart"] { background:#fff; border:1px solid var(--line); border-radius:15px; padding:8px 8px 0; }
[data-testid="stDataFrame"] { border:1px solid var(--line); border-radius:12px; overflow:hidden; }
div[data-testid="stDownloadButton"] > button { background:#16836b; color:#fff; border:1px solid #16836b; border-radius:9px; font-weight:650; }
@media (max-width:800px) { .main-title { font-size:1.8rem; } .block-container { padding-top:1.2rem; } }
</style>
""",
    unsafe_allow_html=True,
)


def read_csv_bytes(data: bytes) -> pd.DataFrame:
    try:
        frame = pd.read_csv(BytesIO(data), encoding="utf-8-sig")
    except UnicodeDecodeError:
        frame = pd.read_csv(BytesIO(data), encoding="latin1")
    frame.columns = frame.columns.astype(str).str.strip()
    # Parse common date columns and numeric-looking values without assuming a fixed schema.
    for col in frame.columns:
        if any(word in col.lower() for word in ("date", "datetime", "timestamp")):
            parsed = pd.to_datetime(frame[col], errors="coerce")
            if parsed.notna().any():
                frame[col] = parsed
    for col in frame.columns:
        if frame[col].dtype == "object":
            cleaned = (
                frame[col].astype(str).str.replace(r"[$,]", "", regex=True).str.strip()
            )
            numeric = pd.to_numeric(cleaned, errors="coerce")
            if numeric.notna().mean() >= 0.85 and numeric.notna().sum() > 0:
                frame[col] = numeric
    return frame


def money(value):
    return f"{value:,.2f}"


def style_chart(fig, height=340):
    fig.update_layout(
        height=height,
        margin=dict(l=8, r=8, t=38, b=8),
        paper_bgcolor="white",
        plot_bgcolor="white",
        font=dict(family="Arial, sans-serif", color=TEXT, size=12),
        title=dict(font=dict(size=15, color="#17212b"), x=0.01, xanchor="left"),
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1,
            title_text="",
        ),
    )
    fig.update_xaxes(showgrid=False, linecolor=GRID, zeroline=False)
    fig.update_yaxes(showgrid=True, gridcolor=GRID, zeroline=False)
    return fig


def unique_name(name, existing):
    candidate = name
    i = 2
    while candidate in existing:
        candidate = f"{name} ({i})"
        i += 1
    return candidate


st.sidebar.markdown("## Dataset")
st.sidebar.caption("Choose a saved file, upload a CSV, or load a public CSV URL.")

# Discover saved CSV files from the data folder.
saved_paths = sorted(p for p in DATA_DIR.glob("*.csv") if p.is_file())
saved_options = {p.name: p for p in saved_paths}
source_mode = st.sidebar.radio(
    "Data source", ["Saved CSV files", "Upload a CSV", "Public CSV URL"], index=0
)
df = None
source_label = ""

if source_mode == "Saved CSV files":
    if not saved_options:
        st.sidebar.info(
            f"No CSV files found in `{DATA_DIR}`. Upload one below or place CSV files in the data folder."
        )
    else:
        default_index = (
            list(saved_options).index("sales.csv")
            if "sales.csv" in saved_options
            else 0
        )
        chosen_file = st.sidebar.selectbox(
            "Select dataset", list(saved_options), index=default_index
        )
        try:
            path = saved_options[chosen_file]
            df = read_csv_bytes(path.read_bytes())
            source_label = path.name
        except Exception as exc:
            st.error(f"Could not read {chosen_file}: {exc}")
            st.stop()
elif source_mode == "Upload a CSV":
    upload = st.sidebar.file_uploader(
        "Choose a CSV file",
        type=["csv"],
        help="Your uploaded file is used for this session; it does not overwrite saved files.",
    )
    if upload is not None:
        try:
            df = read_csv_bytes(upload.getvalue())
            source_label = upload.name
        except Exception as exc:
            st.error(f"Could not read the uploaded CSV: {exc}")
            st.stop()
    else:
        st.info("Upload a CSV file in the sidebar to begin.")
        st.stop()
else:
    url = st.sidebar.text_input(
        "CSV URL", placeholder="https://example.com/dataset.csv"
    )
    st.sidebar.caption(
        "Use a direct link to a public .csv file. Private/login-only links may not work."
    )
    if not url.strip():
        st.info(
            "Enter a direct public CSV URL in the sidebar. Only load datasets from sources you trust."
        )
        st.stop()
    parsed = urlparse(url.strip())
    if parsed.scheme not in ("http", "https") or not parsed.netloc:
        st.error("Enter a valid public URL beginning with http:// or https://")
        st.stop()
    try:
        # Streamlit reruns this script; cache the URL result for a short period.
        @st.cache_data(ttl=300, show_spinner="Downloading public CSV…")
        def load_url_csv(csv_url):
            import requests

            response = requests.get(
                csv_url, timeout=20, headers={"User-Agent": "RetailSalesAnalytics/1.0"}
            )
            response.raise_for_status()
            if len(response.content) > 50 * 1024 * 1024:
                raise ValueError("CSV is larger than the 50 MB limit.")
            return read_csv_bytes(response.content)

        df = load_url_csv(url.strip())
        source_label = parsed.path.rsplit("/", 1)[-1] or parsed.netloc
    except Exception as exc:
        st.error(f"Could not load that URL as a CSV: {exc}")
        st.caption(
            "Check that the URL is a direct, publicly accessible CSV link and that the site allows downloads."
        )
        st.stop()

if df is None:
    st.info("Choose a dataset source in the sidebar to start.")
    st.stop()
if df.empty:
    st.warning("This dataset has no rows.")
    st.stop()

st.markdown('<div class="eyebrow">DATA EXPLORER</div>', unsafe_allow_html=True)
st.markdown('<p class="main-title">Retail Sales Analytics</p>', unsafe_allow_html=True)
st.markdown(
    '<p class="subtitle">Explore different CSV datasets with flexible filters, visualizations, and downloadable results.</p>',
    unsafe_allow_html=True,
)
st.caption(
    f"**Selected dataset:** {source_label} · {len(df):,} rows · {len(df.columns):,} columns"
)
st.divider()

# Generic filters: date range plus categorical columns.
filtered = df.copy()
st.sidebar.markdown("## Filters")
date_cols = [
    c for c in filtered.columns if pd.api.types.is_datetime64_any_dtype(filtered[c])
]
if date_cols:
    date_col = st.sidebar.selectbox("Date column", ["None"] + date_cols, index=1)
    if date_col != "None":
        valid_dates = filtered[date_col].dropna()
        if not valid_dates.empty:
            min_date, max_date = valid_dates.min().date(), valid_dates.max().date()
            if min_date < max_date:
                selected_dates = st.sidebar.date_input(
                    "Date range",
                    value=(min_date, max_date),
                    min_value=min_date,
                    max_value=max_date,
                )
                if (
                    isinstance(selected_dates, (tuple, list))
                    and len(selected_dates) == 2
                ):
                    start_date, end_date = selected_dates
                    filtered = filtered[
                        filtered[date_col].notna()
                        & filtered[date_col].dt.date.between(start_date, end_date)
                    ]
            else:
                st.sidebar.caption(f"Only one date: {min_date}")

categorical_cols = [
    c
    for c in filtered.columns
    if (
        pd.api.types.is_object_dtype(filtered[c])
        or isinstance(filtered[c].dtype, pd.CategoricalDtype)
    )
    and filtered[c].nunique(dropna=True) <= 50
]
preferred = [
    c
    for c in [
        "Region",
        "Category",
        "Segment",
        "State",
        "Sales_Channel",
        "Customer_Type",
        "Payment_Method",
    ]
    if c in categorical_cols
]
filter_cols = preferred + [c for c in categorical_cols if c not in preferred][:3]
for col in filter_cols:
    options = sorted(filtered[col].dropna().astype(str).unique().tolist())
    if options and len(options) <= 50:
        selected = st.sidebar.multiselect(
            col, options=options, default=options, key=f"filter_{col}_{source_label}"
        )
        if selected:
            filtered = filtered[filtered[col].astype(str).isin(selected)]
        else:
            filtered = filtered.iloc[0:0]
if st.sidebar.button("Reset filters", use_container_width=True):
    st.rerun()
st.sidebar.divider()
st.sidebar.caption(f"Source: {source_label}")
st.sidebar.caption(f"{len(filtered):,} of {len(df):,} records selected")
if filtered.empty:
    st.warning("No records match these filters. Adjust the selections.")
    st.stop()

# Numeric fields and flexible overview.
numeric_cols = filtered.select_dtypes(include=np.number).columns.tolist()
possible_sales = [
    c
    for c in numeric_cols
    if c.lower()
    in ("sales", "revenue", "total_sales", "amount", "order_amount", "price")
]
possible_profit = [
    c
    for c in numeric_cols
    if c.lower() in ("profit", "net_profit", "gross_profit", "margin_amount")
]
possible_quantity = [
    c for c in numeric_cols if c.lower() in ("quantity", "qty", "units", "units_sold")
]
metric_candidates = possible_sales + [
    c for c in numeric_cols if c not in possible_sales
]
primary_metric = (
    st.selectbox("Primary metric for charts", metric_candidates, index=0)
    if metric_candidates
    else None
)

kpi_cols = st.columns(4)
kpi_cols[0].metric("Rows", f"{len(filtered):,}")
kpi_cols[1].metric("Columns", f"{len(filtered.columns):,}")
kpi_cols[2].metric("Numeric columns", f"{len(numeric_cols):,}")
kpi_cols[3].metric("Missing cells", f"{int(filtered.isna().sum().sum()):,}")
if possible_sales:
    sales_col = possible_sales[0]
    kpi_cols = st.columns(3)
    kpi_cols[0].metric(f"Total {sales_col}", f"{filtered[sales_col].sum():,.2f}")
    if possible_profit:
        profit_col = possible_profit[0]
        kpi_cols[1].metric(f"Total {profit_col}", f"{filtered[profit_col].sum():,.2f}")
        total_sales = filtered[sales_col].sum()
        margin = filtered[profit_col].sum() / total_sales * 100 if total_sales else 0
        kpi_cols[2].metric("Profit margin", f"{margin:.2f}%")
    elif possible_quantity:
        kpi_cols[1].metric(
            f"Total {possible_quantity[0]}",
            f"{filtered[possible_quantity[0]].sum():,.2f}",
        )
        kpi_cols[2].metric(f"Average {sales_col}", f"{filtered[sales_col].mean():,.2f}")
    else:
        kpi_cols[1].metric(f"Average {sales_col}", f"{filtered[sales_col].mean():,.2f}")
        kpi_cols[2].metric(
            f"Median {sales_col}", f"{filtered[sales_col].median():,.2f}"
        )

st.divider()
st.markdown("### Dataset overview")
left, right = st.columns([1.15, 1])
with left:
    st.markdown("**Column summary**")
    summary = pd.DataFrame(
        {
            "Column": filtered.columns,
            "Data type": [str(filtered[c].dtype) for c in filtered.columns],
            "Non-null": [int(filtered[c].notna().sum()) for c in filtered.columns],
            "Missing": [int(filtered[c].isna().sum()) for c in filtered.columns],
            "Unique values": [
                int(filtered[c].nunique(dropna=True)) for c in filtered.columns
            ],
        }
    )
    st.dataframe(summary, use_container_width=True, hide_index=True, height=350)
with right:
    st.markdown("**Missing values by column**")
    missing = (
        filtered.isna()
        .sum()
        .rename("Missing values")
        .reset_index()
        .rename(columns={"index": "Column"})
    )
    missing = missing[missing["Missing values"] > 0].sort_values(
        "Missing values", ascending=True
    )
    if missing.empty:
        st.success("No missing values in the current selection.")
    else:
        fig = px.bar(
            missing,
            x="Missing values",
            y="Column",
            orientation="h",
            color_discrete_sequence=[BLUE],
            title="Missing values",
        )
        st.plotly_chart(
            style_chart(fig, max(300, len(missing) * 25)), use_container_width=True
        )

st.divider()
st.markdown("### Visual analysis")
if primary_metric:
    chart_a, chart_b = st.columns(2)
    with chart_a:
        st.markdown(f"**Distribution of {primary_metric}**")
        vals = filtered[primary_metric].dropna()
        if not vals.empty:
            fig = px.histogram(
                filtered, x=primary_metric, nbins=30, color_discrete_sequence=[GREEN]
            )
            st.plotly_chart(style_chart(fig, 340), use_container_width=True)
        else:
            st.info("No numeric values available for this metric.")
    with chart_b:
        st.markdown(f"**{primary_metric} by category**")
        group_cols = [
            c
            for c in filtered.columns
            if c in categorical_cols and filtered[c].nunique(dropna=True) <= 30
        ]
        group_col = (
            st.selectbox("Group by", group_cols, key=f"group_{source_label}")
            if group_cols
            else None
        )
        if group_col:
            grouped = (
                filtered.groupby(group_col, dropna=False)[primary_metric]
                .sum()
                .reset_index()
                .sort_values(primary_metric, ascending=False)
                .head(20)
            )
            fig = px.bar(
                grouped, x=group_col, y=primary_metric, color_discrete_sequence=[BLUE]
            )
            fig.update_layout(xaxis_title=group_col, yaxis_title=primary_metric)
            st.plotly_chart(style_chart(fig, 340), use_container_width=True)
        else:
            st.info("No suitable categorical column found for grouping.")
else:
    st.info(
        "No numeric columns were detected, so numeric charts are unavailable. You can still inspect and download the dataset below."
    )

if date_cols and primary_metric:
    available_date_cols = [c for c in date_cols if filtered[c].notna().any()]
    if available_date_cols:
        trend_date = st.selectbox(
            "Trend date column", available_date_cols, key=f"trend_date_{source_label}"
        )
        trend = filtered.dropna(subset=[trend_date]).copy()
        if not trend.empty:
            trend["Period"] = trend[trend_date].dt.to_period("M").dt.to_timestamp()
            trend = (
                trend.groupby("Period", as_index=False)[primary_metric]
                .sum()
                .sort_values("Period")
            )
            fig = px.line(
                trend,
                x="Period",
                y=primary_metric,
                markers=True,
                color_discrete_sequence=[GREEN],
                title=f"Monthly {primary_metric}",
            )
            st.plotly_chart(style_chart(fig, 350), use_container_width=True)

if len(numeric_cols) >= 2:
    with st.expander("Explore correlations between numeric columns"):
        corr_cols = st.multiselect(
            "Choose numeric columns",
            numeric_cols,
            default=numeric_cols[: min(8, len(numeric_cols))],
        )
        if len(corr_cols) >= 2:
            corr = filtered[corr_cols].corr(numeric_only=True)
            fig = px.imshow(
                corr,
                text_auto=".2f",
                aspect="auto",
                color_continuous_scale="RdBu_r",
                zmin=-1,
                zmax=1,
                title="Correlation matrix",
            )
            st.plotly_chart(style_chart(fig, 420), use_container_width=True)
        else:
            st.caption("Select at least two numeric columns.")

st.divider()
st.markdown("### Explore and export records")
search = st.text_input(
    "Search records", placeholder="Type a value to search across the visible table…"
)
display_data = filtered.copy()
if search.strip():
    mask = (
        display_data.astype(str)
        .apply(
            lambda col: col.str.contains(
                search.strip(), case=False, regex=False, na=False
            )
        )
        .any(axis=1)
    )
    display_data = display_data[mask]
st.caption(f"{len(display_data):,} matching records")
st.dataframe(display_data, use_container_width=True, hide_index=True, height=360)
st.download_button(
    "Download filtered data (CSV)",
    data=filtered.to_csv(index=False).encode("utf-8-sig"),
    file_name="filtered_dataset.csv",
    mime="text/csv",
)
st.download_button(
    "Download column summary (CSV)",
    data=summary.to_csv(index=False).encode("utf-8-sig"),
    file_name="dataset_column_summary.csv",
    mime="text/csv",
)
st.caption(
    "Built with Python, Pandas, Streamlit, NumPy, and Plotly. Online CSV URLs must be public direct-download links."
)
