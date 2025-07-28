import streamlit as st
import yfinance as yf
import pandas as pd
import altair as alt

st.set_page_config(page_title="Aktier som dippar", layout="centered")

# --- RSI-BERÄKNING ---
def compute_rsi(series, period=14):
    delta = series.diff()
    gain = delta.where(delta > 0, 0.0)
    loss = -delta.where(delta < 0, 0.0)
    avg_gain = gain.rolling(window=period).mean()
    avg_loss = loss.rolling(window=period).mean()
    rs = avg_gain / avg_loss
    rsi = 100 - (100 / (1 + rs))
    return rsi

# --- DATAHÄMTNING ---
def get_data(ticker):
    df = yf.download(ticker, period='3mo', interval='1d', auto_adjust=False)
    if df.empty or 'Close' not in df.columns:
        return pd.DataFrame()
    df['RSI'] = compute_rsi(df['Close'])
    return df.dropna()

# --- NAMN -> TICKER-MAPPNING ---
stock_names = {
    "saab": "SAAB-B.ST",
    "evo": "EVO.ST",
    "evolution": "EVO.ST"
}

# --- TITEL ---
st.title("📉 Aktier som dippar – möjliga köplägen")

# --- INPUT ---
user_input = st.text_input("Skriv ett företagsnamn (t.ex. 'saab', 'evo')").lower().strip()

if user_input:
    ticker = stock_names.get(user_input)

    if not ticker:
        st.error("❌ Företaget kunde inte hittas. Prova t.ex. 'saab' eller 'evo'.")
    else:
        df = get_data(ticker)

        if df.empty:
            st.error(f"Ingen data hittades för {user_input.upper()} ({ticker}).")
        else:
            st.subheader(f"{user_input.capitalize()} ({ticker})")

            # Senaste värden
            latest_close = df['Close'].iloc[-1]
            latest_rsi = df['RSI'].iloc[-1]

            st.write(f"💰 Senaste stängningspris: **{latest_close:.2f} SEK**")

            # RSI-indikator med färg
            if latest_rsi < 30:
                st.success(f"📉 RSI: **{latest_rsi:.2f}** – Översåld (möjligt köpläge)")
            elif latest_rsi > 70:
                st.warning(f"📈 RSI: **{latest_rsi:.2f}** – Överköpt (var försiktig)")
            else:
                st.write(f"📈 RSI: **{latest_rsi:.2f}**")

            # Prisgraf
            st.write("📊 Prisgraf:")
            chart = alt.Chart(df.reset_index()).mark_line().encode(
                x='Date:T',
                y='Close:Q',
                tooltip=['Date:T', 'Close:Q', 'RSI:Q']
            ).properties(
                width=700,
                height=400
            ).interactive()
            st.altair_chart(chart)

            # Tabell
            st.write("📋 Öppnings- och stängningspriser:")
            st.dataframe(df[['Open', 'Close']].sort_index(ascending=False).round(2))
else:
    st.info("🔍 Ange ett företagsnamn för att se analysen.")