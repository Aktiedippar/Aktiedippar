import streamlit as st
import yfinance as yf
import pandas as pd
import altair as alt
from datetime import date, timedelta

st.set_page_config(page_title="Aktiedippar", layout="wide")

# --- CSS-styling för Avanza-liknande känsla ---
st.markdown("""
    <style>
    body {
        background-color: #f4f6f9;
    }
    .title {
        font-size: 40px;
        font-weight: bold;
        text-align: center;
        margin-bottom: 20px;
        color: #14375A;
    }
    .footer {
        font-size: 14px;
        color: gray;
        text-align: center;
        margin-top: 50px;
    }
    </style>
""", unsafe_allow_html=True)

st.markdown('<div class="title">📈 Aktiedippar</div>', unsafe_allow_html=True)

# --- Funktion för att hitta ticker från företagsnamn ---
def get_ticker(name):
    name = name.lower()
    mapping = {
        "saab": "SAAB-B.ST",
        "volvo": "VOLV-B.ST",
        "tesla": "TSLA",
        "apple": "AAPL",
        "evolution": "EVO.ST",
        "hm": "HM-B.ST",
        "h&m": "HM-B.ST"
    }
    return mapping.get(name, name.upper())

# --- Datuminställningar ---
end_date = date.today()
start_date = end_date - timedelta(days=90)

# --- Sökfält ---
user_input = st.text_input("Sök aktie (t.ex. 'saab', 'tesla', 'apple'):")

if user_input:
    ticker = get_ticker(user_input)
    df = yf.download(ticker, start=start_date, end=end_date)

    if df.empty:
        st.error(f"Ingen data hittades för {user_input} ({ticker}).")
    else:
        df.reset_index(inplace=True)

        # --- RSI (Relative Strength Index) ---
        delta = df["Close"].diff()
        gain = delta.where(delta > 0, 0)
        loss = -delta.where(delta < 0, 0)
        avg_gain = gain.rolling(window=14).mean()
        avg_loss = loss.rolling(window=14).mean()
        rs = avg_gain / avg_loss
        df["RSI"] = 100 - (100 / (1 + rs))

        # --- SMA 20 (Simple Moving Average) ---
        df["SMA 20"] = df["Close"].rolling(window=20).mean()

        # --- Hämta senaste stängningspris ---
        if not df["Close"].empty:
            latest_close = df["Close"].iloc[-1]
            st.write(f"💰 Senaste stängningspris: **{latest_close:.2f} SEK**")

        # --- Beräkna dynamiskt y-intervall för bättre graf ---
        min_price = df["Close"].min()
        max_price = df["Close"].max()
        y_scale = alt.Scale(domain=[min_price * 0.95, max_price * 1.05])

        # --- Prisgraf med SMA 20 ---
        base = alt.Chart(df).encode(
            x="Date:T",
            y=alt.Y("Close:Q", title="Stängningspris (SEK)", scale=y_scale)
        )

        line_close = base.mark_line(color="#1f77b4").encode(
            tooltip=["Date:T", "Close:Q"]
        )

        sma_line = base.mark_line(color="orange").encode(
            y="SMA 20:Q",
            tooltip=["Date:T", "SMA 20:Q"]
        )

        st.altair_chart((line_close + sma_line).properties(title="📉 Prisgraf med SMA 20"), use_container_width=True)

        # --- Volymgraf ---
        volume_chart = alt.Chart(df).mark_bar(color="#7f7f7f").encode(
            x="Date:T",
            y="Volume:Q",
            tooltip=["Date:T", "Volume"]
        ).properties(height=100, title="📊 Volym")

        st.altair_chart(volume_chart, use_container_width=True)

        # --- RSI-graf ---
        rsi_chart = alt.Chart(df).mark_line(color="purple").encode(
            x="Date:T",
            y=alt.Y("RSI:Q", scale=alt.Scale(domain=[0, 100])),
            tooltip=["Date:T", "RSI:Q"]
        ).properties(title="📈 RSI (14 dagar)")

        st.altair_chart(rsi_chart, use_container_width=True)

        # --- Tabell med öppnings- och stängningspriser ---
        st.subheader("📅 Öppnings- och stängningspriser")
        st.dataframe(df[["Date", "Open", "Close"]].dropna().sort_values("Date", ascending=False).round(2))

# --- Diskret signatur ---
st.markdown('<div class="footer">Byggd med ❤️ av Julius</div>', unsafe_allow_html=True)