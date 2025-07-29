import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objs as go
from datetime import datetime, timedelta
import time
import base64
from PIL import Image

# === KONFIGURATION ===
REFRESH_INTERVAL = 30  # sekunder

st.set_page_config(page_title="Aktieanalys", layout="wide")

# === LOGGA + RUBRIK ===
col1, col2 = st.columns([1, 10])
with col1:
    try:
        image = Image.open("logga.png")
        st.image(image, width=60)
    except:
        st.write("🔍")

with col2:
    st.title("📈 Aktieanalysverktyg")

# === AVANZA-KNAPP ===
avanza_logo = "https://www.avanza.se/_nuxt/img/avanza-logo-green.9f0e3a1.svg"
avanza_button_html = f"""
<a href="https://www.avanza.se" target="_blank">
    <img src="{avanza_logo}" alt="Avanza" width="120" style="margin-bottom: 10px;">
</a>
"""
st.markdown(avanza_button_html, unsafe_allow_html=True)

# === NEDRÄKNANDE TIMER + LJUD ===
def countdown_timer(seconds):
    for remaining in range(seconds, 0, -1):
        minutes, sec = divmod(remaining, 60)
        timer_html = f"""
        <div style='font-size: 26px; font-weight: bold; color: #444; text-align: center; margin-bottom: 15px;'>
            ⏳ Uppdatering om:
            <div style="font-size: 44px; color: #2E8B57;">{minutes:02}:{sec:02}</div>
        </div>
        """
        st.markdown(timer_html, unsafe_allow_html=True)
        time.sleep(1)
        st.empty()
    
    # Spela ljud när tiden är slut
    try:
        with open("ping.mp3", "rb") as f:
            b64_sound = base64.b64encode(f.read()).decode()
            sound_html = f"""
            <audio autoplay>
                <source src="data:audio/mp3;base64,{b64_sound}" type="audio/mp3">
            </audio>
            """
            st.markdown(sound_html, unsafe_allow_html=True)
    except:
        st.warning("Ljudfil (ping.mp3) saknas.")

# === TIMERN KÖRS ===
countdown_timer(REFRESH_INTERVAL)

# === SÖK AKTIE ===
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
        # === LADDA NER DATA ===
        df = yf.download(ticker, period="1d", interval="1m")

        if not df.empty and "Close" in df.columns:
            current_price = float(df["Close"].dropna().iloc[-1])
            current_time = df.index[-1].strftime('%Y-%m-%d %H:%M')

            # === VISA PRIS & TID ===
            currency = "SEK" if ".ST" in ticker else "USD"
            st.markdown(f"💰 **Aktuellt pris:** {current_price:.2f} {currency}")
            st.markdown(f"🕒 **Senast uppdaterad:** {current_time}")

            # === GRAF ===
            fig = go.Figure()
            fig.add_trace(go.Scatter(x=df.index, y=df["Close"], mode='lines+markers', name="Nuvarande pris", line=dict(color="green")))
            fig.update_layout(title="📊 Aktuellt pris", xaxis_title="Tid", yaxis_title=f"Pris ({currency})", height=500, template="plotly_white")
            st.plotly_chart(fig, use_container_width=True)

        else:
            st.error("Ingen data hittades för vald aktie.")
    else:
        st.warning("Företagsnamnet känns inte igen.")

# === UPPDATERA AUTOMATISKT EFTER TIMERN ===
st.rerun()