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
    get_cumulative_returns,
    get_latest_prices,
    get_pipeline_runs,
    get_price_history,
)


st.set_page_config(
    page_title="Market Data Dashboard",
    page_icon="📈",
    layout="wide",
)

st.title("Market Data Dashboard")
st.caption("Stock and ETF price data loaded from PostgreSQL")

symbols = get_available_symbols()

if not symbols:
    st.warning("No symbols found. Run the pipeline first.")
    st.stop()

selected_symbol = st.selectbox(
    "Select a symbol",
    symbols,
)

price_history = get_price_history(selected_symbol)
cumulative_returns = get_cumulative_returns(selected_symbol)
latest_prices = get_latest_prices()
pipeline_runs = get_pipeline_runs()

if price_history.empty:
    st.warning(f"No price history found for {selected_symbol}.")
    st.stop()

# Latest prices section
st.subheader("Latest prices")
st.dataframe(latest_prices, width="stretch")

# Close price chart
st.subheader(f"Close price history: {selected_symbol}")

fig_price = px.line(
    price_history,
    x="price_date",
    y="close_price",
    title=f"{selected_symbol} close price over time",
    markers=True,
)

st.plotly_chart(fig_price, width="stretch")

# Cumulative return chart
st.subheader(f"Cumulative return: {selected_symbol}")

fig_return = px.line(
    cumulative_returns,
    x="price_date",
    y="cumulative_return_pct",
    title=f"{selected_symbol} cumulative return over time",
    markers=True,
)

st.plotly_chart(fig_return, width="stretch")

# Latest rows section
st.subheader(f"Latest rows: {selected_symbol}")

st.dataframe(
    price_history.sort_values("price_date", ascending=False).head(10),
    width="stretch",
)

# Pipeline monitoring section
st.subheader("Pipeline runs")

st.dataframe(
    pipeline_runs,
    width="stretch",
)
