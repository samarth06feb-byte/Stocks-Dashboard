import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np

# 1. Page Config
st.set_page_config(layout="wide", page_title="Hermes & Jackson Terminal")
st.title("🏛️ Hermes & Jackson | Research Terminal")

# 2. CACHING STRATEGY
# Use cache_resource for the 'Ticker' object (it's a tool/resource)
@st.cache_resource(ttl=3600)
def get_ticker(symbol):
    return yf.Ticker(symbol)

# Use cache_data for the actual numbers (it's data)
@st.cache_data(ttl=3600)
def get_stock_stats(symbol):
    t = yf.Ticker(symbol)
    # We only return dictionaries/dataframes, NOT the 't' object itself
    # This prevents the UnserializableReturnValueError
    return t.info, t.fast_info

# 3. SIDEBAR
with st.sidebar:
    st.header("Terminal Settings")
    ticker_symbol = st.text_input("Enter Ticker", "F").upper()
    period = st.selectbox("Chart Period", ["1mo", "6mo", "1y", "5y", "max"], index=2)
    
    st.divider()
    st.subheader("Portfolio Monitoring")
    # Your core brands and watchlist
    default_tickers = "F, RACE, OSK, DOLE, CALM, AAPL, MSFT, GOOG, TSLA, NVDA"
    input_tickers = st.text_area("Portfolio Tickers:", default_tickers)
    tickers_list = [t.strip().upper() for t in input_tickers.split(",") if t.strip()]

# 4. DEFINE TABS EARLY (Prevents NameError)
tab1, tab2, tab3, tab4, tab5 = st.tabs(["Overview", "Financials", "News", "Analysis", "Volatility"])

# 5. DATA EXECUTION
if ticker_symbol:
    try:
        # Fetch data using our split-caching method
        ticker_obj = get_ticker(ticker_symbol)
        info, fast_info = get_stock_stats(ticker_symbol)
        
        # --- TAB 1: OVERVIEW ---
        with tab1:
            col1, col2 = st.columns([1, 2])
            with col1:
                st.header(info.get('longName', ticker_symbol))
                # Fallback logic for price data
                price = info.get('currentPrice') or fast_info.get('last_price', 'N/A')
                st.metric("Current Price", f"${price}")
                st.write(f"**Sector:** {info.get('sector', 'N/A')}")
                st.write(f"**Summary:** {info.get('longBusinessSummary', 'No summary available.')[:300]}...")
            with col2:
                history = ticker_obj.history(period=period)
                st.line_chart(history['Close'])

        # --- TAB 2: FINANCIALS ---
        with tab2:
            st.header("Financial Statements")
            def format_df(df):
                return df.style.format("{:,.0f}")
            
            if not ticker_obj.income_stmt.empty:
                st.subheader("Income Statement")
                st.dataframe(format_df(ticker_obj.income_stmt), use_container_width=True)
            
            if not ticker_obj.balance_sheet.empty:
                st.subheader("Balance Sheet")
                st.dataframe(format_df(ticker_obj.balance_sheet), use_container_width=True)

        # --- TAB 3: NEWS ---
        with tab3:
            st.subheader(f"Latest Intelligence: {ticker_symbol}")
            news_items = ticker_obj.news
            if news_items:
                for item in news_items[:5]:
                    st.write(f"**{item.get('title')}**")
                    st.caption(f"Source: {item.get('publisher')}")
                    st.write(f"[Read Article]({item.get('link')})")
                    st.divider()

        # --- TAB 4: ANALYSIS (Peter Lynch Style) ---
        with tab4:
            st.subheader("Asset Categorization")
            pe = info.get('forwardPE', 0)
            growth = info.get('earningsGrowth', 0)
            
            # Logic tailored to your investment goals
            if pe and 0 < pe < 15:
                st.success("Analysis: STALWART / VALUE")
                st.write("This asset shows a low P/E multiple relative to market averages.")
            elif growth and growth > 0.20:
                st.warning("Analysis: FAST GROWER")
                st.write("Earnings growth exceeds 20%. Typical of high-octane growth stocks.")
            elif info.get('debtToEquity', 100) > 200:
                st.error("Analysis: POTENTIAL TURNAROUND")
                st.write("High debt-to-equity ratio detected. Monitor solvency closely.")
            else:
                st.info("Analysis: CYCLICAL / SLOW GROWER")

    except Exception as e:
        st.error(f"Yahoo Data Unavailable: The server is currently being throttled.")
        st.info("This is common on shared hosting. Please wait 5-10 minutes.")

# --- TAB 5: VOLATILITY (PORTFOLIO) ---
with tab5:
    st.header("Portfolio Risk Profile")
    if tickers_list:
        try:
            # We download this separately so it doesn't block the main search
            port_data = yf.download(tickers_list, period="1y")['Close']
            port_returns = port_data.pct_change().dropna()
            vol = port_returns.std() * np.sqrt(252) * 100
            
            vol_df = pd.DataFrame(vol, columns=["Volatility (%)"]).sort_values(by="Volatility (%)", ascending=False)
            st.bar_chart(vol_df)
            st.write(f"**Average Portfolio Risk:** {vol.mean():.2f}% Volatility")
        except:
            st.warning("Could not load portfolio volatility. Try reducing the number of tickers.")
