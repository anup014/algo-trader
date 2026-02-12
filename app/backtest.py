from data.fetch_data import fetch_stock_data
from indicators.indicators import add_indicators
from indicators.support_resistance import support_resistance
from app.main import generate_signal




def backtest_strategy(symbol):
    print(f"\n📊 Backtesting for {symbol}...")

    df = fetch_stock_data(symbol, interval="5m", period="30d")
    df = add_indicators(df)

    capital = 100000
    position = None
    entry_price = 0
    trades = []
    equity_curve = []

    stop_loss = None
    target = None
    quantity = 0

    risk_percent = 0.02
    reward_ratio = 2

    for i in range(50, len(df)):

        temp_df = df.iloc[:i]

        support, resistance = support_resistance(temp_df)

        price = float(temp_df['Close'].iloc[-1].values[0])
        rsi = float(temp_df['RSI'].iloc[-1])

        nearest_support = max([s for s in support if s < price], default=None)
        nearest_resistance = min([r for r in resistance if r > price], default=None)

        if nearest_support is not None:
            nearest_support = float(nearest_support[0])

        if nearest_resistance is not None:
            nearest_resistance = float(nearest_resistance[0])

        signal = generate_signal(price, nearest_support, nearest_resistance, rsi)

        print("Price:", price, "RSI:", rsi, "Signal:", signal)

        # ======================
        # ENTRY LOGIC
        # ======================
        if "BUY" in signal and position is None:

            risk_amount = capital * risk_percent
            stop_loss = price * 0.995
            risk_per_share = price - stop_loss

            if risk_per_share == 0:
                continue

            quantity = risk_amount / risk_per_share
            target = price + reward_ratio * risk_per_share

            position = "LONG"
            entry_price = price

            trades.append({
                "type": "BUY",
                "entry": price
            })

        # ======================
        # EXIT LOGIC
        # ======================
        elif position == "LONG":

            # Exit on SELL signal
            if "SELL" in signal:

                profit = (price - entry_price) * quantity
                capital += profit

                trades.append({
                    "type": "SELL",
                    "exit": price,
                    "profit": profit
                })

                position = None
                stop_loss = None
                target = None
                quantity = 0

            # Stop Loss Hit
            elif price <= stop_loss:

                loss = (price - entry_price) * quantity
                capital += loss

                trades.append({
                    "type": "SELL",
                    "exit": price,
                    "profit": loss
                })

                position = None
                stop_loss = None
                target = None
                quantity = 0

            # Target Hit
            elif price >= target:

                profit = (price - entry_price) * quantity
                capital += profit

                trades.append({
                    "type": "SELL",
                    "exit": price,
                    "profit": profit
                })

                position = None
                stop_loss = None
                target = None
                quantity = 0

        equity_curve.append(capital)

    return capital, trades, equity_curve


def calculate_drawdown(equity_curve):
    peak = equity_curve[0]
    max_dd = 0

    for value in equity_curve:
        if value > peak:
            peak = value

        dd = peak - value

        if dd > max_dd:
            max_dd = dd

    return max_dd


# ===============================
# STEP 5: PERFORMANCE ANALYSIS
# ===============================
import numpy as np

def analyze_performance(trades, initial_capital, final_capital, equity_curve):
    
    sell_trades = [t for t in trades if t["type"] == "SELL"]
    profits = [t["profit"] for t in sell_trades]

    total_trades = len(profits)
    wins = [p for p in profits if p > 0]
    losses = [p for p in profits if p <= 0]

    win_rate = (len(wins) / total_trades) * 100 if total_trades else 0

    total_profit = sum(wins) if wins else 0
    total_loss = abs(sum(losses)) if losses else 0

    profit_factor = total_profit / total_loss if total_loss != 0 else 0

    avg_win = np.mean(wins) if wins else 0
    avg_loss = np.mean(losses) if losses else 0
    risk_reward = abs(avg_win / avg_loss) if avg_loss != 0 else 0

    returns = np.diff(equity_curve)
    sharpe = (np.mean(returns) / np.std(returns)) * np.sqrt(252) if np.std(returns) != 0 else 0

    total_return_percent = ((final_capital - initial_capital) / initial_capital) * 100

    print("\n📊 PROFESSIONAL PERFORMANCE REPORT")
    print(f"Initial Capital      : ₹{initial_capital}")
    print(f"Final Capital        : ₹{round(final_capital,2)}")
    print(f"Total Return         : {round(total_return_percent,2)}%")
    print(f"Total Trades         : {total_trades}")
    print(f"Win Rate             : {round(win_rate,2)}%")
    print(f"Profit Factor        : {round(profit_factor,2)}")
    print(f"Risk-Reward Ratio    : {round(risk_reward,2)}")
    print(f"Sharpe Ratio         : {round(sharpe,2)}")



# ===============================
# MAIN EXECUTION
# ===============================
if __name__ == "__main__":
    initial_capital = 100000
    final_capital, trades, equity_curve = backtest_strategy("RELIANCE.NS")

    analyze_performance(trades, initial_capital, final_capital, equity_curve)

    max_drawdown = calculate_drawdown(equity_curve)
    print(f"Max Drawdown : ₹{round(max_drawdown, 2)}")

    