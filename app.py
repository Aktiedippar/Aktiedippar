import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objs as go
from datetime import datetime, timedelta
import numpy as np
import time

# Streamlit-sidinställningar
st.set_page_config(page_title="Aktieanalys", layout="wide")

# Logga + rubrik i rad
st.markdown(
    """
    <div style="display: flex; align-items: center;">
        <img src="https://raw.githubusercontent.com/Aktiedippar/Aktiedippar/main/logga.png" width="50" style="margin-right: 15px;">
        <h1 style="margin: 0; font-size: 2.2em;">📈 Aktieanalysverktyg</h1>
    </div>
    """,
    unsafe_allow_html=True
)

# Refresh-timer
if "last_refresh" not in st.session_state:
    st.session_state.last_refresh = time.time()

if time.time() - st.session_state.last_refresh > 30:
    st.session_state.last_refresh = time.time()
    st.rerun()

# Input-sökning
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
                # Första grafen – senaste pris
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
                    template="plotly_white"
                )

                st.plotly_chart(fig, use_container_width=True)

                # Andra grafen – framtidsprognos
                st.markdown("🔮 **Framtidsprognos baserat på trenden**")

                # En enkel linjär regressionsmodell
                recent_data = hist["Close"].dropna().tail(36)
                if len(recent_data) >= 10:
                    y = recent_data.values
                    x = np.arange(len(y))
                    coeffs = np.polyfit(x, y, 1)
                    future_x = np.arange(len(y), len(y) + 7)
                    future_y = np.polyval(coeffs, future_x)

                    future_times = [hist.index[-1] + timedelta(minutes=5 * (i + 1)) for i in range(7)]

                    fig_forecast = go.Figure()
                    fig_forecast.add_trace(go.Scatter(
                        x=future_times,
                        y=future_y,
                        name="Prognos",
                        line=dict(color="blue", dash="dash")
                    ))

                    fig_forecast.update_layout(
                        title="🔮 Prognos – Nästa 30–40 minuter",
                        xaxis_title="Tidpunkt",
                        yaxis_title=f"Pris ({currency})",
                        height=350,
                        template="plotly_white"
                    )

                    st.plotly_chart(fig_forecast, use_container_width=True)
                else:
                    st.info("Inte tillräckligt med data för att göra en prognos.")
            else:
                st.warning("Ingen intradagsdata hittades för denna aktie.")
        else:
            st.warning("Kunde inte hämta aktuellt pris.")
    else:
        st.warning("Företagsnamnet känns inte igen.")