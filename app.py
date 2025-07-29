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

        if not df.empty:
            df["SMA_20"] = df["Close"].rolling(window=20).mean()
            df["SMA_50"] = df["Close"].rolling(window=50).mean()
            df["SMA_200"] = df["Close"].rolling(window=200).mean()
            df["RSI"] = 100 - (100 / (1 + df["Close"].pct_change().rolling(window=14).mean() /
                                       df["Close"].pct_change().rolling(window=14).std()))

            sma_cols = ["SMA_20", "SMA_50", "SMA_200"]
            valid_sma_cols = []
            for col in sma_cols:
                if col in df.columns:
                    try:
                        if df[col].notna().any():
                            valid_sma_cols.append(col)
                    except KeyError:
                        pass

            if valid_sma_cols:
                try:
                    df = df.dropna(subset=valid_sma_cols, how="all")
                except KeyError:
                    pass

            st.markdown(f"💰 **Senaste stängningspris:** {df['Close'][-1]:.2f} SEK")
            st.markdown(f"📅 **Senaste handelsdag:** {df.index[-1].strftime('%Y-%m-%d')}")

            fig = go.Figure()
            fig.add_trace(go.Scatter(x=df.index, y=df["Close"], mode="lines", name="Stängningspris"))

            if "SMA_20" in df.columns and df["SMA_20"].notna().any():
                fig.add_trace(go.Scatter(x=df.index, y=df["SMA_20"], mode="lines", name="SMA 20"))
            if "SMA_50" in df.columns and df["SMA_50"].notna().any():
                fig.add_trace(go.Scatter(x=df.index, y=df["SMA_50"], mode="lines", name="SMA 50"))
            if "SMA_200" in df.columns and df["SMA_200"].notna().any():
                fig.add_trace(go.Scatter(x=df.index, y=df["SMA_200"], mode="lines", name="SMA 200"))

            fig.update_layout(title="Pris & Glidande Medelvärden", xaxis_title="Datum", yaxis_title="Pris",
                              height=500, template="plotly_white")
            st.plotly_chart(fig, use_container_width=True)

            fig_rsi = go.Figure()
            fig_rsi.add_trace(go.Scatter(x=df.index, y=df["RSI"], mode="lines", name="RSI"))
            fig_rsi.add_hline(y=70, line_dash="dash", line_color="red")
            fig_rsi.add_hline(y=30, line_dash="dash", line_color="green")
            fig_rsi.update_layout(title="RSI (Relative Strength Index)", xaxis_title="Datum", yaxis_title="RSI",
                                  height=300, template="plotly_white")
            st.plotly_chart(fig_rsi, use_container_width=True)

            st.subheader("📊 Prisdata")
            st.dataframe(df[["Open", "Close"]].tail(30))
        else:
            st.error("Ingen data hittades för vald aktie.")
    else:
        st.warning("Företaget känns inte igen.")