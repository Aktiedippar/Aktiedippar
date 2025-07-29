import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objs as go
from datetime import datetime
import time

# === Inställningar ===
st.set_page_config(page_title="Aktieanalys", layout="wide")
REFRESH_INTERVAL = 30  # sekunder

# === Titel med logga ===
st.markdown(
    """
    <div style="display: flex; align-items: center;">
        <img src="https://raw.githubusercontent.com/Aktiedippar/Aktiedippar/main/logga.png" width="50" style="margin-right: 15px;">
        <h1 style="margin: 0; font-size: 2.2em;">📈 Aktieanalysverktyg</h1>
    </div>
    """,
    unsafe_allow_html=True
)

# === Initiera session state ===
if "saved_input" not in st.session_state:
    st.session_state.saved_input = ""
if "last_refresh" not in st.session_state:
    st.session_state.last_refresh = time.time()

# === Nedräkning och automatisk uppdatering ===
seconds_left = REFRESH_INTERVAL
countdown_placeholder = st.empty()

for remaining in range(seconds_left, 0, -1):
    countdown_placeholder.markdown(f"🔄 Uppdatering om: **{remaining} sekunder**")
    time.sleep(1)

# === Tvinga omstart efter nedräkning ===
st.session_state.last_refresh = time.time()
st.rerun()

# === Sökfält ===
user_input = st.text_input("Sök företagsnamn (t.ex. 'Tesla', 'Saab', 'Evolution'):", value=st.session_state.saved_input)

if user_input:
    st.session_state.saved_input = user_input

# === Namn till ticker ===
company_map = {
    "tesla": "TSLA",
    "saab": "SAAB-B.ST",
    "evolution": "EVO.ST",
    "volvo": "VOLV-B.ST",
    "ericsson": "ERIC-B.ST"
}

# === Hämta aktiedata ===
if st.session_state.saved_input:
    ticker = company_map.get(st.session_state.saved_input.lower())
    if ticker:
        ticker_obj = yf.Ticker(ticker)

        # Aktuellt pris + valuta
        latest_price = ticker_obj.info.get("regularMarketPrice")
        currency = ticker_obj.info.get("currency", "SEK")

        if latest_price is not None:
            st.markdown(f"💰 **Nuvarande pris:** {latest_price:.2f} {currency}")
            st.markdown(f"📅 **Tidpunkt:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

            # Prisgraf: intradagsdata
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
        else:
            st.warning("Kunde inte hämta aktuellt pris.")
    else:
        st.warning("Företagsnamnet känns inte igen.")