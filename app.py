import streamlit as st
import pandas as pd
import yfinance as yf
import plotly.express as px

st.set_page_config(page_title="Crypto Treasury Dashboard", layout="wide")
st.title("Crypto Treasury Dashboard")

# ---------------- Sidebar ----------------
st.sidebar.header("Settings")
tickers = st.sidebar.multiselect(
    "Select assets",
    ["BTC-USD", "ETH-USD", "SOL-USD", "AVAX-USD", "DOGE-USD"],
    default=["BTC-USD", "ETH-USD"]
)
period = st.sidebar.selectbox("Time period", ["1mo", "3mo", "6mo", "1y", "2y", "5y"], index=2)

# Comparison options
view = st.sidebar.radio(
    "Comparison mode",
    ["Price (USD)", "Rebased to 100", "Daily % change", "Cumulative return"],
    index=1
)
log_scale = st.sidebar.checkbox("Log scale (only for Price view)", value=False)

# --------------- Data loader ---------------
@st.cache_data
def load_close_prices(symbols, per):
    """
    Download prices with auto_adjust so we get adjusted closes.
    Normalize to a simple 2D DataFrame of close prices (columns=tickers).
    """
    if not symbols:
        return pd.DataFrame()

    # auto_adjust=True returns a frame with columns like ['Close'] (or MultiIndex for multi-tickers)
    df = yf.download(symbols, period=per, auto_adjust=True, progress=False)

    # MultiIndex (multiple tickers): level 0 is price field, level 1 is ticker
    if isinstance(df.columns, pd.MultiIndex):
        if "Close" in df.columns.get_level_values(0):
            prices = df["Close"]
        else:
            # take the first available price field as a fallback
            prices = df[df.columns.levels[0][0]]
            # in some cases this may still be MultiIndex; reduce to tickers
            if isinstance(prices.columns, pd.MultiIndex):
                prices.columns = prices.columns.get_level_values(1)
    else:
        # Single ticker: columns might include 'Close' (preferred)
        if "Close" in df.columns:
            prices = df[["Close"]]
        else:
            # fallback to the first numeric column
            prices = df.select_dtypes("number")
        # rename column to the ticker symbol
        col_name = symbols[0] if isinstance(symbols, list) else symbols
        prices = prices.rename(columns={prices.columns[0]: col_name})

    # Ensure column names are plain strings (tickers)
    if isinstance(prices.columns, pd.MultiIndex):
        prices.columns = prices.columns.get_level_values(-1)

    return prices

# ---------------- Main ----------------
if not tickers:
    st.info("Pick at least one asset from the sidebar to begin.")
else:
    try:
        prices = load_close_prices(tickers, period)

        if prices.empty:
            st.warning("No price data returned. Try a different ticker or time period.")
        else:
            # Build comparison view
            to_plot = prices.copy()
            if view == "Rebased to 100":
                to_plot = (to_plot / to_plot.iloc[0]) * 100
                y_label = "Index (start = 100)"
            elif view == "Daily % change":
                to_plot = to_plot.pct_change() * 100
                y_label = "Daily change (%)"
            elif view == "Cumulative return":
                to_plot = (1 + to_plot.pct_change()).cumprod() - 1
                to_plot = to_plot * 100
                y_label = "Cumulative return (%)"
            else:
                y_label = "Price (USD)"

            st.subheader("Price history" if view == "Price (USD)" else view)

            fig = px.line(
                to_plot,
                x=to_plot.index,
                y=to_plot.columns,
                labels={"value": y_label, "index": "Date"}
            )
            if view == "Price (USD)" and log_scale:
                fig.update_yaxes(type="log")

            st.plotly_chart(fig, use_container_width=True)

            st.subheader("Summary statistics")
            st.dataframe(prices.describe())

    except Exception as e:
        st.error(f"Error fetching or displaying data: {e}")

