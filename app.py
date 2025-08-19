import streamlit as st
import pandas as pd
import yfinance as yf
import plotly.express as px

st.set_page_config(page_title="Crypto Treasury Dashboard", layout="wide")
st.title("💰 Crypto Treasury Dashboard")

st.sidebar.header("Settings")
tickers = st.sidebar.multiselect(
    "Select Assets to Track", ["BTC-USD", "ETH-USD", "SOL-USD"],
    default=["BTC-USD", "ETH-USD"]
)
period = st.sidebar.selectbox("Time Period", ["1mo", "3mo", "6mo", "1y", "5y"], index=2)

def load_prices(tickers, period):
    # auto_adjust=True returns only 'Close' (adjusted)
    df = yf.download(tickers, period=period, auto_adjust=True, progress=False)

    # If multiple tickers, yfinance returns a MultiIndex with price fields
    # When auto_adjust=True it's usually just 'Close'. Normalize to a 2D frame of close prices.
    if isinstance(df.columns, pd.MultiIndex):
        if "Close" in df.columns.get_level_values(0):
            close = df["Close"]
        elif "Adj Close" in df.columns.get_level_values(0):
            close = df["Adj Close"]
        else:
            # fallback: take the first level (price field) available
            lvl0 = df.columns.levels[0][0]
            close = df[lvl0]
    else:
        # Single ticker → a Series/DataFrame with columns like ['Close']
        if "Close" in df.columns:
            close = df[["Close"]].rename(columns={"Close": tickers[0] if isinstance(tickers, list) else tickers})
        elif "Adj Close" in df.columns:
            close = df[["Adj Close"]].rename(columns={"Adj Close": tickers[0] if isinstance(tickers, list) else tickers})
        else:
            close = df

    # Ensure columns are just ticker symbols
    if isinstance(close.columns, pd.MultiIndex):
        close.columns = close.columns.get_level_values(0)  # tickers on level 1 in some versions
        if len(set(close.columns)) != close.shape[1]:
            close.columns = close.columns.get_level_values(1)

    return close

if tickers:
    try:
        prices = load_prices(tickers, period)
        if not prices.empty:
            st.subheader("Price history")
            fig = px.line(prices, x=prices.index, y=prices.columns, labels={"value":"Price (USD)", "index":"Date"})
            st.plotly_chart(fig, use_container_width=True)

            st.subheader("Summary stats")
            st.dataframe(prices.describe())
        else:
            st.warning("No data returned. Try a different ticker or time period.")
    except Exception as e:
        st.error(
