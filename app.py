import streamlit as st
import yfinance as yf
import pandas as pd
import altair as alt
from datetime import datetime, timedelta

st.set_page_config(page_title="Aktieanalys", layout="wide")

# Anpassad bakgrundsfärg med mörkblå stil
page_bg = """
<style>
body {
    background-color: #0e1a2b;
    color: white;
}
[data-testid="stHeader"] {
    background: rgba(0,0,0,0);
}
h1 {
    text-align: center;
    color: white;
}
</style>
"""
st.markdown(page_bg, unsafe_allow_html=True)

st.markdown("<h1>📈 Aktieanalys</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align:center;'>av Julius</p>", unsafe_allow_html=True)

# Inputruta
user_input = st.text_input("Sök efter företagsnamn eller ticker (t.ex. 'saab', 'evo', 'TSLA')").strip()

ticker_map = {
    "saab": "SAAB-B.ST",
    "evo": "EVO.ST",
    "volvo": "VOLV-B.ST",
    "ericsson": "ERIC-B.ST",
    "tesla": "TSLA",
    "apple": "AAPL",
    "google": "GOOGL",
}

if user_input:
    ticker_symbol = ticker_map.get(user_input.lower(), user_input.upper())

    try:
        end_date = datetime.today()
        start_date = end_date - timedelta(days=90)

        df = yf.download(ticker_symbol, start=start_date, end=end_date)
        if df.empty:
            st.error(f"Ingen data hittades för {ticker_symbol}.")
        else:
            df.reset_index(inplace=True)
            df['Date'] = pd.to_datetime(df['Date'])

            # Senaste stängningspris
            latest_close = df['Close'].tail(1)
            if not latest_close.empty:
                st.write(f"💰 Senaste stängningspris: **{latest_close.values[0]:.2f} SEK**")
            else:
                st.write("Ingen stängningsdata tillgänglig.")

            # SMA (20-dagars)
            df['SMA20'] = df['Close'].rolling(window=20).mean()

            # Bestäm proportionell skala
            min_price = df["Close"].min()
            max_price = df["Close"].max()

            chart = alt.Chart(df).mark_line().encode(
                x=alt.X("Date:T", title="Datum"),
                y=alt.Y("Close:Q", title="Stängningspris (SEK)",
                        scale=alt.Scale(domain=[min_price * 0.95, max_price * 1.05])),
                tooltip=["Date:T", "Close:Q"]
            ).properties(
                title=f"{ticker_symbol} - Kursutveckling",
                width=900,
                height=400
            ).interactive()

            sma_line = alt.Chart(df).mark_line(color='orange').encode(
                x="Date:T",
                y="SMA20:Q"
            )

            st.altair_chart(chart + sma_line, use_container_width=True)

            # Visa tabell
            st.subheader("📊 Tabell: Öppnings- och stängningspriser")
            st.dataframe(df[['Date', 'Open', 'Close']].dropna().sort_values(by='Date', ascending=False).round(2))

    except Exception as e:
        st.error(f"Något gick fel: {e}")