def generate_signal(data):
    latest = data.iloc[-1]

    if (
        latest['Close'] > latest['EMA20'] and
        latest['MACD'] > latest['MACD_signal']
    ):
        return "BUY"

    elif (
        latest['Close'] < latest['EMA20'] and
        latest['MACD'] < latest['MACD_signal']
    ):
        return "SELL"

    return "HOLD"