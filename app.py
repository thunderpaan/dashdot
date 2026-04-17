import streamlit as st
import yfinance as yf
import plotly.graph_objects as go
import pandas as pd
import json
import os
import requests

from ta.trend import EMAIndicator, MACD
from ta.volatility import BollingerBands

# -----------------------
# CONFIG
# -----------------------
st.set_page_config(layout="wide")
WATCHLIST_FILE = "watchlist.json"

# Enable AI only if running locally
USE_AI = os.getenv("USE_AI", "false") == "true"

# -----------------------
# WATCHLIST FUNCTIONS
# -----------------------
def load_watchlist():
    if os.path.exists(WATCHLIST_FILE):
        with open(WATCHLIST_FILE, "r") as f:
            return json.load(f)
    return ["RELIANCE.NS"]

def save_watchlist(watchlist):
    with open(WATCHLIST_FILE, "w") as f:
        json.dump(watchlist, f)

watchlist = load_watchlist()

# -----------------------
# SIDEBAR
# -----------------------
st.sidebar.title("📊 Watchlist")

new_stock = st.sidebar.text_input("Add Stock (e.g. INFY.NS)")
if st.sidebar.button("Add Stock"):
    if new_stock and new_stock not in watchlist:
        watchlist.append(new_stock)
        save_watchlist(watchlist)

stock = st.sidebar.selectbox("Select Stock", watchlist)

interval = st.sidebar.selectbox("Interval", ["5m", "15m", "1h", "1d"])
period = st.sidebar.selectbox("Period", ["1d", "5d", "1mo", "3mo"])

# -----------------------
# FETCH DATA
# -----------------------
data = yf.download(stock, period=period, interval=interval)

if data.empty:
    st.error("No data found. Check stock symbol.")
    st.stop()

# -----------------------
# INDICATORS
# -----------------------
# Clean data first
data = data.dropna()

# Ensure enough data points
if len(data) < 100:
    st.warning("Not enough data for indicators")
else:
    # Convert to float (important)
    data['Close'] = pd.to_numeric(data['Close'], errors='coerce')

    # Drop NaN again after conversion
    data = data.dropna()

    # EMA
    data['EMA10'] = EMAIndicator(close=data['Close'], window=10).ema_indicator()
    data['EMA20'] = EMAIndicator(close=data['Close'], window=20).ema_indicator()
    data['EMA50'] = EMAIndicator(close=data['Close'], window=50).ema_indicator()
    data['EMA100'] = EMAIndicator(close=data['Close'], window=100).ema_indicator()

macd = MACD(data['Close'])
data['MACD'] = macd.macd()
data['MACD_signal'] = macd.macd_signal()

bb = BollingerBands(data['Close'])
data['bb_high'] = bb.bollinger_hband()
data['bb_low'] = bb.bollinger_lband()

# -----------------------
# FIBONACCI
# -----------------------
st.sidebar.subheader("Fibonacci Levels")
fib_high = st.sidebar.number_input("Swing High", value=float(data['High'].max()))
fib_low = st.sidebar.number_input("Swing Low", value=float(data['Low'].min()))

fib_levels = [
    fib_high - (fib_high - fib_low) * 0.236,
    fib_high - (fib_high - fib_low) * 0.382,
    fib_high - (fib_high - fib_low) * 0.5,
    fib_high - (fib_high - fib_low) * 0.618,
]

# -----------------------
# AI FUNCTION (OLLAMA)
# -----------------------
def get_ai_signal(data, stock):
    try:
        latest = data.iloc[-1]

        prompt = f"""
        You are a professional stock trader.

        Analyze the data:

        Stock: {stock}
        Price: {latest['Close']}
        EMA10: {latest['EMA10']}
        EMA20: {latest['EMA20']}
        EMA50: {latest['EMA50']}
        EMA100: {latest['EMA100']}
        MACD: {latest['MACD']}
        MACD Signal: {latest['MACD_signal']}
        Bollinger High: {latest['bb_high']}
        Bollinger Low: {latest['bb_low']}

        Output format:
        Signal: BUY/SELL/HOLD
        Confidence: %
        Reason: short explanation
        """

        response = requests.post(
            "http://localhost:11434/api/generate",
            json={
                "model": "gemma",
                "prompt": prompt,
                "stream": False
            },
            timeout=10
        )

        return response.json()['response']

    except Exception:
        return "AI unavailable (works only locally with Ollama running)"

# -----------------------
# SIGNAL LOGIC (BASE)
# -----------------------
signal = "HOLD"

if (
    data['Close'].iloc[-1] > data['EMA20'].iloc[-1]
    and data['MACD'].iloc[-1] > data['MACD_signal'].iloc[-1]
):
    signal = "BUY"

elif (
    data['Close'].iloc[-1] < data['EMA20'].iloc[-1]
    and data['MACD'].iloc[-1] < data['MACD_signal'].iloc[-1]
):
    signal = "SELL"

# -----------------------
# CHART
# -----------------------
fig = go.Figure()

fig.add_trace(go.Candlestick(
    x=data.index,
    open=data['Open'],
    high=data['High'],
    low=data['Low'],
    close=data['Close'],
    name="Candles"
))

# EMA
for ema in ['EMA10', 'EMA20', 'EMA50', 'EMA100']:
    fig.add_trace(go.Scatter(x=data.index, y=data[ema], name=ema))

# Bollinger
fig.add_trace(go.Scatter(x=data.index, y=data['bb_high'], name="BB High", line=dict(dash='dot')))
fig.add_trace(go.Scatter(x=data.index, y=data['bb_low'], name="BB Low", line=dict(dash='dot')))

# Fibonacci
for level in fib_levels:
    fig.add_hline(y=level, line_dash="dash")

fig.update_layout(
    template="plotly_dark",
    xaxis_rangeslider_visible=False,
    height=700
)

# -----------------------
# LAYOUT
# -----------------------
st.title(f"📈 {stock} Trading Dashboard")

col1, col2 = st.columns([3, 1])

with col1:
    st.plotly_chart(fig, use_container_width=True)

with col2:
    st.subheader("Market Info")
    st.metric("Price", round(data['Close'].iloc[-1], 2))
    st.metric("Signal", signal)

    # -----------------------
    # AI PANEL
    # -----------------------
    st.subheader("🤖 AI Analysis")

    if USE_AI:
        if st.button("Run AI Analysis"):
            with st.spinner("Analyzing..."):
                ai_output = get_ai_signal(data, stock)
                st.text(ai_output)
    else:
        st.info("AI disabled on cloud (enable locally using USE_AI=true)")

# -----------------------
# MACD CHART
# -----------------------
st.subheader("MACD")
st.line_chart(data[['MACD', 'MACD_signal']])