import yfinance as yf

def get_data(symbol, interval, period):
    data = yf.download(symbol, interval=interval, period=period)
    return data.dropna()