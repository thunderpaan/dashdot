import requests

def get_ai_signal(data, symbol):
    latest = data.iloc[-1]

    prompt = f"""
    Analyze stock {symbol}

    Price: {latest['Close']}
    EMA20: {latest['EMA20']}
    MACD: {latest['MACD']}
    MACD Signal: {latest['MACD_signal']}

    Give:
    Signal: BUY/SELL/HOLD
    Confidence: %
    """

    try:
        res = requests.post(
            "http://localhost:11434/api/generate",
            json={"model": "gemma", "prompt": prompt, "stream": False},
            timeout=10
        )
        return res.json()['response']
    except:
        return "AI unavailable"