def generate_signal(price, support, resistance, rsi):

    if support is None or resistance is None:
        return "NO TRADE"

    if rsi < 30 and price <= support:
        return "BUY"

    elif rsi > 70 and price >= resistance:
        return "SELL"

    else:
        return "HOLD"
