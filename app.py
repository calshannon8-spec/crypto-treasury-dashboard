import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="Crypto Treasury Dashboard", layout="wide")

st.title("💰 Crypto Treasury Dashboard")

# --- Sidebar Settings ---
st.sidebar.header("Settings")

assets = st.sidebar.multiselect(
    "Select Assets to Track",
    ["BTC-USD", "ETH-USD", "SOL-USD", "ADA-USD", "DOGE-USD"],
    default=["BTC-USD", "ETH-USD"]
)

period = st.sidebar.selectbox(
    "Time Period",
    ["1mo", "3mo", "6mo", "1y", "2y", "5y"],
    index=2
)

# --- Data Loader ---
@st.cache_data
def load_prices(tickers, period):
    try:
        data = yf.download(tickers, period=period)
        if "Adj Close" in data.columns:  
            data = data["Adj Close"]
        return data
    except Exception as e:
        st.error(f"Error fetching data: {e}")
        return pd.DataFrame()

# --- Main Display ---
if assets:
    try:
        prices = load_prices(assets, period)
        if not prices.empty:
            st.subheader("Price History")
            fig = px.line(
                prices,
                x=prices.index,
                y=prices.columns,
                labels={"value": "Price (USD)", "index": "Date"},
                title=f"Price Trends ({period})"
            )
            st.plotly_chart(fig, use_container_width=True)

            st.subheader("Summary Statistics")
            st.dataframe(prices.describe())
        else:
            st.warning("No price data returned. Try a different ticker

