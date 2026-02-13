import streamlit as st
import pandas as pd
import numpy as np
import yfinance as yf
import plotly.graph_objects as go
from datetime import datetime

# ==========================================================
# 1. CORE DATA ENGINE (SMART SEARCH & QUANT LOGIC)
# ==========================================================
class QuantEnginePro:
    """Handles high-fidelity data extraction and institutional auditing."""
    
    @staticmethod
    @st.cache_data(ttl=60)
    def fetch_market_data(user_input, interval):
        """Auto-corrects beginner searches and repairs 2026 data headers."""
        try:
            query = user_input.strip().upper()
            
            # Logic: If user types 'RELIANCE', we try 'RELIANCE.NS' automatically
            search_list = [query]
            if "." not in query:
                search_list.insert(0, f"{query}.NS")
            
            df = pd.DataFrame()
            final_symbol = query
            
            for ticker in search_list:
                # Optimized period fetching based on interval choice
                lookback = "60d" if interval in ["15m", "1h"] else "max"
                df = yf.download(ticker, interval=interval, period=lookback, progress=False, auto_adjust=True)
                if not df.empty:
                    final_symbol = ticker
                    break
            
            if df.empty: return None, query

            # 2026 DATA FIX: Flatten Multi-Index columns to prevent blank charts
            if isinstance(df.columns, pd.MultiIndex):
                df.columns = df.columns.get_level_values(0)
            
            df.index = pd.to_datetime(df.index)
            return df, final_symbol
        except:
            return None, user_input

    @staticmethod
    def apply_technicals(df):
        """Calculates RSI, VWAP, EMA, and Yearly Benchmarks."""
        # RSI 14 Logic
        delta = df['Close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
        df['RSI'] = 100 - (100 / (1 + (gain / loss)))

        # Institutional VWAP
        typical_p = (df['High'] + df['Low'] + df['Close']) / 3
        df['VWAP'] = (typical_p * df['Volume']).cumsum() / df['Volume'].cumsum()

        # Moving Averages
        df['EMA_20'] = df['Close'].ewm(span=20, adjust=False).mean()
        df['SMA_50'] = df['Close'].rolling(window=50).mean()
        
        # Performance Benchmarks
        df['52W_H'] = df['High'].rolling(window=252, min_periods=1).max()
        df['52W_L'] = df['Low'].rolling(window=252, min_periods=1).min()
        
        return df

# ==========================================================
# 2. UI CONFIGURATION & STYLING
# ==========================================================
st.set_page_config(page_title="QuantPro Terminal", layout="wide", page_icon="💎")

# Initialize App Memory
if 'app_state' not in st.session_state:
    st.session_state.app_state = "welcome"
if 'watchlist' not in st.session_state:
    st.session_state.watchlist = ["RELIANCE", "TCS", "ZOMATO", "IRFC"]
if 'active_ticker' not in st.session_state:
    st.session_state.active_ticker = "RELIANCE"

# CSS for Deep Dark Theme & Custom Metric Styling
st.markdown("""
    <style>
    .stApp { background-color: #0d1117; color: #c9d1d9; }
    [data-testid="stMetric"] { background-color: #161b22; border: 1px solid #30363d; border-radius: 12px; padding: 15px; }
    [data-testid="stMetricValue"] { color: #58a6ff !important; font-weight: 700; }
    .stSidebar { background-color: #0d1117 !important; border-right: 1px solid #30363d; }
    .stTabs [data-baseweb="tab-list"] { gap: 24px; border-bottom: 1px solid #30363d; }
    .stTabs [data-baseweb="tab"] { color: #8b949e; font-size: 1.1rem; }
    .stTabs [aria-selected="true"] { color: #58a6ff !important; border-bottom-color: #58a6ff !important; }
    </style>
    """, unsafe_allow_html=True)

# ==========================================================
# 3. PAGE ROUTING LOGIC
# ==========================================================

# --- PAGE A: THE FULL-SCREEN LANDING PAGE ---
# --- PAGE A: THE FULL-SCREEN LANDING PAGE ---
# --- PAGE A: THE FULL-SCREEN LANDING PAGE ---
if st.session_state.app_state == "welcome":
    # 1. Advanced CSS for High-End Typography and Button Styling
    st.markdown("""
        <style>
            @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;700;900&display=swap');
            
            [data-testid="stSidebar"] { display: none; }
            
            div.stButton > button:first-child {
                height: 4.8em !important;
                font-family: 'Inter', -apple-system, sans-serif !important;
                font-size: 20px !important;
                font-weight: 700 !important;
                letter-spacing: 3px !important; /* Professional Tracking */
                text-transform: uppercase !important;
                border-radius: 12px !important;
                background: rgba(88, 166, 255, 0.1) !important;
                color: #58a6ff !important;
                border: 2px solid #58a6ff !important;
                backdrop-filter: blur(10px) !important; /* Glass effect */
                margin-top: -180px; 
                position: relative;
                z-index: 9999;
                transition: all 0.4s cubic-bezier(0.165, 0.84, 0.44, 1);
            }
            
            div.stButton > button:first-child:hover {
                background: #58a6ff !important;
                color: #0d1117 !important;
                transform: translateY(-8px);
                box-shadow: 0 20px 40px rgba(88, 166, 255, 0.3) !important;
            }
        </style>
    """, unsafe_allow_html=True)

    # 2. Hero Image with Modern Typography Overlay
    st.markdown(f"""
        <div style="
            height: 85vh; 
            width: 100%; 
            background-image: linear-gradient(rgba(13, 17, 23, 0.2), rgba(13, 17, 23, 0.9)), 
            url('https://images.pexels.com/photos/6770610/pexels-photo-6770610.jpeg?auto=compress&cs=tinysrgb&w=1260'); 
            background-size: cover; 
            background-position: center; 
            display: flex; 
            flex-direction: column; 
            justify-content: center; 
            align-items: center; 
            border-radius: 40px;
            color: white;
            text-align: center;
            font-family: 'Inter', sans-serif;
            border: 1px solid #30363d;
        ">
            <h1 style="font-size: clamp(3.5rem, 12vw, 7.5rem); margin-bottom: 0px; font-weight: 900; letter-spacing: -6px; line-height: 0.9;">QUANTPRO</h1>
            <p style="font-size: clamp(1rem, 3vw, 1.5rem); max-width: 750px; margin-top: 20px; margin-bottom: 80px; opacity: 0.8; font-weight: 400; letter-spacing: 1px; color: #8b949e;">
                INSTITUTIONAL INTELLIGENCE • REAL-TIME MOMENTUM
            </p>
        </div>
    """, unsafe_allow_html=True)

    # 3. The Button Placement
    _, btn_col, _ = st.columns([1, 2, 1]) 
    with btn_col:
        if st.button("Launch Terminal", use_container_width=True):
            st.session_state.app_state = "terminal"
            st.rerun()

# --- PAGE B: THE TRADING TERMINAL ---
elif st.session_state.app_state == "terminal":
    # --- SIDEBAR ARCHITECTURE ---
    st.sidebar.title("💎 QuantPro Terminal")
    if st.sidebar.button("🏠 Exit to Home Screen", use_container_width=True):
        st.session_state.app_state = "welcome"
        st.rerun()

    st.sidebar.markdown("---")
    st.sidebar.subheader("📌 Your Watchlist")
    for item in st.session_state.watchlist:
        cols = st.sidebar.columns([4, 1])
        if cols[0].button(f"📊 {item}", key=f"nav_{item}", use_container_width=True):
            st.session_state.active_ticker = item
            st.rerun()
        if cols[1].button("✖", key=f"del_{item}"):
            st.session_state.watchlist.remove(item)
            st.rerun()

    st.sidebar.markdown("---")
    new_stock = st.sidebar.text_input("🔍 Search Stock", placeholder="e.g. HDFC").upper()
    if st.sidebar.button("Add & Analyze", use_container_width=True):
        if new_stock:
            if new_stock not in st.session_state.watchlist:
                st.session_state.watchlist.append(new_stock)
            st.session_state.active_ticker = new_stock
            st.rerun()

    # --- MAIN TERMINAL VIEW ---
    engine = QuantEnginePro()
    interval = st.sidebar.selectbox("⏱️ Timeframe", ["15m", "1h", "1d"], index=0)
    
    data, ticker_id = engine.fetch_market_data(st.session_state.active_ticker, interval)

    if data is not None:
        df = engine.apply_technicals(data)
        last, prev = df.iloc[-1], df.iloc[-2]
        
        # Header & LTP Metric
        h1, h2 = st.columns([3, 1])
        with h1:
            st.title(f"{ticker_id}")
            st.caption(f"2026 Market Feed | Precision Analysis | Interval: {interval}")
        with h2:
            st.write("")
            change_pct = ((last['Close'] - prev['Close']) / prev['Close']) * 100
            st.metric("LTP", f"₹{last['Close']:,.2f}", f"{change_pct:.2f}%")

        # --------------------------------------------------
        # THE RESTORED TECHNICAL AUDIT GRID (4-COLUMN)
        # --------------------------------------------------
        st.subheader("📋 Institutional Technical Audit")
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.markdown("**Price Action**")
            st.metric("Open", f"₹{last['Open']:,.2f}")
            st.metric("Day High", f"₹{last['High']:,.2f}")
            st.metric("Day Low", f"₹{last['Low']:,.2f}")

        with col2:
            st.markdown("**Institutional Levels**")
            st.metric("VWAP", f"₹{last['VWAP']:,.2f}")
            st.metric("EMA (20)", f"₹{last['EMA_20']:,.2f}")
            st.metric("SMA (50)", f"₹{last['SMA_50']:,.2f}")

        with col3:
            st.markdown("**Momentum**")
            st.metric("RSI (14)", f"{last['RSI']:.2f}")
            rsi_val = last['RSI']
            rsi_zone = "Oversold" if rsi_val < 30 else "Overbought" if rsi_val > 70 else "Neutral"
            st.metric("RSI Zone", rsi_zone)
            st.metric("Volume", f"{int(last['Volume']):,}")

        with col4:
            st.markdown("**Yearly Benchmarks**")
            st.metric("52W High", f"₹{last['52W_H']:,.2f}")
            st.metric("52W Low", f"₹{last['52W_L']:,.2f}")
            dist_high = ((last['52W_H'] - last['Close']) / last['52W_H']) * 100
            st.metric("Off 52W High", f"{dist_high:.2f}%")
        
        st.markdown("---")

        # --- ANALYSIS TABS ---
        tab_chart, tab_data = st.tabs(["📉 Momentum Visualizer", "📝 Full Audit Logs"])
        
        with tab_chart:
            st.subheader("Relative Strength Index (RSI)")
            
            
            fig = go.Figure()
            fig.add_trace(go.Scatter(
                x=df.index, y=df['RSI'],
                line=dict(color='#58a6ff', width=2),
                fill='toself', fillcolor='rgba(88, 166, 255, 0.05)',
                name="RSI 14"
            ))
            
            # Threshold Markers
            fig.add_hline(y=70, line_dash="dash", line_color="#f85149", annotation_text="Overbought")
            fig.add_hline(y=30, line_dash="dash", line_color="#3fb950", annotation_text="Oversold")
            
            fig.update_layout(
                height=550, template="plotly_dark",
                plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)',
                xaxis=dict(gridcolor='#30363d', rangeslider_visible=True, showgrid=True), 
                yaxis=dict(gridcolor='#30363d', side="right", range=[0, 100]),
                margin=dict(l=0, r=50, t=10, b=10)
            )
            st.plotly_chart(fig, use_container_width=True)

        with tab_data:
            st.subheader("Historical Quantitative Audit")
            st.dataframe(df.sort_index(ascending=False).head(200), use_container_width=True)
            
    else:
        st.error(f"Failed to fetch data for '{st.session_state.active_ticker}'.")
        st.info("Searching common names (e.g., RELIANCE, TCS) usually works best.")

st.sidebar.markdown("---")
st.sidebar.caption("QuantPro Terminal v3.0 | Secure Build 2026")
