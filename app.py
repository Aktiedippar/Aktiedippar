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

# Hämtar data från yfinance
def get_data(ticker):
    df = yf.download(ticker, period='3mo', interval='1d', auto_adjust=False)
    if df.empty or 'Close' not in df.columns:
        return pd.DataFrame()
    df['RSI'] = compute_rsi(df['Close'])
    return df.dropna()

# Tickers för Saab och Evolution
stock_names = {
    "Saab": "SAAB-B.ST",
    "Evolution": "EVO.ST"
}

# Rubrik
st.title("📉 Aktier som dippar – möjliga köplägen")

# Användaren väljer företag
selected_name = st.selectbox("Välj ett bolag:", list(stock_names.keys()))
ticker = stock_names[selected_name]

# Hämta data
df = get_data(ticker)

# Visa data om den finns
if df.empty:
    st.error(f"Ingen data hittades för {selected_name}.")
else:
    st.subheader(f"{selected_name} ({ticker})")

    # Hämta senaste värden säkert
    latest_close = df['Close'].iloc[-1] if 'Close' in df.columns else None
    latest_rsi = df['RSI'].iloc[-1] if 'RSI' in df.columns else None

    if pd.notna(latest_close):
        st.write(f"💰 Senaste stängningspris: **{latest_close:.2f} SEK**")
    else:
        st.write("❌ Kunde inte visa senaste stängningspris.")

    if pd.notna(latest_rsi):
        st.write(f"📈 RSI: **{latest_rsi:.2f}**")
    else:
        st.write("❌ Kunde inte visa RSI.")

    # Linjediagram
    st.line_chart(df['Close'])

    # Tabell med öppnings- och stängningspriser
    st.write("📋 Öppnings- och stängningspriser:")
    st.dataframe(df[['Open', 'Close']].sort_index(ascending=False).round(2))