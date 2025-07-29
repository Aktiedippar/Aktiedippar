import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objs as go
from datetime import datetime, timedelta
import time
import numpy as np

st.set_page_config(page_title="Aktieanalys", layout="wide")

st.markdown(
    """
    <div style="display: flex; align-items: center;">
        <img src="https://raw.githubusercontent.com/Aktiedippar/Aktiedippar/main/logga.png" width="50" style="margin-right: 15px;">
        <h1 style="margin: 0; font-size: 2.2em;">📈 Aktieanalysverktyg</h1>
    </div>
    """,
    unsafe_allow_html=True
)

if "last_refresh" not in st.session_state:
    st.session_state.last_refresh = time.time()

if time.time() - st.session_state.last_refresh > 30:
    st.session_state.last_refresh = time.time()
    st.rerun()

if "saved_input" not in st.session_state:
    st.session_state.saved_input = ""

user_input = st.text_input("Sök företagsnamn (t.ex. 'Tesla', 'Saab', 'Evolution'):", value=st.session_state.saved_input)

if user_input:
    st.session_state.saved_input = user_input

company_map = {
    "tesla": "TSLA",
    "saab": "SAAB-B.ST",
    "evolution": "EVO.ST",
    "volvo": "VOLV-B.ST",
    "ericsson": "ERIC-B.ST"
}

if st.session_state.saved_input:
    ticker = company_map.get(st.session_state.saved_input.lower())
    if ticker:
        ticker_obj = yf.Ticker(ticker)
        latest_price = ticker_obj.info.get("regularMarketPrice")
        currency = ticker_obj.info.get("currency", "SEK")

        if latest_price is not None:
            st.markdown(f"💰 **Nuvarande pris:** {latest_price:.2f} {currency}")
            st.markdown(f"📅 **Tidpunkt:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

            hist = ticker_obj.history(period="1d", interval="5m")

            if not hist.empty:
                fig = go.Figure()
                fig.add_trace(go.Scatter(
                    x=hist.index,
                    y=hist["Close"],
                    name="Pris",
                    line=dict(color="green", width=2)
                ))
                fig.update_layout(
                    title="📈 Prisgraf – senaste handelsdagen",
                    xaxis_title="Tidpunkt",
                    yaxis_title=f"Pris ({currency})",
                    height=400,
                    template="plotly_white",
                    margin=dict(l=40, r=40, t=40, b=40)
                )
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.warning("Ingen intradagsdata hittades för denna aktie.")

            # ----- Framtidsprognosgraf (2 veckor) -----
            forecast_hist = ticker_obj.history(period="6mo", interval="1d")

            if not forecast_hist.empty:
                forecast_hist = forecast_hist.dropna(subset=["Close"])
                forecast_hist.reset_index(inplace=True)
                forecast_hist["Days"] = (forecast_hist["Date"] - forecast_hist["Date"].min()).dt.days

                X = forecast_hist["Days"].values.reshape(-1, 1)
                y = forecast_hist["Close"].values
                coef = np.polyfit(forecast_hist["Days"], y, 1)
                poly1d_fn = np.poly1d(coef)

                future_days = np.arange(forecast_hist["Days"].max() + 1, forecast_hist["Days"].max() + 15)
                future_dates = [forecast_hist["Date"].max() + timedelta(days=int(i)) for i in range(1, 15)]
                forecast_values = poly1d_fn(future_days)

                forecast_fig = go.Figure()
                forecast_fig.add_trace(go.Scatter(
                    x=forecast_hist["Date"],
                    y=forecast_hist["Close"],
                    mode="lines",
                    name="Historiskt pris",
                    line=dict(color="gray")
                ))
                forecast_fig.add_trace(go.Scatter(
                    x=future_dates,
                    y=forecast_values,
                    mode="lines+markers",
                    name="Prognos (2 veckor)",
                    line=dict(color="blue", dash="dash")
                ))

                forecast_fig.update_layout(
                    title="🔮 Framtidsprognos – kommande 2 veckor",
                    xaxis_title="Datum",
                    yaxis_title=f"Pris ({currency})",
                    height=400,
                    template="plotly_white"
                )
                st.plotly_chart(forecast_fig, use_container_width=True)
        else:
            st.warning("Kunde inte hämta aktuellt pris.")
    else:
        st.warning("Företagsnamnet känns inte igen.")