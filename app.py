import streamlit as st
import yfinance as yf
import pandas as pd
import altair as alt

# --- MARINBLÅ BAKGRUND & LJUS TEXT ---
st.markdown("""
    <style>
    body {
        background-color: #001f3f;
        color: white;
    }
    .stApp {
        background-color: #001f3f;
        color: white;
    }
    h1, h2, h3, h4, h5, h6, p, div, span {
        color: white !important;
    }
    .stDataFrame {
        background-color: #1a1a1a;
    }
    </style>
""", unsafe_allow_html=True)

st.set_page_config(page_title="Aktier som dippar", page_icon="📉", layout="centered")

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

# --- CENTRERAD RUBRIK ---
st.markdown("<h1 style='text-align: center;'>📉 Aktieanalys 📈</h1>", unsafe_allow_html=True)

# --- ANVÄNDARINPUT ---
user_input = st.text_input("Skriv ett företagsnamn eller ticker (t.ex. 'saab', 'tesla', 'AAPL')").strip().lower()

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
            # Gissad valuta
            currency = "SEK" if ".ST" in ticker else "USD"

            st.subheader(f"{user_input.capitalize()} ({ticker})")

            try:
                latest_close = float(df['Close'].iloc[-1])
                latest_rsi = float(df['RSI'].iloc[-1])

                st.write(f"💰 Senaste stängningspris: **{latest_close:.2f} {currency}**")

                if latest_rsi < 30:
                    st.success(f"📉 RSI: **{latest_rsi:.2f}** – Översåld (möjligt köpläge)")
                elif latest_rsi > 70:
                    st.warning(f"📈 RSI: **{latest_rsi:.2f}** – Överköpt (var försiktig)")
                else:
                    st.write(f"📈 RSI: **{latest_rsi:.2f}**")
            except:
                st.warning("⚠️ Kunde inte hämta stängningspris eller RSI.")

            # PRISGRAF
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

            # TABELL
            st.write("📋 Öppnings- och stängningspriser:")
            st.dataframe(df[['Open', 'Close']].sort_index(ascending=False).round(2))
else:
    st.info("🔍 Ange ett företagsnamn eller ticker för att se analysen.")

# --- DISKRET SIGNATUR ---
st.markdown("<p style='text-align: center; color: gray; font-size: 13px;'>© 2025 av Julius</p>", unsafe_allow_html=True)