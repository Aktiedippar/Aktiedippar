import streamlit as st
import yfinance as yf
import pandas as pd
import altair as alt

# --- SIDKONFIGURATION ---
st.set_page_config(page_title="Aktier som dippar", page_icon="📉", layout="centered")

# --- STIL FÖR MARINEBLÅ BAKGRUND ---
st.markdown("""
    <style>
    body {
        background-color: #0f1c2e;
        color: white;
    }
    .stApp {
        background-color: #0f1c2e;
        color: white;
    }
    h1, h2, h3, h4, h5, h6, p, div, span {
        color: white !important;
    }
    .stDataFrame {
        background-color: #1a1a1a;
        color: white;
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
        df['MA14'] = df['Close'].rolling(window=14).mean()
        df['MA50'] = df['Close'].rolling(window=50).mean()
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

# --- RESOLVERAR TICKER ---
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

# --- HANTERA TICKER & VISA DATA ---
if user_input:
    ticker = resolve_ticker(user_input)

    if ticker is None:
        st.error("❌ Kunde inte hitta någon giltig ticker för det du skrev.")
    else:
        df = get_data(ticker)

        if df.empty:
            st.error(f"⚠️ Ingen data hittades för {user_input.upper()} ({ticker}).")
        else:
            st.subheader(f"{user_input.capitalize()} ({ticker})")

            try:
                latest_close = float(df['Close'].iloc[-1])
            except Exception:
                latest_close = None

            try:
                latest_rsi = float(df['RSI'].iloc[-1])
            except Exception:
                latest_rsi = None

            if latest_close is not None:
                st.write(f"💰 Senaste stängningspris: **{latest_close:.2f} SEK**")

            if latest_rsi is not None:
                if latest_rsi < 30:
                    st.success(f"📉 RSI: **{latest_rsi:.2f}** – Översåld (möjligt köpläge)")
                elif latest_rsi > 70:
                    st.warning(f"📈 RSI: **{latest_rsi:.2f}** – Överköpt (var försiktig)")
                else:
                    st.write(f"📈 RSI: **{latest_rsi:.2f}**")

            # --- PRISGRAF MED MA ---
            st.write("📊 Pris & Medelvärden:")
            price_chart = alt.Chart(df.reset_index()).transform_fold(
                ['Close', 'MA14', 'MA50'],
                as_=['Typ', 'Värde']
            ).mark_line().encode(
                x='Date:T',
                y='Värde:Q',
                color='Typ:N',
                tooltip=['Date:T', 'Close:Q', 'MA14:Q', 'MA50:Q']
            ).properties(width=700, height=400).interactive()
            st.altair_chart(price_chart)

            # --- VOLUMGRAF ---
            st.write("📦 Volym:")
            volume_chart = alt.Chart(df.reset_index()).mark_bar(color='lightblue').encode(
                x='Date:T',
                y='Volume:Q'
            ).properties(width=700, height=120)
            st.altair_chart(volume_chart)

            # --- RSI-GRAF ---
            st.write("📈 RSI över tid:")
            rsi_chart = alt.Chart(df.reset_index()).mark_line(color='orange').encode(
                x='Date:T',
                y='RSI:Q'
            ).properties(width=700, height=150)
            st.altair_chart(rsi_chart)

            # --- TABELL ---
            st.write("📋 Öppnings- och stängningspriser:")
            st.dataframe(df[['Open', 'Close']].sort_index(ascending=False).round(2))

# --- DISKRET SIGNATUR ---
st.markdown("<p style='text-align: center; color: gray; font-size: 13px;'>© 2025 av Julius</p>", unsafe_allow_html=True)