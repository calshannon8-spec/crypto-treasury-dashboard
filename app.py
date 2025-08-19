if tickers:
    try:
        prices = load_prices(tickers, period)
        if not prices.empty:
            st.subheader("Price history")
            fig = px.line(prices, x=prices.index, y=prices.columns,
                          labels={"value": "Price (USD)", "index": "Date"})
            st.plotly_chart(fig, use_container_width=True)

            st.subheader("Summary stats")
            st.dataframe(prices.describe())
        else:
            st.warning("No data returned. Try a different ticker or time period.")
    except Exception as e:
        st.error(f"Error fetching data: {e}")  # ✅ parentheses closed
else:
    st.info("Pick at least one asset from the sidebar.")
