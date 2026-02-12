import numpy as np


def support_resistance(df):
    supports = []
    resistances = []

    close = df["Close"].values

    for i in range(2, len(close) - 2):

        # Support
        if (
            close[i] < close[i - 1]
            and close[i] < close[i + 1]
            and close[i + 1] < close[i + 2]
            and close[i - 1] < close[i - 2]
        ):
            supports.append(float(close[i]))

        # Resistance
        if (
            close[i] > close[i - 1]
            and close[i] > close[i + 1]
            and close[i + 1] > close[i + 2]
            and close[i - 1] > close[i - 2]
        ):
            resistances.append(float(close[i]))

    return supports, resistances
