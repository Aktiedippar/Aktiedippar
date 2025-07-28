import streamlit as st
import yfinance as yf
import pandas as pd
import altair as alt
from datetime import date, timedelta

st.set_page_config(page_title="Aktiedippar", layout="wide")

# --- Färgtema liknande Avanza ---
st.markdown("""
    <style>
        body {
            background-color: #0a1929;
            color: white;
        }
        .css-18e3th9 {
            background-color: #0a1929;
        }
        .stApp {
            background-color: #0a1929;
        }
    </style>
""", unsafe_allow_html=True)

# --- Titel ---
st.markdown("<h1 style='text-align: center; color: white;'>Aktiedippar</h1>", unsafe_allow_html=True)

# --- Sökfält för företagsnamn ---
ticker_input = st.text_input("Sök företag eller ticker", "SAAB")

# --- Ticker-konvertering ---
def get_ticker(name):
    name = name.lower()
    mapping = {
        "saab": "SAAB-B.ST",
        "volvo": "VOLV-B.ST",
        "evolution": "EVO.ST",
        "hm": "HM-B.ST",
        "ericsson": "ERIC-B.ST",
        "tesla": "TSLA",
        "apple": "AAPL",
        "microsoft": "MSFT"
    }
    return mapping.get(name, name)

ticker = get_ticker(ticker_input)

# --- Hämta historisk data ---
end = date.today()
start = end - timedelta(days=90)

try:
    df = yf.download(ticker, start=start, end=end)

    if df.empty:
        st.error(f"Ingen data hittades för {ticker_input} ({ticker}).")
    else:
        df["Date"] = df.index
        df = df[["Date", "Open", "Close", "Volume"]].dropna()

        # --- RSI-beräkning ---
        delta = df["Close"].diff()
        gain = delta.where(delta > 0, 0)
        loss = -delta.where(delta < 0, 0)
        avg_gain = gain.rolling(window=14).mean()
        avg_loss = loss.rolling(window=14).mean()
        rs = avg_gain / avg_loss
        rsi = 100 - (100 / (1 + rs))
        df["RSI"] = rsi

        # --- SMA20 ---
        df["SMA20"] = df["Close"].rolling(window=20).mean()

        # --- Senaste stängningspris ---
        latest_close = df["Close"].iloc[-1]
        st.write(f"💰 Senaste stängningspris: **{latest_close:.2f} SEK**")

        # --- Grafer ---
        min_price = float(df["Close"].min())
        max_price = float(df["Close"].max())

        chart = alt.Chart(df).mark_line(color="#1f77b4").encode(
            x=alt.X("Date:T", title="Datum"),
            y=alt.Y("Close:Q", title="Stängningspris (SEK)",
                    scale=alt.Scale(domain=[min_price * 0.95, max_price * 1.05]))
        ).properties(
            width=800,
            height=400,
            title="Stängningspris (senaste 3 månaderna)"
        )

        sma_line = alt.Chart(df).mark_line(color="orange").encode(
            x="Date:T",
            y="SMA20:Q"
        )

        st.altair_chart(chart + sma_line, use_container_width=True)

        # --- RSI-graf ---
        rsi_chart = alt.Chart(df).mark_line(color="purple").encode(
            x="Date:T",
            y=alt.Y("RSI:Q", title="RSI")
        ).properties(
            width=800,
            height=200,
            title="RSI (Relative Strength Index)"
        )

        st.altair_chart(rsi_chart, use_container_width=True)

        # --- Tabell ---
        st.dataframe(df[["Open", "Close"]].dropna().sort_index(ascending=False).round(2))

        # --- Diskret signatur ---
        st.markdown("<p style='font-size: 10px; text-align: right; color: grey;'>av Julius</p>", unsafe_allow_html=True)

except Exception as e:
    st.error(f"Något gick fel: {e}")