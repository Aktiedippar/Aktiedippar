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

# Hämtar data för en aktie
def get_data(ticker):
    df = yf.download(ticker, period='3mo', interval='1d', auto_adjust=False)
    if df.empty:
        return pd.DataFrame()
    df['RSI'] = compute_rsi(df['Close'])
    return df.dropna()

# Lista på tickers
stock_list = ["SAAB-B.ST", "EVO.ST"]

st.title("📉 Aktier som dippar – möjliga köplägen")

# Analysera varje aktie
for stock in stock_list:
    df = get_data(stock)
    if df.empty:
        continue

    latest_close = df['Close'].iloc[-1]
    latest_rsi = df['RSI'].iloc[-1]

    st.subheader(f"{stock}")
    st.write(f"💰 Senaste stängningspris: **{latest_close:.2f} SEK**")
    st.write(f"📈 RSI: **{latest_rsi:.2f}**")
    st.line_chart(df['Close'])

    st.write("📋 Öppnings- och stängningspriser:")
    st.dataframe(df[['Open', 'Close']].sort_index(ascending=False).round(2))