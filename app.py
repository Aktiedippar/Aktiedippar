import streamlit as st
import yfinance as yf
import pandas as pd

# Funktion för att räkna RSI
def compute_rsi(series, period=14):
    delta = series.diff()
    gain = delta.where(delta > 0, 0.0)
    loss = -delta.where(delta < 0, 0.0)
    avg_gain = gain.rolling(window=period).mean()
    avg_loss = loss.rolling(window=period).mean()
    rs = avg_gain / avg_loss
    rsi = 100 - (100 / (1 + rs))
    return rsi

# Hämtar data för ett bolag
def get_data(ticker):
    df = yf.download(ticker, period='3mo', auto_adjust=True)
    if df.empty or 'Close' not in df.columns:
        return pd.DataFrame()
    df['RSI'] = compute_rsi(df['Close'])
    return df

# Lista på aktier att analysera (lägg till fler om du vill)
stock_list = [
    'AAPL', 'MSFT', 'TSLA', 'AMZN', 'GOOGL',
    'SAAB-B.ST',      # SAAB B
    'EVO.ST'          # Evolution AB
]
st.title("📉 Aktier som dippar – möjliga köplägen")

# Analysera varje aktie
for stock in stock_list:
    df = get_data(stock)
    if df.empty:
        continue

    latest_rsi = df['RSI'].iloc[-1]
    latest_close = df['Close'].iloc[-1]

    # Visa bara om RSI är lågt
    if latest_rsi < 50:
        st.subheader(f"📊 {stock}")
        st.write(f"💰 Senaste pris: **{latest_close:.2f} USD**")
        st.write(f"📉 RSI: **{latest_rsi:.2f}** *(översåld)*")
        st.line_chart(df['Close'])