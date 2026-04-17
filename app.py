import streamlit as st
from data.data_fetcher import get_data
from indi.indicators import apply_indicators
from strat.strategy import generate_signal
from ai.ai_engine import get_ai_signal

st.title("Trading Dashboard")

symbol = st.text_input("Stock", "RELIANCE.NS")

interval = "15m"
period = "1mo"

data = get_data(symbol, interval, period)

data = apply_indicators(data)

signal = generate_signal(data)

st.write("Signal:", signal)

if st.button("Run AI"):
    st.write(get_ai_signal(data, symbol))