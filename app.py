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
    df = yf.download(ticker, period='6mo', auto_adjust=True)
    if df.empty or 'Close' not in df.columns:
        return pd.DataFrame()
    df['RSI'] = compute_rsi(df['Close'])
    return df

# Namn till ticker-mappning
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
st.title("📉 Aktier som dippar – möjliga köplägen")

# Användarinmatning
input_names = st.text_input("Ange bolag (t.ex. saab, evolution, tesla):", "saab, evolution")

# Konvertera till tickerlista
input_list = [name.strip().lower() for name in input_names.split(',')]
stock_list = [name_to_ticker[name] for name in input_list if name in name_to_ticker]

if not stock_list:
    st.warning("Inga giltiga bolagsnamn hittades. Kontrollera stavning.")
else:
    for stock in stock_list:
        df = get_data(stock)
        if df.empty:
            st.write(f"⚠️ Ingen data för {stock}.")
            continue

        latest_rsi = df['RSI'].iloc[-1]
        latest_close = df['Close'].iloc[-1]

        st.subheader(f"📊 {stock}")
        st.write(f"💰 Senaste pris: **{latest_close:.2f} USD**")
        if latest_rsi < 50:
            st.write(f"📉 RSI: **{latest_rsi:.2f}** 🟠 *(Lågt RSI)*")
        else:
            st.write(f"📈 RSI: **{latest_rsi:.2f}**")
        st.line_chart(df['Close'])