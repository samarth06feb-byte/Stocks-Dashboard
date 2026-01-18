import yfinance as yf
import streamlit as st
# You may need to add 'requests' and 'requests_cache' to requirements.txt
import requests_cache 

# Create a session that caches data for 1 hour to reduce requests
session = requests_cache.CachedSession('hermes_cache', expire_after=3600)
session.headers.update({'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/115.0.0.0 Safari/537.36'})

# Then, when you call yf.Ticker, pass the session:
ticker = yf.Ticker(ticker_symbol, session=session)
import pandas as pd
import numpy as np

# 1. Page Config (Only once at the top)
st.set_page_config(layout="wide", page_title="Hermes & Jackson Terminal")
st.title("Stocks Research Terminal")

# 2. Combined Sidebar
with st.sidebar:
    st.header("Search & Portfolio Risk Settings")
    # Single Ticker Research
    ticker_symbol = st.text_input("Enter Ticker for Research", "F").upper()
    period = st.selectbox("Chart Period", ["1mo", "6mo", "1y", "5y", "max"], index=2)
    
    st.divider()
    
    # Portfolio Analysis (15 Stocks)
    st.subheader("MAX 15 Stocks")
    default_tickers = "F, RACE, OSK, DOLE, CALM, AAPL, MSFT, GOOG, TSLA, AMZN, NVDA, META, BRK-B, V, JPM"
    input_tickers = st.text_area("Portfolio Tickers (comma separated):", default_tickers)
    tickers = [t.strip().upper() for t in input_tickers.split(",")]
    
    st.divider()
   

# 3. Define the Tabs
tab1, tab2, tab3, tab4, tab5 = st.tabs([" Overview", " Financials", " News", " Analysis", " Volatility"])

# --- TAB 1: OVERVIEW ---
if ticker_symbol:
    ticker = yf.Ticker(ticker_symbol)
    info = ticker.info
    
    with tab1:
        col1, col2 = st.columns([1, 2])
        with col1:
            st.header(info.get('longName', ticker_symbol))
            st.metric("Current Price", f"${info.get('currentPrice', 'N/A')}")
            st.write(f"**Sector:** {info.get('sector', 'N/A')}")
        with col2:
            st.subheader("Performance")
            history = ticker.history(period=period)
            st.line_chart(history['Close'])

    # --- TAB 2: FINANCIALS ---
    with tab2:
        st.header("Financial Statements")
        st.info("Note: Numbers are in actual units. Use the scrollbar to see all years.")

        # Function to format numbers with commas
        def format_financials(df):
            return df[::-1].style.format("{:,.0f}")

        # 1. Income Statement
        st.subheader("Income Statement (Top Line to Bottom Line)")
        if not ticker.income_stmt.empty:
            st.dataframe(format_financials(ticker.income_stmt), use_container_width=True)
        
        # 2. Balance Sheet
        st.subheader("Balance Sheet (Assets & Liabilities)")
        if not ticker.balance_sheet.empty:
            st.dataframe(format_financials(ticker.balance_sheet), use_container_width=True)

        # 3. CASH FLOW STATEMENT (New Addition)
        st.subheader("Cash Flow Statement (The Real Money)")
        if not ticker.cash_flow.empty:
            st.dataframe(format_financials(ticker.cash_flow), use_container_width=True)
    # --- TAB 3: NEWS ---
    with tab3:
        st.subheader(f"Latest News for {ticker_symbol}")
        news = ticker.news
        if news:
            for item in news[:5]:
                st.write(f"**{item.get('title', 'No Title')}**")
                st.caption(f"Source: {item.get('publisher', 'Unknown')}")
                st.write(f"[Read Article]({item.get('link', '#')})")
                st.divider()

    # --- TAB 4: ANALYSIS ---
    with tab4:
        st.subheader("Peter Lynch Style Categorization")
        pe_ratio = info.get('forwardPE', 0)
        growth = info.get('earningsGrowth', 0)
        if pe_ratio > 0 and pe_ratio < 15:
            st.success("Category: Stalwart / Potential Value")
        elif growth and growth > 0.20:
            st.warning("Category: Fast Grower")
        else:
            st.info("Category: Monitor for Turnaround or Cyclicality")

# --- TAB 5: VOLATILITY (PORTFOLIO ANALYSIS) ---
with tab5:
    st.header("Portfolio Risk Analyzer")
    if len(tickers) > 0:
        try:
            data = yf.download(tickers, period="1y")['Close']
            returns = data.pct_change().dropna()
            volatility = returns.std() * np.sqrt(252) * 100
            
            vol_df = pd.DataFrame(volatility, columns=["Volatility (%)"]).sort_values(by="Volatility (%)", ascending=False)
            
            c1, c2 = st.columns([1, 2])
            with c1:
                st.dataframe(vol_df.style.format("{:.2f}%"))
            with c2:
                st.bar_chart(vol_df)
                
            avg_vol = volatility.mean()
            st.subheader(f"Average Portfolio Volatility: {avg_vol:.2f}%")
            
            if avg_vol > 30:
                st.error("Risk Level: HIGH (Aggressive/Fast Growers)")
            elif avg_vol > 15:
                st.warning("Risk Level: MODERATE (Stalwarts & Cyclicals)")
            else:
                st.success("Risk Level: LOW (Conservative)")
        except Exception as e:
            st.error(f"Error analyzing portfolio: {e}")
