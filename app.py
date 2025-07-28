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
    if df.empty or 'Close' not in df.columns:
        return pd.DataFrame()
    df['RSI'] = compute_rsi(df['Close'])
    df = df[['Open', 'Close', 'RSI']]
    return df

# Namn → Ticker
name_to_ticker = {
    'apple': 'AAPL',
    'microsoft': 'MSFT',
    'tesla': 'TSLA',
    'amazon': 'AMZN',
    'google': 'GOOGL',
    'saab': 'SAAB-B.ST',
    'evolution': 'EVO.ST'
}

# Titel
st.title("📉 Aktier – Daglig prisdata och RSI")

# Inmatning
input_names = st.text_input("Ange bolag (t.ex. saab, evolution, tesla):", "saab, evolution")
input_list = [name.strip().lower() for name in input_names.split(',')]
stock_list = [name_to_ticker[name] for name in input_list if name in name_to_ticker]

if not stock_list:
    st.warning("⚠️ Inga giltiga bolagsnamn hittades.")
else:
    for name in input_list:
        if name not in name_to_ticker:
            st.write(f"⚠️ Okänt bolagsnamn: {name}")
            continue

        ticker = name_to_ticker[name]
        df = get_data(ticker)

        if df.empty:
            st.write(f"⚠️ Ingen data tillgänglig för {ticker}.")
            continue

        df = df.dropna()
        if df.empty:
            st.write(f"⚠️ För lite data för {ticker}.")
            continue

        # Visa analys
        st.subheader(f"📊 {name.title()} ({ticker})")

        # Senaste värden
        latest_rsi = df['RSI'].iloc[-1]
        latest_close = df['Close'].iloc[-1]
        st.write(f"💰 Senaste stängningspris: **{latest_close:.2f} USD**")
        st.write(f"📈 RSI: **{latest_rsi:.2f}**")

        # Diagram
        st.line_chart(df[['Close']])

        # Tabell med öppning/stängning
        st.write("📅 Öppning & Stängning – senaste 3 månaderna:")
        st.dataframe(df[['Open', 'Close']].sort_index(ascending=False).round(2))