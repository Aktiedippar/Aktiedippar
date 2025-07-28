import streamlit as st
import yfinance as yf
import pandas as pd
import altair as alt
from datetime import datetime, timedelta

# Användarens sökning
st.set_page_config(page_title="Aktiedippar", layout="wide", page_icon="📉")

# Bakgrundsfärg: marinblå
page_bg = """
<style>
body {
    background-color: #0a1e3f;
    color: white;
}
h1, h2, h3 {
    color: white;
    text-align: center;
}
</style>
"""
st.markdown(page_bg, unsafe_allow_html=True)

# Titel
st.markdown("<h1>📊 Aktiedippar</h1>", unsafe_allow_html=True)

# Diskret namn
st.markdown("<p style='text-align: right; font-size: 12px;'>av Julius</p>", unsafe_allow_html=True)

# Sökruta
user_input = st.text_input("🔍 Sök efter ett företag (t.ex. 'saab')").upper()

# Mapping av namn till tickers
ticker_map = {
    "SAAB": "SAAB-B.ST",
    "TESLA": "TSLA",
    "VOLVO": "VOLV-B.ST",
    "EVO": "EVO.ST",
    "EVOLUTION": "EVO.ST"
}

ticker = ticker_map.get(user_input, user_input if "." in user_input or user_input == "" else None)

if ticker:
    try:
        end_date = datetime.today()
        start_date = end_date - timedelta(days=90)

        df = yf.download(ticker, start=start_date, end=end_date)
        if df.empty:
            st.warning(f"Ingen data hittades för {user_input} ({ticker}).")
        else:
            df = df[['Open', 'Close']].dropna()
            df.reset_index(inplace=True)

            # Visa senaste stängningspris
            latest_close = df['Close'].iloc[-1] if not df.empty else None
            if latest_close is not None:
                st.write(f"💰 Senaste stängningspris: **{latest_close:.2f} SEK**")
            else:
                st.write("💰 Stängningspris kunde inte hämtas.")

            # Skapa proportionerlig graf
            min_price = df['Close'].min()
            max_price = df['Close'].max()

            base = alt.Chart(df).encode(
                x=alt.X("Date:T", title="Datum"),
                y=alt.Y("Close:Q", title="Stängningspris (SEK)", scale=alt.Scale(domain=[min_price * 0.95, max_price * 1.05]))
            )

            line = base.mark_line(color="deepskyblue", strokeWidth=2).encode(
                tooltip=["Date:T", "Close:Q"]
            )

            # Glidande medelvärde (SMA 20)
            df["SMA20"] = df["Close"].rolling(window=20).mean()
            sma_line = alt.Chart(df).mark_line(color="orange", strokeDash=[5,5]).encode(
                x="Date:T",
                y="SMA20:Q"
            )

            st.altair_chart((line + sma_line).interactive(), use_container_width=True)

            # Tabell
            st.subheader("📋 Data de senaste 90 dagarna")
            st.dataframe(df[["Date", "Open", "Close"]].sort_values("Date", ascending=False).round(2))

    except Exception as e:
        st.error(f"Något gick fel: {str(e)}")
else:
    if user_input:
        st.warning("⚠️ Hittade ingen ticker för det namnet.")