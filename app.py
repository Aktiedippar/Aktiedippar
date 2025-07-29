import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objs as go
from datetime import datetime
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

# Initiera refresh-timer
if "last_refresh" not in st.session_state:
    st.session_state.last_refresh = time.time()

# Om mer än 30 sekunder gått → kör om appen
if time.time() - st.session_state.last_refresh > 30:
    st.session_state.last_refresh = time.time()
    st.experimental_rerun()

# Initiera sökfältsdata
if "saved_input" not in st.session_state:
    st.session_state.saved_input = ""

# Sökfält
user_input = st.text_input("Sök företagsnamn (t.ex. 'Tesla', 'Saab', 'Evolution'):", value=st.session_state.saved_input)

# Spara senaste inmatningen
if user_input:
    st.session_state.saved_input = user_input

# Mappning av namn till ticker
company_map = {
    "tesla": "TSLA",
    "saab": "SAAB-B.ST",
    "evolution": "EVO.ST",
    "volvo": "VOLV-B.ST",
    "ericsson": "ERIC-B.ST"
}

# Hämta data om sökning finns
if st.session_state.saved_input:
    ticker = company_map.get(st.session_state.saved_input.lower())
    if ticker:
        ticker_obj = yf.Ticker(ticker)

        # Hämta nuvarande pris och valuta
        latest_price = ticker_obj.info.get("regularMarketPrice")
        currency = ticker_obj.info.get("currency", "SEK")

        if latest_price is not None:
            st.markdown(f"💰 **Nuvarande pris:** {latest_price:.2f} {currency}")
            st.markdown(f"📅 **Tidpunkt:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

            # Hämta intradagsdata
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