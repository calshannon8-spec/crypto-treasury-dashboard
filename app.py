import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="Crypto Treasury Dashboard", layout="wide")

st.title("💰 Crypto Treasury Dashboard")

# Sidebar
st.sidebar.header("Settings")
tickers = st.sidebar.multiselect(
    "Select assets",
    ["BTC-USD", "ETH-USD", "SOL-USD", "AVAX-USD", "DOGE-USD"],
    default=["BTC-USD", "ETH-USD"]
)

period = st.sidebar.selectbox(
    "Time period",
    ["1mo", "3mo", "6mo", "1y", "2y", "5y"],
    index=2
)

# New options
view = st.sidebar.radio(
    "View mode",
    ["Price (USD)", "Percent Change (%)"]
)

log_scale = st.sidebar.checkbox("Log scale", value=False)

# Fetch price data
if tickers:
    data = yf.download(tickers, period=period)["Adj Close"]

    if isinstance(data, pd.Series):
        data = data.to_frame()

    if view == "Percent Change (%)":
        df = data.pct_change().cumsum() * 100
        y_label = "Cumulative Change (%)"
    else:
        df = data
        y_label = "Price (USD)"

    df = df.reset_index().melt(id_vars="Date", var_name="Ticker", value_name=y_label)

    fig = px.line(
        df,
        x="Date",
        y=y_label,
        color="Ticker",
        title="Price history",
        log_y=log_scale
    )
    st.plotly_chart(fig, use_container_width=True)

else:
    st.warning("Please select at least one asset.")
