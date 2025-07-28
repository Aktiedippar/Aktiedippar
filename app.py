import streamlit as st
import yfinance as yf
import pandas as pd
import altair as alt

# --- SIDKONFIGURATION ---
st.set_page_config(page_title="Aktier som dippar", page_icon="📉", layout="centered")

# --- BAKGRUND & STIL ---
st.markdown("""
    <style>
    .stApp {
        background-color: #0b1f3a; /* Marinblå */
        color: white;
    }
    h1, h2, h3, h4, h5, h6, p, div, span {
        color: white !important;
    }
    .metric-container {
        background-color: #112b4a;
        padding: 1rem;
        border-radius: 0.5rem;
        margin-bottom: 1rem;
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
            # --- Hämta senaste värden ---
            try:
                latest_close = float(df['Close'].iloc[-1])
            except:
                latest_close = None

            try:
                latest_rsi = float(df['RSI'].iloc[-1])
            except:
                latest_rsi = None

            # --- Visa rubrik och nyckeltal ---
            if latest_close is not None and latest_rsi is not None:
                st.markdown(f"""
                    <div class="metric-container">
                        <h2>{user_input.capitalize()} ({ticker})</h2>
                        <p>💰 Stängningspris: <b>{latest_close:.2f} SEK</b></p>
                        <p>📊 RSI: <b>{latest_rsi:.2f}</b></p>
                    </div>
                """, unsafe_allow_html=True)
            else:
                st.warning("Kunde inte visa stängningspris och RSI.")

            # --- Prisgraf ---
            st.write("📊 Prisgraf:")
            chart = alt.Chart(df.reset_index()).mark_line(color='lightblue').encode(
                x='Date:T',
                y='Close:Q',
                tooltip=['Date:T', 'Close:Q', 'RSI:Q']
            ).properties(
                width=700,
                height=400
            ).interactive()
            st.altair_chart(chart)

            # --- Tabell ---
            st.write("📋 Öppnings- och stängningspriser:")
            if 'Open' in df.columns and 'Close' in df.columns:
                st.dataframe(df[['Open', 'Close']].sort_index(ascending=False).round(2))
            else:
                st.warning("❌ Data saknar öppnings- eller stängningspriser.")
else:
    st.info("🔍 Ange ett företagsnamn eller ticker för att se analysen.")
    st.markdown("<p style='text-align: center; color: gray; font-size: 13px;'>© 2025 av Julius</p>", unsafe_allow_html=True)