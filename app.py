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
    return df.dropna(subset=['Close', 'Open', 'RSI'])

# Mappar företagsnamn till rätt ticker
stock_names = {
    "Saab": "SAAB-B.ST",
    "Evolution": "EVO.ST"
}

st.title("📉 Aktier som dippar – möjliga köplägen")

# Användaren väljer bolag
selected_name = st.selectbox("Välj ett bolag:", list(stock_names.keys()))
ticker = stock_names[selected_name]

# Hämta och visa data
df = get_data(ticker)

if df.empty:
    st.error(f"Ingen data hittades för {selected_name}.")
else:
    st.subheader(f"{selected_name} ({ticker})")
    st.write(f"💰 Senaste stängningspris: **{df['Close'].iloc[-1]:.2f} SEK**")
    st.write(f"📈 RSI: **{df['RSI'].iloc[-1]:.2f}**")
    
    st.line_chart(df['Close'])

    st.write("📋 Öppnings- och stängningspriser senaste 3 månaderna:")
    st.dataframe(df[['Open', 'Close']].round(2).sort_index(ascending=False))