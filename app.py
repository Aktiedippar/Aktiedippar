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
        return df.dropna()
    except Exception:
        return pd.DataFrame()

# --- ENKEL 7-DAGARS PROGNOS ---
def add_forecast(df):
    lookback_days = 14
    if len(df) < lookback_days:
        df['Forecast'] = False
        return df

    train_df = df.tail(lookback_days).copy()
    train_df['Days'] = (train_df.index - train_df.index.min()).days
    X_train = train_df[['Days']]
    y_train = train_df['Close']

    model = LinearRegression()
    model.fit(X_train, y_train)

    last_date = df.index[-1]
    future_dates = [last_date + timedelta(days=i) for i in range(1, 8)]
    future_days = [(d - train_df.index.min()).days for d in future_dates]
    future_prices = model.predict(np.array(future_days).reshape(-1, 1))

    forecast_df = pd.DataFrame({'Close': future_prices}, index=future_dates)
    forecast_df['Forecast'] = True

    df['Forecast'] = False
    return pd.concat([df, forecast_df])

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
st.markdown(
    "<h1 style='text-align: center;'>📉 Aktieanalys 📈</h1>",
    unsafe_allow_html=True
)

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

            # Valutadetektion
            currency = "SEK" if ticker.endswith(".ST") else "USD"

            # Hämta senaste värden
            try:
                latest_close = float(df['Close'].iloc[-1])
            except Exception:
                latest_close = None

            try:
                latest_rsi = float(df['RSI'].iloc[-1])
            except Exception:
                latest_rsi = None

            # Visa stängningspris
            if latest_close is not None:
                st.write(f"💰 Senaste stängningspris: **{latest_close:.2f} {currency}**")
            else:
                st.warning("❌ Kunde inte hämta stängningspris.")

            # Visa RSI
            if latest_rsi is not None:
                if latest_rsi < 30:
                    st.success(f"📉 RSI: **{latest_rsi:.2f}** – Översåld (möjligt köpläge)")
                elif latest_rsi > 70:
                    st.warning(f"📈 RSI: **{latest_rsi:.2f}** – Överköpt (var försiktig)")
                else:
                    st.write(f"📈 RSI: **{latest_rsi:.2f}**")
            else:
                st.warning("❌ Kunde inte hämta RSI-värde.")

            # Lägg till prognos
            df = add_forecast(df)

            # Prisgraf med prognos
            base = alt.Chart(df.reset_index())

            line_actual = base.transform_filter(
                alt.datum.Forecast == False
            ).mark_line(color='blue').encode(
                x='Date:T',
                y='Close:Q',
                tooltip=['Date:T', 'Close:Q']
            )

            line_forecast = base.transform_filter(
                alt.datum.Forecast == True
            ).mark_line(color='pink', strokeDash=[4, 4]).encode(
                x='Date:T',
                y='Close:Q',
                tooltip=['Date:T', 'Close:Q']
            )

            st.write("📊 Prisgraf med prognos:")
            st.altair_chart((line_actual + line_forecast).properties(width=700, height=400).interactive())

            # Tabell
            st.write("📋 Öppnings- och stängningspriser:")
            st.dataframe(df[df['Forecast'] == False][['Open', 'Close']].sort_index(ascending=False).round(2))

# --- DISKRET SIGNATUR ---
st.markdown("<p style='text-align: center; color: gray; font-size: 13px;'>© 2025 av Julius</p>", unsafe_allow_html=True)