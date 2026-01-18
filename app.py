import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np

# 1. Page Config
st.set_page_config(layout="wide", page_title="Hermes & Jackson Terminal")
st.title("Stocks Research Terminal")

# 2. CACHED DATA FETCHING (The "Security Layer")
@st.cache_data(ttl=3600)
def get_stock_data(symbol):
    try:
        ticker = yf.Ticker(symbol)
        # We fetch both the heavy info AND the fast_info to be safe
        # Fast_info is less likely to trigger rate limits
        return ticker, ticker.info, ticker.fast_info
    except Exception:
        return None, None, None

# 3. SIDEBAR
with st.sidebar:
    st.header("Hermes & Jackson Settings")
    ticker_symbol = st.text_input("Enter Ticker for Research", "F").upper()
    period = st.selectbox("Chart Period", ["1mo", "6mo", "1y", "5y", "max"], index=2)
    st.divider()
    
    st.subheader("Portfolio Analysis")
    default_tickers = "F, RACE, OSK, DOLE, CALM, AAPL, MSFT, GOOG, TSLA, AMZN, NVDA, META, BRK-B, V, JPM"
    input_tickers = st.text_area("Portfolio Tickers:", default_tickers)
    tickers = [t.strip().upper() for t in input_tickers.split(",")]

# 4. DEFINE TABS ONCE
tab1, tab2, tab3, tab4, tab5 = st.tabs(["Overview", "Financials", "News", "Analysis", "Volatility"])

# 5. EXECUTION BLOCK
if ticker_symbol:
    ticker, info, fast_info = get_stock_data(ticker_symbol)
    
    # Check if we got data back
    if ticker and info and 'longName' in info:
        
        # --- TAB 1: OVERVIEW ---
        with tab1:
            col1, col2 = st.columns([1, 2])
            with col1:
                st.header(info.get('longName', ticker_symbol))
                # Fallback to fast_info if price is missing in heavy info
                price = info.get('currentPrice') or fast_info.get('last_price', 'N/A')
                st.metric("Current Price", f"${price}")
                st.write(f"**Sector:** {info.get('sector', 'N/A')}")
                st.write(f"**Industry:** {info.get('industry', 'N/A')}")
            with col2:
                st.subheader("Performance")
                history = ticker.history(period=period)
                st.line_chart(history['Close'])

        # --- TAB 2: FINANCIALS ---
        with tab2:
            st.header("Financial Statements")
            def format_financials(df):
                return df[::-1].style.format("{:,.0f}")

            st.subheader("Income Statement")
            if not ticker.income_stmt.empty:
                st.dataframe(format_financials(ticker.income_stmt), use_container_width=True)
            
            st.subheader("Balance Sheet")
            if not ticker.balance_sheet.empty:
                st.dataframe(format_financials(ticker.balance_sheet), use_container_width=True)

        # --- TAB 3: NEWS ---
        with tab3:
            st.subheader(f"Latest News")
            news = ticker.news
            if news:
                for item in news[:5]:
                    st.write(f"**{item.get('title')}**")
                    st.write(f"[Read Article]({item.get('link')})")
                    st.divider()

        # --- TAB 4: ANALYSIS (Peter Lynch Style) ---
        with tab4:
            st.subheader("Categorization")
            pe_ratio = info.get('forwardPE', 0)
            growth = info.get('earningsGrowth', 0)
            
            # Use logic to categorize based on your Saved Info
            if pe_ratio > 0 and pe_ratio < 15:
                st.success("Category: Stalwart / Potential Value")
            elif growth and growth > 0.20:
                st.warning("Category: Fast Grower")
            else:
                st.info("Category: Monitor for Turnaround or Cyclicality")

    else:
        st.error("Rate Limit reached or Invalid Ticker. Please wait a few minutes or try a different stock.")

# --- TAB 5: VOLATILITY (PORTFOLIO) ---
with tab5:
    st.header("Portfolio Risk Analyzer")
    if tickers:
        try:
            # Download bulk data (Separate call to avoid crashing the main research)
            data = yf.download(tickers, period="1y")['Close']
            returns = data.pct_change().dropna()
            volatility = returns.std() * np.sqrt(252) * 100
            
            vol_df = pd.DataFrame(volatility, columns=["Volatility (%)"]).sort_values(by="Volatility (%)", ascending=False)
            st.bar_chart(vol_df)
            st.write(f"Average Portfolio Volatility: **{volatility.mean():.2f}%**")
        except Exception as e:
            st.error("Could not run portfolio analysis. Yahoo may be limiting bulk downloads.")
