import streamlit as st
import yfinance as yf
import pandas as pd

# Set page to wide mode for a more professional look
st.set_page_config(layout="wide", page_title="Hermes & Jackson Terminal")

st.title("Stock Research Terminal")

# SIDEBAR: For user inputs and global settings
with st.sidebar:
    st.header("Search & Settings")
    ticker_symbol = st.text_input("Enter Ticker", "F").upper()
    period = st.selectbox("Chart Period", ["1mo", "6mo", "1y", "5y", "max"], index=2)
    st.divider()
    

# FETCH DATA
if ticker_symbol:
    ticker = yf.Ticker(ticker_symbol)
    info = ticker.info
    
    # MAIN TABS: Organize your research
    tab1, tab2, tab3, tab4 = st.tabs(["📊 Overview", "📈 Financials", "📰 News", "⚙️ Analysis"])

    # TAB 1: OVERVIEW
    with tab1:
        col1, col2 = st.columns([1, 2])
        with col1:
            st.header(info.get('longName', ticker_symbol))
            st.write(f"**Sector:** {info.get('sector', 'N/A')}")
            st.write(f"**Industry:** {info.get('industry', 'N/A')}")
            st.metric("Current Price", f"${info.get('currentPrice', 'N/A')}")
        
        with col2:
            st.subheader("Stock Performance")
            history = ticker.history(period=period)
            st.line_chart(history['Close'])

    # TAB 2: FINANCIALS (Income Statement & Balance Sheet)
    with tab2:
        st.subheader("Annual Income Statement")
        st.dataframe(ticker.income_stmt)
        
        st.subheader("Balance Sheet")
        st.dataframe(ticker.balance_sheet)

    # TAB 3: NEWS (Stay updated on brands)
    with tab3:
        st.subheader(f"Latest News for {ticker_symbol}")
        news = ticker.news
        for item in news[:5]: # Show top 5 news stories
            
            st.caption(f"Source: {item['publisher']}")
            st.write(f"[Read Article]({item['link']})")
            st.divider()

    # TAB 4: ANALYSIS (Peter Lynch Style Categorization)
    with tab4:
        st.subheader("Fundamental Analysis")
        pe_ratio = info.get('forwardPE', 0)
        growth = info.get('earningsGrowth', 0)
        
        st.write(f"**Forward P/E:** {pe_ratio}")
        
        # Categorization Logic
        if pe_ratio > 0 and pe_ratio < 15:
            st.success("Category: Potential Value/Stalwart")
        elif growth and growth > 0.20:
            st.warning("Category: Fast Grower")
        else:
            st.info("Category: Monitor for Turnaround or Cyclicality")
