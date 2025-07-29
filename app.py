import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objs as go
from datetime import datetime, timedelta
from sklearn.linear_model import LinearRegression
import numpy as np

st.set_page_config(page_title="Aktieanalys", layout="wide")
st.title("📈 Aktieanalysverktyg")

user_input = st.text_input("Sök företagsnamn (t.ex. 'Tesla', 'Saab', 'Evolution'):")

company_map = {
    "tesla": "TSLA",
    "saab": "SAAB-B.ST",
    "evolution": "EVO.ST",
    "volvo": "VOLV-B.ST",
    "ericsson": "ERIC-B.ST"
}

if user_input:
    ticker = company_map.get(user_input.lower())
    if ticker:
        end_date = datetime.today()
        start_date = end_date - timedelta(days=90)
        df = yf.download(ticker, start=start_date, end=end_date)

        if not df.empty and "Close" in df.columns:
            df["SMA_20"] = df["Close"].rolling(window=20).mean()
            df["SMA_50"] = df["Close"].rolling(window=50).mean()
            df["SMA_200"] = df["Close"].rolling(window=200).mean()

            price_change = df["Close"].pct_change()
            rs = price_change.rolling(14).mean() / price_change.rolling(14).std()
            df["RSI"] = 100 - (100 / (1 + rs))

            sma_cols = ["SMA_20", "SMA_50", "SMA_200"]
            valid_sma_cols = [col for col in sma_cols if col in df.columns and df[col].notna().any()]
            if valid_sma_cols:
                try:
                    df = df.dropna(subset=valid_sma_cols, how="all")
                except KeyError:
                    pass

            # Senaste pris & datum
            try:
                latest_close = float(df["Close"].dropna().iloc[-1])
            except Exception:
                latest_close = None

            try:
                latest_date = df.index[-1].strftime('%Y-%m-%d')
            except Exception:
                latest_date = "Okänt datum"

            if latest_close is not None:
                currency = "SEK" if ".ST" in ticker else "USD"
                st.markdown(f"💰 **Senaste stängningspris:** {latest_close:.2f} {currency}")
            else:
                st.warning("Kunde inte hämta stängningspris.")

            st.markdown(f"📅 **Senaste handelsdag:** {latest_date}")

            # Prisgraf (nuvarande)
            fig = go.Figure()
            fig.add_trace(go.Scatter(x=df.index, y=df["Close"], name="Stängningspris", line=dict(color="black")))

            for col, color in zip(valid_sma_cols, ["blue", "orange", "purple"]):
                fig.add_trace(go.Scatter(x=df.index, y=df[col], name=col, line=dict(dash="dot", color=color)))

            fig.update_layout(title="Pris & Glidande Medelvärden", xaxis_title="Datum", yaxis_title="Pris",
                              height=500, template="plotly_white")
            st.plotly_chart(fig, use_container_width=True)

            # Prognosgraf
            df_forecast = df.tail(60).copy()
            df_forecast = df_forecast.reset_index()
            df_forecast["Days"] = (df_forecast["Date"] - df_forecast["Date"].min()).dt.days
            X = df_forecast[["Days"]]
            y = df_forecast["Close"]

            model = LinearRegression()
            model.fit(X, y)

            future_days = 7
            last_day = df_forecast["Days"].iloc[-1]
            future_X = np.array([last_day + i for i in range(1, future_days + 1)]).reshape(-1, 1)
            future_dates = [df.index[-1] + timedelta(days=i) for i in range(1, future_days + 1)]
            future_prices = model.predict(future_X)

            fig_forecast = go.Figure()
            fig_forecast.add_trace(go.Scatter(x=df.index, y=df["Close"], name="Historik", line=dict(color="gray")))
            fig_forecast.add_trace(go.Scatter(x=future_dates, y=future_prices, name="Prognos", line=dict(color="green", dash="dash")))

            fig_forecast.update_layout(title="📈 Prognos (7 dagar framåt)", xaxis_title="Datum", yaxis_title="Pris",
                                       height=400, template="plotly_white")
            st.plotly_chart(fig_forecast, use_container_width=True)

            # RSI-graf
            if "RSI" in df.columns and df["RSI"].notna().any():
                fig_rsi = go.Figure()
                fig_rsi.add_trace(go.Scatter(x=df.index, y=df["RSI"], name="RSI", line=dict(color="green")))
                fig_rsi.add_hline(y=70, line_dash="dash", line_color="red")
                fig_rsi.add_hline(y=30, line_dash="dash", line_color="blue")
                fig_rsi.update_layout(title="RSI (Relative Strength Index)", xaxis_title="Datum", yaxis_title="RSI",
                                      height=300, template="plotly_white")
                st.plotly_chart(fig_rsi, use_container_width=True)

            # Tabell
            st.subheader("📊 Prisdata")
            st.dataframe(df[["Open", "Close"]].dropna().tail(30))

        else:
            st.error("Ingen data hittades för vald aktie.")
    else:
        st.warning("Företagsnamnet känns inte igen.")