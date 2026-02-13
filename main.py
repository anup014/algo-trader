import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from indicators.indicators import add_indicators
from indicators.support_resistance import support_resistance
from data.fetch_data import fetch_stock_data

# 1. Page Setup
st.set_page_config(page_title="Algo Trader Dashboard", layout="wide")
st.title("💹 Reliance.NS Trading Algorithm")

# 2. Your Original Trading Logic
def generate_signal(price, support, resistance, rsi):
    # PURE RSI momentum system
    if rsi < 50:
        return "BUY 🟢"
    elif rsi > 55:
        return "SELL 🔴"
    else:
        return "HOLD ⚪"

# 3. Main Application Function
def run_algo():
    symbol = "RELIANCE.NS"

    # Status Message
    with st.spinner("Crunching numbers..."):
        # Fetching data using your existing modules
        df = fetch_stock_data(symbol, interval="5m", period="30d")
        df = df.squeeze()
        df = add_indicators(df)
        support, resistance = support_resistance(df)

    # Core Calculations
    latest_price = float(df['Close'].iloc[-1])
    rsi = float(df['RSI'].iloc[-1])
    
    # Finding nearest levels
    nearest_support = max([s for s in support if s < latest_price], default=None)
    nearest_resistance = min([r for r in resistance if r > latest_price], default=None)

    # 4. Web Display (The UI)
    st.divider()
    
    # Big Metric Boxes
    m1, m2, m3 = st.columns(3)
    m1.metric("Current Price", f"₹{latest_price:.2f}")
    m2.metric("RSI (14)", round(rsi, 2))
    
    # Running the signal logic
    signal = generate_signal(latest_price, nearest_support, nearest_resistance, rsi)
    
    # Decision Display
    st.subheader("🧠 TRADING DECISION")
    if "BUY" in signal:
        st.success(f"Final Signal: {signal}")
    elif "SELL" in signal:
        st.error(f"Final Signal: {signal}")
    else:
        st.info(f"Final Signal: {signal}")

    # Technical Details
    with st.expander("Show Technical Levels"):
        st.write(f"**Support:** {nearest_support}")
        st.write(f"**Resistance:** {nearest_resistance}")
        st.dataframe(df.tail(10))

# Standard Python Entry Point
if __name__ == "__main__":
    run_algo()
