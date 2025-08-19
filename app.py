import streamlit as st
import pandas as pd
import yfinance as yf
import plotly.express as px

st.set_page_config(page_title="Crypto Treasury Dashboard", layout="wide")

# Title
st.title("💰 Crypto Treasury Dashboard")

# Sidebar for user input
st.sidebar.header("Settings")
tickers = st.sidebar.multiselect(
    "Select Assets to Track",
    ["BTC-USD", "ETH-USD", "SOL-USD"],
    default=["BTC-USD", "ETH-USD"]
)
period = st.sidebar.selectbox("Time Period", ["1mo", "3mo", "6mo", "1y", "5y"], index=2)

# Fetch price data
if tickers:
    data = yf.download(tickers, period=period)["Adj Close"]
    st.subheader("Price History")
    fig = px.line(data, x=data.index, y=data.columns, title="Crypto Prices")
    st.plotly_chart(fig, use_container_width=True)

    # Simple stats
    st.subheader("Summary Statistics")
    st.write(data.describe())

else:
    st.warning("Please select at least one asset from the sidebar.")

st.markdown("---")
st.caption("Built with Streamlit 🚀")

