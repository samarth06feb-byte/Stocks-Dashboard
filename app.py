import streamlit as st
import yfinance as yf

st.title("Stock Research Terminal")

ticker = st.text_input("Enter Ticker Symbol (e.g., TSLA, F, AAPL):", "F")

if ticker:
    data = yf.Ticker(ticker)
    info = data.info
    
    st.header(f"{info.get('longName', ticker)}")
    
    # Financial Highlights
    col1, col2, col3 = st.columns(3)
    col1.metric("Price", f"${info.get('currentPrice', 'N/A')}")
    col2.metric("Forward P/E", info.get('forwardPE', 'N/A'))
    col3.metric("Market Cap", f"{info.get('marketCap', 0):,}")

    # Sector & Business Summary
    st.write(f"**Sector:** {info.get('sector', 'Unknown')}")
    st.write(info.get('longBusinessSummary', 'No summary available.'))

    # Historical Chart
    chart_data = data.history(period="1y")
    st.line_chart(chart_data['Close'])
