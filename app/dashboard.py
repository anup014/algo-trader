# ==========================================
# IMPORTS
# ==========================================
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import sys
import os
import yfinance as yf

# ==========================================
# FIX PROJECT PATH
# ==========================================
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from data.fetch_data import fetch_stock_data
from indicators.indicators import add_indicators
from indicators.support_resistance import support_resistance
from strategy.signal import generate_signal


# ==========================================
# PAGE CONFIG
# ==========================================
st.set_page_config(page_title="AI Stock Dashboard", layout="wide")
st.title("📊 AI Powered Trading Dashboard")


# ==========================================
# SIDEBAR
# ==========================================
st.sidebar.header("Stock Settings")

@st.cache_data
def load_indian_stocks():
    major_stocks = [
        "RELIANCE", "TCS", "INFY", "HDFCBANK",
        "ICICIBANK", "SBIN", "LT", "ITC",
        "HINDUNILVR", "AXISBANK", "KOTAKBANK",
        "BHARTIARTL", "MARUTI", "BAJFINANCE",
        "TITAN", "ADANIENT", "WIPRO"
    ]
    return sorted(major_stocks)

stock_list = load_indian_stocks()

selected_stock = st.sidebar.selectbox(
    "Select Indian Stock",
    stock_list
)

symbol = selected_stock + ".NS"

timeframe = st.sidebar.selectbox(
    "Select Timeframe",
    ["5m", "15m", "1h", "1d"]
)

period_map = {
    "5m": "7d",
    "15m": "1mo",
    "1h": "3mo",
    "1d": "6mo"
}

period = period_map[timeframe]


# ==========================================
# ANALYZE BUTTON
# ==========================================
if st.sidebar.button("🔍 Analyze Stock"):

    try:
        # Fetch Data
        df = fetch_stock_data(symbol, interval=timeframe, period=period)

        if df is None or df.empty:
            st.error("No data found for this symbol.")
            st.stop()

        df.index = pd.to_datetime(df.index)

        # Add Indicators
        df = add_indicators(df)

        # Latest values safely
        price = float(df["Close"].iloc[-1])
        rsi = float(df["RSI"].iloc[-1])

        # Support & Resistance
        support, resistance = support_resistance(df)

        # Clean values properly
        clean_support = []
        for s in support:
            try:
                clean_support.append(float(s))
            except:
                pass

        clean_resistance = []
        for r in resistance:
            try:
                clean_resistance.append(float(r))
            except:
                pass

        nearest_support = max(
            [s for s in clean_support if s < price],
            default=None
        )

        nearest_resistance = min(
            [r for r in clean_resistance if r > price],
            default=None
        )

        # Generate Signal
        signal = generate_signal(price, nearest_support, nearest_resistance, rsi)

        # Risk Management
        stop_loss = price * 0.995
        risk_per_share = price - stop_loss
        target = price + 2 * risk_per_share

        # ==========================================
        # OUTPUT SECTION
        # ==========================================
        st.subheader("📈 Live Trade Suggestion")

        col1, col2, col3 = st.columns(3)
        col1.metric("Current Price", f"₹{round(price,2)}")
        col2.metric("RSI", round(rsi,2))
        col3.metric("Signal", signal)

        st.write("### 🎯 Trade Levels")
        st.write(f"Stop Loss: ₹{round(stop_loss,2)}")
        st.write(f"Target: ₹{round(target,2)}")

        st.write("### 📐 Market Structure")
        st.write(f"Nearest Support: {nearest_support}")
        st.write(f"Nearest Resistance: {nearest_resistance}")

        # ==========================================
        # CHART
        # ==========================================
        st.write("### 📊 Price Chart")

        fig = make_subplots(
            rows=2,
            cols=1,
            shared_xaxes=True,
            vertical_spacing=0.05,
            row_heights=[0.7, 0.3]
        )

        # Price
        fig.add_trace(
            go.Scatter(
                x=df.index,
                y=df["Close"],
                mode="lines",
                name="Close Price"
            ),
            row=1,
            col=1
        )

        # Support Line
        if nearest_support is not None:
            fig.add_hline(
                y=nearest_support,
                line_dash="dash",
                row=1,
                col=1
            )

        # Resistance Line
        if nearest_resistance is not None:
            fig.add_hline(
                y=nearest_resistance,
                line_dash="dash",
                row=1,
                col=1
            )

        # RSI
        fig.add_trace(
            go.Scatter(
                x=df.index,
                y=df["RSI"],
                mode="lines",
                name="RSI"
            ),
            row=2,
            col=1
        )

        fig.add_hline(y=70, line_dash="dash", row=2, col=1)
        fig.add_hline(y=30, line_dash="dash", row=2, col=1)

        fig.update_layout(
            height=700,
            template="plotly_dark",
            xaxis_rangeslider_visible=False
        )

        st.plotly_chart(fig, use_container_width=True)

    except Exception as e:
        st.error(f"Error analyzing stock: {e}")
