#app.py file
import streamlit as st
import yfinance as yf
import plotly.graph_objects as go

st.set_page_config(layout="wide")

st.title("Dashboard")

# Sidebar
stock = st.sidebar.text_input("Stock Symbol", "RELIANCE.NS")
interval = st.sidebar.selectbox("Interval", ["1m", "5m", "15m", "1h", "1d"])
period = st.sidebar.selectbox("Period", ["1d", "5d", "1mo", "3mo"])

# Fetch data
data = yf.download(stock, period=period, interval=interval)

if data.empty:
    st.error("No data found. Check symbol.")
else:
    # Candlestick chart
    fig = go.Figure()

    fig.add_trace(go.Candlestick(
        x=data.index,
        open=data['Open'],
        high=data['High'],
        low=data['Low'],
        close=data['Close'],
        name="Candles"
    ))

    # Moving Average
    data['MA20'] = data['Close'].rolling(20).mean()
    fig.add_trace(go.Scatter(
        x=data.index,
        y=data['MA20'],
        line=dict(width=1),
        name="MA20"
    ))

    fig.update_layout(
        title=f"{stock} Chart",
        xaxis_rangeslider_visible=False
    )

    st.plotly_chart(fig, use_container_width=True)