import streamlit as st
import yfinance as yf
import pandas as pd
import altair as alt

# --- APP KONFIGURATION ---
st.set_page_config(page_title="Aktier som dippar", page_icon="📉", layout="centered")

# --- ANPASSAD STIL (inspirerad av Avanza) ---
st.markdown("""
    <style>
    body, .stApp {
        background-color: #f8f9fa;
        color: #212529;
        font-family: 'Helvetica', sans-serif;
    }
    h1, h2, h3 {
        color: #0046b8;
    }
    .metric-box {
        background-color: #ffffff;
        padding: 1rem;
        border-radius: 8px;
        box-shadow: 0 2px 5px rgba(0,0,0,0.05);
        margin-bottom: 1rem;
    }
    .footer {
        text-align: center;
        color: gray;
        font-size: 13px;
        margin-top: 2rem;
    }
    </style>
""", unsafe_allow_html=True)

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
    try:
        df = yf.download(ticker, period='3mo', interval='1d', auto_adjust=False)
        if df.empty or 'Close' not in df.columns:
            return pd.DataFrame()
        df['RSI'] = compute_rsi(df['Close'])
        df['SMA20'] = df['Close'].rolling(window=20).mean()
        df['SMA50'] = df['Close'].rolling(window=50).mean()
        return df.dropna()
    except Exception:
        return pd.DataFrame()

# --- NAMN -> TICKER MAPPNING ---
stock_names = {
    "saab": "SAAB-B.ST",
    "evo": "EVO.ST",
    "evolution": "EVO.ST",
    "betsson": "BETS-B.ST",
    "kindred": "KIND-SDB.ST",
    "volvo": "VOLV-B.ST",
    "tesla": "TSLA",
    "apple": "AAPL"
}

# --- RUBRIK ---
st.markdown("<h1 style='text-align: center;'>📉 Aktieanalys</h1>", unsafe_allow_html=True)

# --- ANVÄNDARINPUT ---
user_input = st.text_input("🔎 Skriv ett företagsnamn eller ticker (t.ex. 'saab', 'tesla', 'AAPL')").strip().lower()

def resolve_ticker(user_input):
    if user_input in stock_names:
        return stock_names[user_input]
    try:
        test_df = yf.download(user_input.upper(), period='1d')
        if not test_df.empty:
            return user_input.upper()
    except:
        pass
    return None

if user_input:
    ticker = resolve_ticker(user_input)

    if ticker is None:
        st.error("❌ Kunde inte hitta någon giltig ticker för det du skrev.")
    else:
        df = get_data(ticker)

        if df.empty:
            st.error(f"⚠️ Ingen data hittades för {user_input.upper()} ({ticker}).")
        else:
            # --- METRIKSEKTION ---
            latest_close = float(df['Close'].iloc[-1]) if 'Close' in df.columns else None
            latest_rsi = float(df['RSI'].iloc[-1]) if 'RSI' in df.columns else None

            st.markdown("<div class='metric-box'>", unsafe_allow_html=True)
            st.subheader(f"{user_input.capitalize()} ({ticker})")
            if latest_close is not None:
                st.write(f"💰 Senaste stängningspris: **{latest_close:.2f} SEK**")
            if latest_rsi is not None:
                st.write(f"📊 RSI: **{latest_rsi:.2f}**")
            st.markdown("</div>", unsafe_allow_html=True)

            # --- GRAF ---
            st.write("📈 Prisgraf med glidande medelvärden:")
            chart = alt.Chart(df.reset_index()).mark_line().encode(
                x='Date:T',
                y='Close:Q',
                tooltip=['Date:T', 'Close:Q', 'RSI:Q']
            ).properties(width=700, height=400)

            sma20_line = alt.Chart(df.reset_index()).mark_line(color='green').encode(
                x='Date:T',
                y='SMA20:Q'
            )

            sma50_line = alt.Chart(df.reset_index()).mark_line(color='orange').encode(
                x='Date:T',
                y='SMA50:Q'
            )

            st.altair_chart(chart + sma20_line + sma50_line)

            # --- TABELL ---
            st.write("📋 Öppnings- och stängningspriser:")
            st.dataframe(df[['Open', 'Close']].sort_index(ascending=False).round(2))

# --- INFO OM SIGNATUR ---
else:
    st.info("🔍 Ange ett företagsnamn eller ticker för att se analysen.")

st.markdown("<div class='footer'>© 2025 av Julius</div>", unsafe_allow_html=True)
