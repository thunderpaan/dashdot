from ta.trend import EMAIndicator, MACD
from ta.volatility import BollingerBands

def apply_indicators(data):
    data['EMA10'] = EMAIndicator(data['Close'], 10).ema_indicator()
    data['EMA20'] = EMAIndicator(data['Close'], 20).ema_indicator()
    data['EMA50'] = EMAIndicator(data['Close'], 50).ema_indicator()
    data['EMA100'] = EMAIndicator(data['Close'], 100).ema_indicator()

    macd = MACD(data['Close'])
    data['MACD'] = macd.macd()
    data['MACD_signal'] = macd.macd_signal()

    bb = BollingerBands(data['Close'])
    data['bb_high'] = bb.bollinger_hband()
    data['bb_low'] = bb.bollinger_lband()

    return data