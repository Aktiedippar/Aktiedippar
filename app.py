import streamlit as st
import pandas as pd
import yfinance as yf
import altair as alt
import numpy as np
from datetime import datetime, timedelta

# Snyggare layout med marinblå känsla
st.set_page_config(page_title="Aktiedippar", layout="wide")
st.markdown(
    """
    <style>
    body {
        background-color: #001F3F;
        color: white;
    }
    .stApp {
        background-color: #001F3F;
    }
    h1, h2, h3, .stTextInput, .stSelectbox {
        color: white;
    }
    .css-1v0mbdj {
        color: white !important;
    }
    </style>
    """,
    unsafe_allow_html=True
)

st.title("📊 Aktieanalysverktyg")

# Sökruta
user_input = st.text_input("Sök företagsnamn eller ticker (t.ex. 'saab' eller 'TSLA')").upper()

# Automatisk konvertering av vanliga namn
name_to_ticker = {
    "SAAB": "SAAB-B.ST",
    "TESLA": "TSLA",
    "EVO": "EVO.ST",
    "VOLVO": "VOLV-B.ST",
}
ticker = name_to_ticker.get(user_input, user_input)

if ticker:
    try:
        end_date = datetime.today()
        start_date = end_date - timedelta(days=90)
        df = yf.download(ticker, start=start_date, end=end_date)

        if df.empty:
            st.error(f"Ingen data hittades för {user_input} ({ticker}).")
        else:
            df['SMA20'] = df['Close'].rolling(window=20).mean()

            # RSI
            delta = df['Close'].diff()
            gain = delta.where(delta > 0, 0)
            loss = -delta.where(delta < 0, 0)
            avg_gain = gain.rolling(window=14).mean()
            avg_loss = loss.rolling(window=14).mean()
            rs = avg_gain / avg_loss
            df['RSI'] = 100 - (100 / (1 + rs))

            # Snyggare prisvisning
            latest_close = df['Close'].dropna()
            if not latest_close.empty:
                value = float(latest_close.iloc[-1])
                st.markdown(f"### 💰 Senaste stängningspris: **{value:.2f} SEK**")
            else:
                st.warning("Kunde inte hämta stängningspris.")

            # Tabell
            st.dataframe(df[['Open', 'Close']].dropna().sort_index(ascending=False).round(2))

            # Proportionerlig skala
            min_price = df['Close'].min()
            max_price = df['Close'].max()

            base = alt.Chart(df.reset_index()).encode(
                x='Date:T'
            )

            close_line = base.mark_line(color='deepskyblue').encode(
                y=alt.Y('Close:Q', title='Stängningspris (SEK)', scale=alt.Scale(domain=[min_price*0.95, max_price*1.05]))
            )

            sma_line = base.mark_line(color='orange').encode(
                y='SMA20:Q'
            )

            st.altair_chart(close_line + sma_line, use_container_width=True)

            # RSI-graf
            rsi_chart = alt.Chart(df.reset_index()).mark_line(color='violet').encode(
                x='Date:T',
                y=alt.Y('RSI:Q', title='RSI')
            ).properties(
                height=200,
                title="RSI (Relative Strength Index)"
            )
            st.altair_chart(rsi_chart, use_container_width=True)

    except Exception as e:
        st.error(f"Något gick fel: {e}")