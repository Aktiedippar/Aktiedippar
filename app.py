import streamlit as st
import yfinance as yf
import pandas as pd
import altair as alt
from datetime import datetime, timedelta

st.set_page_config(page_title="Aktiedippar", layout="wide")

# --- Stilmall för Avanza-liknande utseende ---
st.markdown("""
    <style>
        body {
            background-color: #001f3f;
            color: white;
        }
        .block-container {
            padding-top: 2rem;
            padding-bottom: 2rem;
        }
        h1 {
            color: #39CCCC;
            text-align: center;
        }
        .stDataFrame {
            background-color: white;
            color: black;
        }
        footer {
            visibility: hidden;
        }
        .creator {
            text-align: center;
            font-size: 12px;
            color: #bbbbbb;
            margin-top: 30px;
        }
    </style>
""", unsafe_allow_html=True)

st.markdown("<h1>📊 Aktiedippar</h1>", unsafe_allow_html=True)

# --- Sökruta för företagsnamn ---
user_input = st.text_input("Sök företagsnamn eller ticker", value="Saab")

# --- Automatisk konvertering från namn till ticker ---
ticker_map = {
    "saab": "SAAB-B.ST",
    "volvo": "VOLV-B.ST",
    "evolution": "EVO.ST",
    "tesla": "TSLA",
    "apple": "AAPL",
    "microsoft": "MSFT",
    "google": "GOOGL"
}

ticker = ticker_map.get(user_input.lower(), user_input.upper())

try:
    end_date = datetime.today()
    start_date = end_date - timedelta(days=90)

    df = yf.download(ticker, start=start_date, end=end_date)
    if df.empty:
        st.error(f"Ingen data hittades för {user_input} ({ticker}).")
    else:
        df = df[['Open', 'Close', 'Volume']]
        df.dropna(inplace=True)
        df.index = pd.to_datetime(df.index)

        # Hämta senaste stängningspriset (sista datumet)
        latest_close = df["Close"].iloc[-1]
        st.write(f"💰 Senaste stängningspris: **{latest_close:.2f} SEK**")

        # SMA
        df["SMA 20"] = df["Close"].rolling(window=20).mean()

        # RSI
        delta = df["Close"].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
        rs = gain / loss
        df["RSI"] = 100 - (100 / (1 + rs))

        # --- Graf ---
        min_price = df["Close"].min()
        max_price = df["Close"].max()

        base = alt.Chart(df.reset_index()).encode(
            x=alt.X("Date:T", title="Datum"),
            y=alt.Y("Close:Q", title="Stängningspris (SEK)",
                   scale=alt.Scale(domain=[min_price * 0.95, max_price * 1.05]))
        )

        close_line = base.mark_line(color="lightblue").encode(
            tooltip=["Date:T", "Close:Q"]
        )

        sma_line = base.mark_line(color="orange").encode(
            y="SMA 20:Q",
            tooltip=["Date:T", "SMA 20:Q"]
        )

        st.altair_chart(close_line + sma_line, use_container_width=True)

        # Visa tabell
        st.dataframe(df[['Open', 'Close']].dropna().sort_index(ascending=False).round(2))

        # Visa RSI-graf
        rsi_chart = alt.Chart(df.reset_index()).mark_line(color="pink").encode(
            x="Date:T",
            y=alt.Y("RSI:Q", title="RSI"),
            tooltip=["Date:T", "RSI:Q"]
        ).properties(title="RSI (Relative Strength Index)")
        st.altair_chart(rsi_chart, use_container_width=True)

        # Skapare
        st.markdown("<div class='creator'>av Julius</div>", unsafe_allow_html=True)

except Exception as e:
    st.error(f"Något gick fel: {e}")