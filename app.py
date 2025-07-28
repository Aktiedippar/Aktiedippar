import streamlit as st
import yfinance as yf
import pandas as pd
import altair as alt
from sklearn.linear_model import LinearRegression
from datetime import timedelta
import numpy as np

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

# --- DATAHÄMTNING MED PROGNOS ---
def get_data_with_forecast(ticker):
    df = yf.download(ticker, period='3mo', interval='1d', auto_adjust=False)

    if df.empty or 'Close' not in df.columns:
        return pd.DataFrame()

    df['RSI'] = compute_rsi(df['Close'])
    df = df.dropna()
    df['Forecast'] = False  # Markera som historiska värden

    # Prognos på 7 dagar med linjär regression
    try:
        df_model = df.tail(14).copy()
        df_model['Days'] = (df_model.index - df_model.index.min()).days
        X = df_model[['Days']]
        y = df_model['Close']
        model = LinearRegression()
        model.fit(X, y)

        future_dates = [df.index[-1] + timedelta(days=i) for i in range(1, 8)]
        future_days = [(d - df.index.min()).days for d in future_dates]
        future_prices = model.predict(np.array(future_days).reshape(-1, 1))

        forecast_df = pd.DataFrame({'Close': future_prices.ravel()}, index=future_dates)
        forecast_df['Forecast'] = True

        df_combined = pd.concat([df, forecast_df])
        return df_combined

    except Exception as e:
        return df

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
        df = get_data_with_forecast(ticker)

        if df.empty:
            st.error(f"⚠️ Ingen data hittades för {user_input.upper()} ({ticker}).")
        else:
            st.subheader(f"{user_input.capitalize()} ({ticker})")

            currency = "SEK" if ".ST" in ticker else "USD"

            # Hämta senaste stängningspris
            latest_close = df[df['Forecast'] == False]['Close'].iloc[-1]
            latest_rsi = df[df['Forecast'] == False]['RSI'].iloc[-1]

            st.write(f"💰 Senaste stängningspris: **{latest_close:.2f} {currency}**")

            # Visa RSI
            if latest_rsi < 30:
                st.success(f"📉 RSI: **{latest_rsi:.2f}** – Översåld (möjligt köpläge)")
            elif latest_rsi > 70:
                st.warning(f"📈 RSI: **{latest_rsi:.2f}** – Överköpt (var försiktig)")
            else:
                st.write(f"📈 RSI: **{latest_rsi:.2f}**")

            # --- GRAF ---
            base = alt.Chart(df.reset_index())

            actual = base.transform_filter(
                alt.datum.Forecast == False
            ).mark_line(color='blue').encode(
                x='Date:T',
                y='Close:Q',
                tooltip=['Date:T', 'Close:Q']
            )

            forecast = base.transform_filter(
                alt.datum.Forecast == True
            ).mark_line(color='pink', strokeDash=[4, 4]).encode(
                x='Date:T',
                y='Close:Q',
                tooltip=['Date:T', 'Close:Q']
            )

            st.write("📊 Prisgraf med 7-dagars prognos:")
            st.altair_chart((actual + forecast).properties(width=700, height=400).interactive())

            # --- TABELL ---
            st.write("📋 Öppnings- och stängningspriser (historiska):")
            st.dataframe(
                df[df['Forecast'] == False][['Open', 'Close']]
                .dropna()
                .sort_index(ascending=False)
                .round(2)
            )

# --- SIGNATUR ---
st.markdown("<p style='text-align: center; color: gray; font-size: 13px;'>© 2025 av Julius</p>", unsafe_allow_html=True)