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

# --- DATAHÄMTNING ---
def get_data(ticker):
    try:
        df = yf.download(ticker, period='3mo', interval='1d', auto_adjust=False)
        if df.empty or 'Close' not in df.columns:
            return pd.DataFrame()
        df['RSI'] = compute_rsi(df['Close'])
        df['Forecast'] = False  # markera verkliga data
        return df.dropna()
    except Exception:
        return pd.DataFrame()

# --- SKAPA 7-DAGARS PROGNOS ---
def add_forecast(df):
    df = df.copy()
    df = df.reset_index()

    # Konvertera datum till numeriskt värde
    df['Date_ordinal'] = df['Date'].map(pd.Timestamp.toordinal)
    X = df['Date_ordinal'].values.reshape(-1, 1)
    y = df['Close'].values

    model = LinearRegression()
    model.fit(X, y)

    # Skapa framtida datum
    last_date = df['Date'].max()
    future_dates = [last_date + timedelta(days=i) for i in range(1, 8)]
    future_ordinals = np.array([d.toordinal() for d in future_dates]).reshape(-1, 1)
    future_prices = model.predict(future_ordinals)

    forecast_df = pd.DataFrame({
        'Date': future_dates,
        'Close': future_prices.ravel(),
        'Forecast': True
    })

    forecast_df.set_index('Date', inplace=True)
    df.set_index('Date', inplace=True)

    combined = pd.concat([df, forecast_df], sort=False)
    return combined

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
            df = add_forecast(df)

            # Gissad valuta
            currency = "SEK" if ".ST" in ticker else "USD"

            st.subheader(f"{user_input.capitalize()} ({ticker})")

            historical_df = df[df['Forecast'] == False]

            if not historical_df.empty:
                latest_close = historical_df['Close'].iloc[-1]
                latest_rsi = historical_df['RSI'].iloc[-1]

                st.write(f"💰 Senaste stängningspris: **{latest_close:.2f} {currency}**")

                if latest_rsi < 30:
                    st.success(f"📉 RSI: **{latest_rsi:.2f}** – Översåld (möjligt köpläge)")
                elif latest_rsi > 70:
                    st.warning(f"📈 RSI: **{latest_rsi:.2f}** – Överköpt (var försiktig)")
                else:
                    st.write(f"📈 RSI: **{latest_rsi:.2f}**")
            else:
                st.warning("⚠️ Ingen giltig historisk data hittades för att visa stängningspris och RSI.")

            # PRISGRAF: blå = verklig, rosa = prognos
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

            # TABELL: bara historisk data med Open & Close
            st.write("📋 Öppnings- och stängningspriser:")
            st.dataframe(
                historical_df[['Open', 'Close']].dropna().sort_index(ascending=False).round(2)
            )

else:
    st.info("🔍 Ange ett företagsnamn eller ticker för att se analysen.")

# --- DISKRET SIGNATUR ---
st.markdown("<p style='text-align: center; color: gray; font-size: 13px;'>© 2025 av Julius</p>", unsafe_allow_html=True)