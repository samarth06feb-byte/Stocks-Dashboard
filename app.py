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
    tab1, tab2, tab3, tab4, tab5 = st.tabs([" Overview", " Financials", " News", " Analysis", "Volatility of Portfolio"])

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

   # TAB 3: NEWS (Updated to prevent KeyError)
    with tab3:
        st.subheader(f"Latest News for {ticker_symbol}")
        news = ticker.news
        if news:
            for item in news[:5]:
                st.write(f"**{item.get('title', 'No Title')}**")
                # Using .get ensures if 'publisher' is missing, it won't crash
                st.caption(f"Source: {item.get('publisher', 'Unknown Source')}")
                st.write(f"[Read Article]({item.get('link', '#')})")
                st.divider()
        else:
            st.write("No recent news found for this ticker.")

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
            
    # TAB 5: VOLATILITY For Portfolio
    with tab5:
    import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np

st.set_page_config(layout="wide", page_title="H&J Portfolio Risk Terminal")

st.title("Portfolio Risk Analyzer")

# SIDEBAR for 15 Tickers
with st.sidebar:
    st.header("Your 15 Stocks")
    # Default list including your interests (Defense, Auto, Food)
    default_tickers = "F, RACE, OSK, DOLE, CALM, AAPL, MSFT, GOOG, TSLA, AMZN, NVDA, META, BRK-B, V, JPM"
    input_tickers = st.text_area("Enter 15 Tickers (comma separated):", default_tickers)
    tickers = [t.strip().upper() for t in input_tickers.split(",")]
    
    st.divider()
    st.info("Analyzing Annualized Volatility & Risk")

if len(tickers) > 0:
    try:
        # 1. DOWNLOAD DATA
        data = yf.download(tickers, period="1y")['Close']
        
        # 2. CALCULATE DAILY RETURNS
        returns = data.pct_change().dropna()
        
        # 3. CALCULATE VOLATILITY (Standard Deviation)
        # Annualized Volatility = Daily SD * Square Root of 252 trading days
        volatility = returns.std() * np.sqrt(252) * 100
        
        # 4. DISPLAY RESULTS
        st.subheader("Portfolio Volatility Overview (Annualized)")
        
        # Create a clean table for the 15 stocks
        vol_df = pd.DataFrame(volatility, columns=["Volatility (%)"]).sort_values(by="Volatility (%)", ascending=False)
        
        col1, col2 = st.columns([1, 2])
        
        with col1:
            st.dataframe(vol_df.style.format("{:.2f}%"))
            
        with col2:
            st.bar_chart(vol_df)

        # 5. RISK SUMMARY
        st.divider()
        avg_vol = volatility.mean()
        st.subheader(f"Average Portfolio Volatility: {avg_vol:.2f}%")
        
        if avg_vol > 30:
            st.error("Risk Level: HIGH (Aggressive Growth/Fast Growers)")
        elif avg_vol > 15:
            st.warning("Risk Level: MODERATE (Stalwarts & Cyclicals)")
        else:
            st.success("Risk Level: LOW (Conservative/Slow Growers)")

    except Exception as e:
            st.error(f"Please ensure tickers are correct. Error: {e}")
        
       
       
