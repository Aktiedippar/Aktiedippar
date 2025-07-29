import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objs as go
from datetime import datetime, timedelta

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
            # Beräkna indikatorer
            df["SMA_20"] = df["Close"].rolling(window=20).mean()
            df["SMA_50"] = df["Close"].rolling(window=50).mean()
            df["SMA_200"] = df["Close"].rolling(window=200).mean()

            price_change = df["Close"].pct_change()
            rs = price_change.rolling(14).mean() / price_change.rolling(14).std()
            df["RSI"] = 100 - (100 / (1 + rs))

            # Kontrollera SMA-kolumner
            sma_cols = ["SMA_20", "SMA_50", "SMA_200"]
            valid_sma_cols = [col for col in sma_cols if col in df.columns and df[col].notna().any()]
            if valid_sma_cols:
                try:
                    df = df.dropna(subset=valid_sma_cols, how="all")
                except KeyError:
                    pass

            # Säkert hämtad senaste stängningspris och datum
            try:
                latest_close = float(df["Close"].dropna().iloc[-1])
            except Exception:
                latest_close = None

            try:
                latest_date = df.index[-1].strftime('%Y-%m-%d')
            except Exception:
                latest_date = "Okänt datum"

            # Visa pris och datum
            if latest_close is not None:
                st.markdown(f"💰 **Senaste stängningspris:** {latest_close:.2f} SEK")
            else:
                st.warning("Kunde inte hämta stängningspris.")

            st.markdown(f"📅 **Senaste handelsdag:** {latest_date}")

            # Prisgraf med SMA
            fig = go.Figure()
            fig.add_trace(go.Scatter(x=df.index, y=df["Close"], name="Stängningspris", line=dict(color="black")))

            for col, color in zip(valid_sma_cols, ["blue", "orange", "purple"]):
                fig.add_trace(go.Scatter(x=df.index, y=df[col], name=col, line=dict(dash="dot", color=color)))

            fig.update_layout(title="Pris & Glidande Medelvärden", xaxis_title="Datum", yaxis_title="Pris",
                              height=500, template="plotly_white")
            st.plotly_chart(fig, use_container_width=True)

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