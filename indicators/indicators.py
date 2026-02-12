import pandas as pd


def calculate_rsi(series, period=14):
    delta = series.diff()

    gain = delta.clip(lower=0)
    loss = -delta.clip(upper=0)

    avg_gain = gain.rolling(window=period).mean()
    avg_loss = loss.rolling(window=period).mean()

    rs = avg_gain / avg_loss
    rsi = 100 - (100 / (1 + rs))

    return rsi


def add_indicators(df):
    df = df.copy()

    # 🔥 ENSURE CLOSE IS 1D
    df["Close"] = df["Close"].squeeze()

    df["RSI"] = calculate_rsi(df["Close"], 14)

    df.dropna(inplace=True)

    return df
