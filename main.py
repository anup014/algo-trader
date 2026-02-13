
from indicators.indicators import add_indicators
from indicators.support_resistance import support_resistance
from data.fetch_data import fetch_stock_data
from strategy.signal import generate_signal



def generate_signal(price, support, resistance, rsi):

    # PURE RSI momentum system
    if rsi < 50:
        return "BUY 🟢"

    elif rsi > 55:
        return "SELL 🔴"

    else:
        return "HOLD ⚪"





def run_algo():
    symbol = "RELIANCE.NS"

    print("\n📊 Fetching data...")
    df = fetch_stock_data(symbol, interval="5m", period="30d")
    df = df.squeeze()

    print("📈 Adding indicators...")
    df = add_indicators(df)

    print("📐 Calculating support & resistance...")
    support, resistance = support_resistance(df)

    latest_price = float(df['Close'].iloc[-1])


    nearest_support = max([s for s in support if s < latest_price], default=None)
    nearest_resistance = min([r for r in resistance if r > latest_price], default=None)

    if nearest_support is not None:
      nearest_support = float(nearest_support[0])

    if nearest_resistance is not None:
      nearest_resistance = float(nearest_resistance[0])

    rsi = float(df['RSI'].iloc[-1])




    signal = generate_signal(
        latest_price,
        nearest_support,
        nearest_resistance,
        rsi
    )
    print ("Signal:", signal)

    print("\n============ RESULT ============")
    print(f"Last Price         : {latest_price:.2f}")
    print(f"Nearest Support    : {nearest_support}")
    print(f"Nearest Resistance : {nearest_resistance}")

    print("\n🧠 TRADING DECISION")
    print(f"RSI               : {round(rsi, 2)}")
    print(f"Signal            : {signal}")


# 🔥 THIS MUST BE AT THE VERY BOTTOM
if __name__ == "__main__":
    run_algo()
