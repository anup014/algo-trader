import yfinance as yf
import pandas as pd


def fetch_stock_data(symbol, interval="5m", period="7d"):
    try:
        df = yf.download(
            symbol,
            interval=interval,
            period=period,
            progress=False,
            auto_adjust=True,
            group_by="column"
        )

        if df is None or df.empty:
            return pd.DataFrame()

        # 🔥 FIX MULTI-INDEX COLUMN ISSUE
        if isinstance(df.columns, pd.MultiIndex):
            df.columns = df.columns.get_level_values(0)

        # 🔥 ENSURE 1D COLUMNS
        for col in df.columns:
            if isinstance(df[col], pd.DataFrame):
                df[col] = df[col].iloc[:, 0]

        df = df[["Open", "High", "Low", "Close", "Volume"]]

        df.dropna(inplace=True)

        return df

    except Exception as e:
        print("Fetch error:", e)
        return pd.DataFrame()
