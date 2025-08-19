import streamlit as st
import pandas as pd
import yfinance as yf
import plotly.express as px

st.set_page_config(page_title="Crypto Treasury Dashboard", layout="wide")
st.title("Crypto Treasury Dashboard")

# ----- Sidebar -----
st.sidebar.header("Settings")
assets = st.sidebar.multiselect(
    "Select assets",
    ["BTC-USD", "ETH-USD", "SOL-USD", "ADA-USD", "DOGE-USD"],
    default=["BTC-USD", "ETH-USD"]
)
period = st.sidebar.selectbox("Time period", ["1mo", "3mo", "6mo", "1y", "2y", "5y"], index=2)

# ----- Data loader -----
@st.cache_data
def load_prices(tickers, period):
    # auto_adjust -> returns adjusted prices; progress=False avoids log noise
    df = yf.download(tickers, period=period, auto_adjust=True, progress=False)
    # Normalize to a simple 2D DataFrame of close prices
    if isinstance(df.columns, pd.MultiIndex):
        if "Close" in df.columns.get_level_values(0):
            prices = df["Close"]
        else:
            # fall back to first level if "Close" is not present
            prices = df[df.columns.levels[0][0]]
    else:
        # Single ticker
        if "Close" in df.columns:
            prices = df[["Close"]].rename(columns={"Close": tickers[0] if isinstance(tickers, list) else tickers})
        else:
            prices = df
    # Ensure plain column names (tickers)
    if isinstance(prices.columns, pd.MultiIndex):
        if "Close" in prices.columns.get_level_values(0):
            prices.columns = prices.columns.get_level_values(1)
        else:
            prices.columns = prices.columns.get_level_values(0)
    return prices

# ----- Main -----
if assets:
    try:
        prices = load_prices(assets, period)
        if not prices.empty:
            st.subheader("Price history")
            fig = px.line(prices, x=prices.index, y=prices.columns,
                          labels={"value": "Price (USD)", "index": "Date"})
            st.plotly_chart(fig, use_container_width=True)

            st.subheader("Summary statistics")
            st.dataframe(prices.describe())
        else:
            st.warning("No price data returned. Try a different ticker or time period.")
    except Exception as e:
        st.error(f"Error fetching data: {e}")
else:
    st.info("Pick at least one asset from the sidebar to begin.")

