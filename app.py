import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objs as go
from datetime import datetime, timedelta

st.set_page_config(page_title="Aktieanalys", layout="wide")
st.title("📈 Aktieanalysverktyg")

# 1. Sökfält
user_input = st.text_input("Sök företagsnamn (t.ex. 'Tesla', 'Saab', 'Evolution'):")

# 2. Namn till ticker-omvandling
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
        # 3. Hämta data
        end_date = datetime.today()
        start_date = end_date - timedelta(days=90)
        df = yf.download(ticker, start=start_date, end=end_date)

        if df.empty:
            st.error("Ingen data hittades för vald aktie.")
        else:
            df["SMA_20"] = df["Close"].rolling(window=20).mean()
            df["SMA_50"] = df["Close"].rolling(window=50).mean()
            df["SMA_200"] = df["Close"].rolling(window=200).mean()
            df["RSI"] = 100 - (100 / (1 + df["Close"].pct_change().rolling(window=14).mean() /
                                       df["Close"].pct_change().rolling(window=14).std()))

            # 4. Ta bort tomma rader för de existerande SMA-kolumnerna
            sma_cols = ["SMA_20", "SMA_50", "SMA_200"]
            existing_sma_cols = [col for col in sma_cols if col in df.columns]
            if existing_sma_cols:
                df = df.dropna(subset=existing_sma_cols, how="all")

            # 5. Visa senaste prisinfo
            st.markdown(f"💰 **Senaste stängningspris:** {df['Close'][-1]:.2f} SEK")
            st.markdown(f"📅 **Senaste handelsdag:** {df.index[-1].strftime('%Y-%m-%d')}")

            # 6. Prisgraf
            fig = go.Figure()
            fig.add_trace(go.Scatter(x=df.index, y=df["Close"], mode="lines", name="Stängningspris"))

            if "SMA_20" in df.columns:
                fig.add_trace(go.Scatter(x=df.index, y=df["SMA_20"], mode="lines", name="SMA 20"))
            if "SMA_50" in df.columns:
                fig.add_trace(go.Scatter(x=df.index, y=df["SMA_50"], mode="lines", name="SMA 50"))
            if "SMA_200" in df.columns:
                fig.add_trace(go.Scatter(x=df.index, y=df["SMA_200"], mode="lines", name="SMA 200"))

            fig.update_layout(title="Aktiepris med glidande medelvärden", xaxis_title="Datum", yaxis_title="Pris",
                              height=500, template="plotly_white")
            st.plotly_chart(fig, use_container_width=True)

            # 7. RSI-graf
            fig_rsi = go.Figure()
            fig_rsi.add_trace(go.Scatter(x=df.index, y=df["RSI"], mode="lines", name="RSI"))
            fig_rsi.add_hline(y=70, line_dash="dash", line_color="red")
            fig_rsi.add_hline(y=30, line_dash="dash", line_color="green")
            fig_rsi.update_layout(title="RSI (Relative Strength Index)", xaxis_title="Datum", yaxis_title="RSI",
                                  height=300, template="plotly_white")
            st.plotly_chart(fig_rsi, use_container_width=True)

            # 8. Visa tabell
            st.subheader("📊 Data de senaste 3 månaderna")
            st.dataframe(df[["Open", "Close"]].tail(30))
    else:
        st.warning("Företagsnamnet känns inte igen. Försök med t.ex. 'Tesla', 'Saab', 'Evolution', 'Volvo', 'Ericsson'.")