import sys
from pathlib import Path

import plotly.express as px
import streamlit as st


# Make src folder importable
PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_PATH = PROJECT_ROOT / "src"
sys.path.append(str(SRC_PATH))

from read_data import (
    get_available_symbols,
    get_latest_prices,
    get_pipeline_runs,
    get_symbol_performance,
)


@st.cache_data(ttl=3600)
def load_available_symbols():
    return get_available_symbols()


@st.cache_data(ttl=3600)
def load_symbol_performance(symbol: str):
    return get_symbol_performance(symbol)


@st.cache_data(ttl=3600)
def load_latest_prices():
    return get_latest_prices()


@st.cache_data(ttl=3600)
def load_pipeline_runs():
    return get_pipeline_runs()


st.set_page_config(
    page_title="Market Data Dashboard",
    page_icon="📈",
    layout="wide",
)


# -----------------------------
# Header
# -----------------------------
st.title("📈 Market Data Dashboard")
st.caption(
    "End-to-end stock and ETF market data pipeline using Alpha Vantage, PostgreSQL and Streamlit."
)


# -----------------------------
# Load data
# -----------------------------
symbols = load_available_symbols()

if not symbols:
    st.warning("No symbols found. Run the pipeline first.")
    st.stop()


# -----------------------------
# Sidebar
# -----------------------------
st.sidebar.header("Dashboard filters")

selected_symbol = st.sidebar.selectbox(
    "Select a symbol",
    symbols,
)

st.sidebar.markdown("---")
st.sidebar.caption("Data source: PostgreSQL analytics views")


symbol_performance = load_symbol_performance(selected_symbol)
latest_prices = load_latest_prices()
pipeline_runs = load_pipeline_runs()

if symbol_performance.empty:
    st.warning(f"No performance data found for {selected_symbol}.")
    st.stop()


# -----------------------------
# Prepare selected-symbol values
# -----------------------------
symbol_performance_sorted = symbol_performance.sort_values("price_date")

latest_row = symbol_performance_sorted.iloc[-1]

latest_date = latest_row["price_date"]
latest_close = latest_row["close_price"]
latest_volume = latest_row["volume"]
daily_return_pct = latest_row["daily_return_pct"]
total_return_pct = latest_row["cumulative_return_pct"]


# -----------------------------
# KPI cards
# -----------------------------
st.subheader(f"Overview: {selected_symbol}")

kpi_col1, kpi_col2, kpi_col3, kpi_col4, kpi_col5 = st.columns(5)

kpi_col1.metric(
    label="Latest close price",
    value=f"${latest_close:,.2f}",
)

kpi_col2.metric(
    label="Latest date",
    value=str(latest_date),
)

kpi_col3.metric(
    label="Latest volume",
    value=f"{latest_volume:,.0f}",
)

if daily_return_pct is not None:
    kpi_col4.metric(
        label="Daily return",
        value=f"{daily_return_pct:.2f}%",
    )
else:
    kpi_col4.metric(
        label="Daily return",
        value="N/A",
    )

if total_return_pct is not None:
    kpi_col5.metric(
        label="Total return",
        value=f"{total_return_pct:.2f}%",
    )
else:
    kpi_col5.metric(
        label="Total return",
        value="N/A",
    )


# -----------------------------
# Tabs
# -----------------------------
tab_overview, tab_prices, tab_returns, tab_data, tab_pipeline = st.tabs(
    [
        "Overview",
        "Price history",
        "Returns",
        "Data tables",
        "Pipeline monitoring",
    ]
)


# -----------------------------
# Overview tab
# -----------------------------
with tab_overview:
    st.subheader("Latest prices")

    if latest_prices.empty:
        st.info("No latest prices available.")
    else:
        st.dataframe(
            latest_prices,
            width="stretch",
            hide_index=True,
        )

    st.subheader(f"Close price trend: {selected_symbol}")

    fig_price_overview = px.line(
        symbol_performance_sorted,
        x="price_date",
        y="close_price",
        title=f"{selected_symbol} close price over time",
        markers=True,
    )

    fig_price_overview.update_layout(
        xaxis_title="Date",
        yaxis_title="Close price",
    )

    st.plotly_chart(fig_price_overview, width="stretch")


# -----------------------------
# Price history tab
# -----------------------------
with tab_prices:
    st.subheader(f"Price history: {selected_symbol}")

    fig_price = px.line(
        symbol_performance_sorted,
        x="price_date",
        y="close_price",
        title=f"{selected_symbol} close price history",
        markers=True,
    )

    fig_price.update_layout(
        xaxis_title="Date",
        yaxis_title="Close price",
    )

    st.plotly_chart(fig_price, width="stretch")

    st.subheader(f"Volume history: {selected_symbol}")

    fig_volume = px.bar(
        symbol_performance_sorted,
        x="price_date",
        y="volume",
        title=f"{selected_symbol} trading volume over time",
    )

    fig_volume.update_layout(
        xaxis_title="Date",
        yaxis_title="Volume",
    )

    st.plotly_chart(fig_volume, width="stretch")


# -----------------------------
# Returns tab
# -----------------------------
with tab_returns:
    st.subheader(f"Cumulative return: {selected_symbol}")

    fig_return = px.line(
        symbol_performance_sorted,
        x="price_date",
        y="cumulative_return_pct",
        title=f"{selected_symbol} cumulative return over time",
        markers=True,
    )

    fig_return.update_layout(
        xaxis_title="Date",
        yaxis_title="Cumulative return (%)",
    )

    st.plotly_chart(fig_return, width="stretch")

    st.subheader(f"Daily returns: {selected_symbol}")

    fig_daily_returns = px.bar(
        symbol_performance_sorted,
        x="price_date",
        y="daily_return_pct",
        title=f"{selected_symbol} daily return (%)",
    )

    fig_daily_returns.update_layout(
        xaxis_title="Date",
        yaxis_title="Daily return (%)",
    )

    st.plotly_chart(fig_daily_returns, width="stretch")

    st.subheader("Latest return rows")

    st.dataframe(
        symbol_performance_sorted.sort_values("price_date", ascending=False).head(10),
        width="stretch",
        hide_index=True,
    )


# -----------------------------
# Data tables tab
# -----------------------------
with tab_data:
    st.subheader(f"Latest rows: {selected_symbol}")

    st.dataframe(
        symbol_performance_sorted.sort_values("price_date", ascending=False).head(20),
        width="stretch",
        hide_index=True,
    )

    st.subheader("All latest prices")

    if latest_prices.empty:
        st.info("No latest prices available.")
    else:
        st.dataframe(
            latest_prices,
            width="stretch",
            hide_index=True,
        )


# -----------------------------
# Pipeline monitoring tab
# -----------------------------
with tab_pipeline:
    st.subheader("Pipeline runs")

    if pipeline_runs.empty:
        st.info("No pipeline runs found.")
    else:
        st.dataframe(
            pipeline_runs,
            width="stretch",
            hide_index=True,
        )

        latest_pipeline_run = pipeline_runs.iloc[0]

        st.markdown("### Latest pipeline run")

        run_col1, run_col2, run_col3 = st.columns(3)

        run_col1.metric(
            label="Status",
            value=latest_pipeline_run.get("status", "N/A"),
        )

        run_col2.metric(
            label="Records loaded",
            value=latest_pipeline_run.get("records_loaded", "N/A"),
        )

        run_col3.metric(
            label="Started at",
            value=str(latest_pipeline_run.get("started_at", "N/A")),
        )