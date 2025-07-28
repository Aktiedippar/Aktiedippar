
import streamlit as st
import yfinance as yf
import pandas as pd
import altair as alt

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
            st.subheader(f"{user_input.capitalize()} ({ticker})")

            # Hämta senaste värden
            try:
                latest_close = float(df['Close'].iloc[-1])
            except Exception:
                latest_close = None

            try:
                latest_rsi = float(df['RSI'].iloc[-1])
            except Exception:
                latest_rsi = None

            if latest_close is not None:
                st.markdown(f"<p>💰 Stängningspris: <b>{latest_close:.2f} SEK</b></p>", unsafe_allow_html=True)
            else:
                st.warning("❌ Kunde inte hämta stängningspris.")

            if latest_rsi is not None:
                if latest_rsi < 30:
                    st.success(f"📉 RSI: **{latest_rsi:.2f}** – Översåld (möjligt köpläge)")
                elif latest_rsi > 70:
                    st.warning(f"📈 RSI: **{latest_rsi:.2f}** – Överköpt (var försiktig)")
                else:
                    st.info(f"📈 RSI: **{latest_rsi:.2f}**")
            else:
                st.warning("❌ Kunde inte hämta RSI-värde.")

            # 📊 Prisgraf med SMA
            st.write("📊 Prisgraf med glidande medelvärden:")

            base = alt.Chart(df.reset_index()).encode(
                x=alt.X("Date:T", title="Datum")
            )

            price_line = base.mark_line(color="#1f77b4", strokeWidth=2).encode(
                y=alt.Y("Close:Q", title="Stängningspris"),
                tooltip=["Date:T", alt.Tooltip("Close:Q", title="Pris (SEK)")]
            )

            sma20_line = base.mark_line(color="#ff7f0e", strokeDash=[5, 5]).encode(
                y="SMA20:Q",
                tooltip=[alt.Tooltip("SMA20:Q", title="SMA 20")]
            )

            sma50_line = base.mark_line(color="#2ca02c", strokeDash=[2, 2]).encode(
                y="SMA50:Q",
                tooltip=[alt.Tooltip("SMA50:Q", title="SMA 50")]
            )

            chart = alt.layer(price_line, sma20_line, sma50_line).properties(
                width=750,
                height=400,
                title="Prisgraf med SMA 20 & SMA 50"
            ).configure_title(
                fontSize=18,
                anchor="start",
                font="Helvetica"
            ).configure_axis(
                labelFontSize=12,
                titleFontSize=14
            )

            st.altair_chart(chart)

            # Tabell
            st.write("📋 Öppnings- och stängningspriser:")
            st.dataframe(df[['Open', 'Close']].dropna().sort_index(ascending=False).round(2))

else:
    st.info("🔍 Ange ett företagsnamn eller ticker för att se analysen.")
    st.markdown("<p style='text-align: center; color: gray; font-size: 13px;'>© 2025 av Julius</p>", unsafe_allow_html=True)
