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

# Hämta data
def get_data(ticker):
    df = yf.download(ticker, period='3mo', interval='1d', auto_adjust=False)
    if df.empty or 'Close' not in df.columns or 'Open' not in df.columns:
        return pd.DataFrame()
    df['RSI'] = compute_rsi(df['Close'])
    return df[['Open', 'Close', 'RSI']].dropna()

# Aktielista
ticker_map = {
    "Saab": "SAAB-B.ST",
    "Evolution": "EVO.ST"
}

st.title("📉 Saab & Evolution – Aktiedata")

# Välj aktie
selected_stock = st.selectbox("Välj ett bolag:", list(ticker_map.keys()))
ticker = ticker_map[selected_stock]

# Hämta data
df = get_data(ticker)

if df.empty:
    st.error(f"Ingen data hittades för {selected_stock} ({ticker}).")
else:
    latest_close = df['Close'].iloc[-1]
    latest_rsi = df['RSI'].iloc[-1]

    st.subheader(f"{selected_stock} ({ticker})")
    st.write(f"💰 Senaste stängningspris: **{latest_close:.2f} SEK**")
    st.write(f"📈 RSI: 55**{latest_rsi:.2f}**")
    st.line_chart(df['Close'])

    st.write("📋 Öppning & Stängning – senaste 3 månaderna:")
    st.dataframe(df[['Open', 'Close']].sort_index(ascending=False).round(2))