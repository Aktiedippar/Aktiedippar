import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objs as go
from datetime import datetime
from streamlit_autorefresh import st_autorefresh

REFRESH_INTERVAL = 30  # sekunder
st.set_page_config(page_title="Aktieanalys", layout="wide")

# Titel med logga
st.markdown(
    """
    <div style="display: flex; align-items: center;">
        <img src="https://raw.githubusercontent.com/Aktiedippar/Aktiedippar/main/logga.png" width="50" style="margin-right:15px;">
        <h1 style="margin:0; font-size:2.2em;">📈 Aktieanalysverktyg</h1>
    </div>
    """, unsafe_allow_html=True
)

# Autorefresh var 30:e sekund
count = st_autorefresh(interval=REFRESH_INTERVAL * 1000, key="auto_refresh")

# Nedräkning: JavaScript-timer + ljud vid 00:00
st.markdown("""
<div id="countdown" style="font-size:1.5em; font-weight:bold; padding:10px;"></div>
<audio id="alertSound" src="https://actions.google.com/sounds/v1/alarms/beep_short.ogg" preload="auto"></audio>
<script>
let seconds = %d;
function tick(){
    let mins = Math.floor(seconds/60);
    let secs = seconds%%60;
    document.getElementById("countdown").innerText = "🔄 Nästa uppdatering om: "+String(mins).padStart(2,'0')+":"+String(secs).padStart(2,'0');
    if(seconds === 0){
        document.getElementById("alertSound").play();
        seconds = %d;
    } else {
        seconds--;
    }
}
setInterval(tick, 1000);
tick();
</script>
""" % (REFRESH_INTERVAL, REFRESH_INTERVAL), unsafe_allow_html=True)

# Session state för sökning
if "saved_input" not in st.session_state:
    st.session_state.saved_input = ""
user_input = st.text_input("Sök företagsnamn (t.ex. 'Tesla', 'Saab', 'Evolution'):",
                           value=st.session_state.saved_input)
if user_input:
    st.session_state.saved_input = user_input

# Namn → ticker
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
            st.markdown(f"📅 **Tidpunkt:** {datetime.now().strftime('%Y‑%m‑%d %H:%M:%S')}")
            hist = ticker_obj.history(period="1d", interval="5m")
            if not hist.empty:
                fig = go.Figure()
                fig.add_trace(go.Scatter(
                    x=hist.index,
                    y=hist["Close"],
                    name="Pris", line=dict(color="green", width=2)))
                fig.update_layout(
                    title="📈 Prisgraf – senaste handelsdagen",
                    xaxis_title="Tidpunkt", yaxis_title=f"Pris ({currency})",
                    height=400, template="plotly_white", margin=dict(l=40,r=40,t=40,b=40))
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.warning("Ingen intradagsdata hittades.")
        else:
            st.warning("Kunde inte hämta aktuellt pris.")
    else:
        st.warning("Företagsnamnet känns inte igen.")