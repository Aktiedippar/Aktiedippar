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

# Hämtar data
def get_data(ticker):
    df = yf.download(ticker, period='3mo', interval='1d', auto_adjust=False)
    if df.empty:
        return pd.DataFrame()
    df['RSI'] = compute_rsi(df['Close'])
    return df.dropna()

# Mappar företagsnamn till rätt ticker
stock_names = {
    "Saab": "SAAB-B.ST",
    "Evolution": "EVO.ST"
}

st.title("📉 Aktier som dippar – möjliga köplägen")

# Användaren väljer bolag
selected_name = st.selectbox("Välj ett bolag:", list(stock_names.keys()))
ticker = stock_names[selected_name]

# Hämta data
df = get_data(ticker)

# Om data finns, visa analys
if not df.empty:
    st.subheader(f"{selected_name} ({ticker})")
    st.write(f"💰 Senaste stängningspris: **{df['Close'].iloc[-1]:.2f} SEK**")
    st.write(f"📈 RSI: **{df['RSI'].iloc[-1]:.2f}**")
    st.line_chart(df['Close'])
    st.write("📋 Öppnings- och stängningspriser:")
    st.dataframe(df[['Open', 'Close']].sort_index(ascending=False).round(2))

# Om data saknas, visa felmeddelande
if df.empty:
    st.error(f"Ingen data hittades för {selected_name}.")