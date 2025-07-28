import streamlit as st
import yfinance as yf
import pandas as pd
import altair as alt

st.set_page_config(page_title="Avanza-style Aktieanalys", page_icon="📈", layout="centered")

# Avanza-inspirerad stil
st.markdown("""
    <style>
    body, .stApp {
        background-color: #0e1e2a;
        color: #ffffff;
    }
    .reportview-container .main .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
    }
    .metric-container {
        background-color: #142d42;
        padding: 1rem;
        border-radius: 10px;
        margin-bottom: 1rem;
        color: white;
        text-align: center;
    }
    h1, h2, h3, p {
        color: #e6f1f5;
    }
    </style>
""", unsafe_allow_html=True)

# RSI-beräkning
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
    if df.empty:
        return pd.DataFrame()
    df['RSI'] = compute_rsi(df['Close'])
    df['MA14'] = df['Close'].rolling(window=14).mean()
    df['MA50'] = df['Close'].rolling(window=50).mean()
    return df.dropna()

# Ticker-map
stock_names = {
    "saab": "SAAB-B.ST",
    "evo": "EVO.ST",
    "tesla": "TSLA",
    "apple": "AAPL",
    "volvo": "VOLV-B.ST"
}

# Rubrik
st.markdown("<h1 style='text-align: center;'>📈 Aktieanalys – Avanza-stil</h1>", unsafe_allow_html=True)

# Användarinput
user_input = st.text_input("🔍 Sök bolag (t.ex. 'saab', 'tesla')").strip().lower()

def resolve_ticker(user_input):
    if user_input in stock_names:
        return stock_names[user_input]
    try:
        if not yf.download(user_input.upper(), period='1d').empty:
            return user_input.upper()
    except:
        return None
    return None

if user_input:
    ticker = resolve_ticker(user_input)
    if ticker is None:
        st.error("Kunde inte hitta bolaget.")
    else:
        df = get_data(ticker)
        if df.empty:
            st.warning("Ingen data hittades.")
        else:
            latest_close = df['Close'].iloc[-1]
            latest_rsi = df['RSI'].iloc[-1]

            # VISA METRIK
            st.markdown(f"""
            <div class="metric-container">
                <h2>{user_input.capitalize()} ({ticker})</h2>
                <p>💰 Stängningspris: <b>{latest_close:.2f} SEK</b></p>
                <p>📊 RSI: <b>{latest_rsi:.2f}</b></p>
            </div>
            """, unsafe_allow_html=True)

            # Prisgraf
            st.write("📉 Pris & medelvärden:")
            price_chart = alt.Chart(df.reset_index()).transform_fold(
                ['Close', 'MA14', 'MA50'], as_=['Typ', 'Värde']
            ).mark_line().encode(
                x='Date:T',
                y='Värde:Q',
                color=alt.Color('Typ:N', scale=alt.Scale(scheme='dark2')),
                tooltip=['Date:T', 'Close:Q', 'MA14:Q', 'MA50:Q']
            ).properties(width=700, height=400).interactive()
            st.altair_chart(price_chart)

            # RSI-graf
            st.write("📈 RSI över tid:")
            rsi_chart = alt.Chart(df.reset_index()).mark_line(color='orange').encode(
                x='Date:T',
                y='RSI:Q'
            ).properties(width=700, height=150)
            st.altair_chart(rsi_chart)

            # Volym
            st.write("📦 Volym:")
            vol_chart = alt.Chart(df.reset_index()).mark_bar(color='#4db8ff').encode(
                x='Date:T',
                y='Volume:Q'
            ).properties(width=700, height=120)
            st.altair_chart(vol_chart)

            # Tabell
            st.write("📋 Öppnings- och stängningspriser:")
            st.dataframe(df[['Open', 'Close']].sort_index(ascending=False).round(2))

# Signatur
st.markdown("<p style='text-align: center; color: gray; font-size: 13px;'>© 2025 av Julius</p>", unsafe_allow_html=True)