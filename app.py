import yfinance as yf
import streamlit as st
import pandas as pd

st.title("📉 Aktier som dippar – Köpläge?")

stocks = ['EVO.ST', 'VOLV-B.ST', 'ERIC-B.ST', 'INVE-B.ST']
rsi_threshold = 30

def get_data(ticker):
    df = yf.download(ticker, period='3mo')
    df['RSI'] = compute_rsi(df['Adj Close'])
    return df

def compute_rsi(series, period=14):
    delta = series.diff()
    gain = delta.clip(lower=0)
    loss = -delta.clip(upper=0)
    avg_gain = gain.rolling(window=period).mean()
    avg_loss = loss.rolling(window=period).mean()
    rs = avg_gain / avg_loss
    return 100 - (100 / (1 + rs))

for stock in stocks:
    df = get_data(stock)
    if len(df) == 0:
        continue
    latest_rsi = df['RSI'].iloc[-1]
    latest_close = df['Adj Close'].iloc[-1]
    if latest_rsi < rsi_threshold:
        st.write(f"📉 {stock} – RSI: {latest_rsi:.2f} – Pris: {latest_close:.2f} kr")
        