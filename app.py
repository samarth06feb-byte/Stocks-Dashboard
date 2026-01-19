import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
from alpha_vantage.timeseries import TimeSeries

# 1. Page Config
st.set_page_config(layout="wide", page_title="Sam Terminal")
st.title("Stock Research Terminal")

# 2. DATA ENGINES (Cached)
@st.cache_data(ttl=3600)
def get_yahoo_data(symbol):
    try:
        t = yf.Ticker(symbol)
        # We fetch info only once and return it as a dict
        return t.info
    except:
        return None

@st.cache_data(ttl=3600)
def get_backup_price(symbol):
    """Emergency Engine: Alpha Vantage Price"""
    try:
        api_key = st.secrets["AV_API_KEY"]
        ts = TimeSeries(key=api_key, output_format='pandas')
        data, _ = ts.get_quote_endpoint(symbol=symbol)
        return float(data['05. price'].iloc[0])
    except:
        return None

# 3. SIDEBAR
with st.sidebar:
    st.header("Terminal Settings")
    ticker_symbol = st.text_input("Enter Ticker", "F").upper()
    period = st.selectbox("Chart Period", ["1mo", "6mo", "1y", "5y", "max"], index=2)
    st.divider()
    st.subheader("Portfolio Watchlist")
    default_list = "F"
    input_tickers = st.text_area("Portfolio Tickers:", default_list)
    tickers_list = [t.strip().upper() for t in input_tickers.split(",") if t.strip()]

# 4. TABS
tab1, tab2, tab3, tab4 = st.tabs(["Overview", "Financials", "Analysis", "Portfolio Risk"])

# 5. EXECUTION
if ticker_symbol:
    # Get the "Tool" (The Ticker object itself isn't cached to avoid serialization errors)
    ticker_obj = yf.Ticker(ticker_symbol)
    info = get_yahoo_data(ticker_symbol)
    
    # Logic: Try Yahoo price first, then Alpha Vantage
    price = info.get('currentPrice') if info else None
    if price is None:
        price = get_backup_price(ticker_symbol)

    if price:
        # --- TAB 1: OVERVIEW ---
        with tab1:
            col1, col2 = st.columns([1, 2])
            with col1:
                st.header(info.get('longName', ticker_symbol) if info else ticker_symbol)
                st.metric("Current Price", f"${price:.2f}")
                if info:
                    st.write(f"**Sector:** {info.get('sector', 'N/A')}")
                    st.write(f"**Market Cap:** ${info.get('marketCap', 0):,}")
                else:
                    st.warning("Yahoo is throttled. Showing live price from Alpha Vantage.")
            with col2:
                # Historical Chart (Always try Yahoo first for charts)
                try:
                    hist = ticker_obj.history(period=period)
                    st.line_chart(hist['Close'])
                except:
                    st.error("Chart data currently unavailable.")

        # --- TAB 2: FINANCIALS ---
        with tab2:
            st.header("Financial Statements")
            # Commas formatting
            fmt = lambda x: "{:,.0f}".format(x) if isinstance(x, (int, float)) else x
            
               st.subheader("Income Statement")

try:
    # 1. Fetch the raw data
    income = ticker_obj.income_stmt
    
    # 2. Clean the column headers (removes the '00:00:00' timestamp)
    income.columns = [c.strftime('%Y-%m-%d') for c in income.columns]
    
    # 3. Use Pandas Styler to fix scientific notation and add commas
    # This turns 143000000000 into 143,000,000,000
    st.dataframe(income.style.format("{:,.0f}"), use_container_width=True)

except Exception as e:
    st.error("Financial data unavailable. Yahoo is likely throttled.")
              


                # 2. Apply professional formatting
                st.dataframe(income.style.format("{:,.0f}"), use_container_width=True)
                st.dataframe(ticker_obj.income_stmt.style.format(fmt), use_container_width=True)
                st.subheader("Cash Flow")
                st.dataframe(ticker_obj.cash_flow.style.format(fmt), use_container_width=True)
            except:
                    st.error("Financials currently unavailable.")

        # --- TAB 3: LYNCH ANALYSIS ---
        with tab3:
            st.subheader("Asset Categorization")
            if info:
                pe = info.get('forwardPE', 0)
                growth = info.get('earningsGrowth', 0)
                if 0 < pe < 15: st.success("Category: STALWART")
                elif growth and growth > 0.20: st.warning("Category: FAST GROWER")
                else: st.info("Category: MONITOR")
            else:
                st.write("Analysis unavailable during throttling.")

    else:
        st.error("Data connection failed. Check your API key in Secrets.")

# --- TAB 4: RISK ---
with tab4:
    if tickers_list:
        try:
            data = yf.download(tickers_list, period="1y")['Close']
            vol = data.pct_change().std() * np.sqrt(252) * 100
            st.bar_chart(vol)
        except:
            st.warning("Bulk data throttled.")
