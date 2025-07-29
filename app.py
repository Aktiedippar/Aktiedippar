import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objs as go
from datetime import datetime, timedelta
import time
import base64

# ====== KONFIGURATION ======
REFRESH_INTERVAL = 30
st.set_page_config(page_title="Aktieanalys", layout="wide")

# ====== LJUDFUNKTION ======
def play_sound(filename):
    try:
        with open(filename, "rb") as f:
            data = f.read()
            b64 = base64.b64encode(data).decode()
            return f'<audio autoplay><source src="data:audio/mp3;base64,{b64}" type="audio/mp3"></audio>'
    except FileNotFoundError:
        return ""

# ====== TIMER ======
def countdown_timer(seconds):
    placeholder = st.empty()
    for remaining in range(seconds, 0, -1):
        minutes, sec = divmod(remaining, 60)
        placeholder.markdown(f"""
        <div style='font-size:28px; text-align:center;'>
            ⏳ Uppdatering om<br>
            <span style='font-size:48px; color:#2E8B57;'>{minutes:02}:{sec:02}</span>
        </div>
        """, unsafe_allow_html=True)
        time.sleep(1)
    st.markdown(play_sound("ping.mp3"), unsafe_allow_html=True)

# ====== RUBRIK MED LOGGA ======
st.markdown("""
<div style="display:flex;align-items:center;">
 <img src="https://raw.githubusercontent.com/Aktiedippar/Aktiedippar/main/logga.png" width="50" style="margin-right:15px;">
 <h1 style="margin:0;font-size:2.2em;">📈 Aktieanalysverktyg</h1>
</div>
""", unsafe_allow_html=True)

# ====== AVANZA-KNAPP ======
st.markdown("""
<a href="https://www.avanza.se" target="_blank">
    <img src="https://www.avanza.se/_next/static/media/avanza-logo.42e48852.svg" width="140">
</a>
""", unsafe_allow_html=True)

# ====== SÖKFÄLT ======
user_input = st.text_input("Sök företagsnamn (t.ex. 'Tesla', 'Saab', 'Evolution'):")

company_map = {
    "tesla": "TSLA",
    "saab": "SAAB-B.ST",
    "evolution": "EVO.ST",
    "volvo": "VOLV-B.ST",
    "ericsson": "ERIC-B.ST"
}

# ====== HÄMTA DATA ======
if user_input:
    ticker = company_map.get(user_input.lower())
    if ticker:
        end_date = datetime.now()
        start_date = end_date - timedelta(days=1)
        df = yf.download(ticker, start=start_date, end=end_date, interval="1m")

        if not df.empty and "Close" in df.columns:
            try:
                latest_price = float(df["Close"].dropna().iloc[-1])
                latest_time = df.index[-1].strftime('%Y-%m-%d %H:%M')
            except:
                latest_price, latest_time = None, "Okänt"

            currency = "USD" if not ticker.endswith(".ST") else "SEK"
            st.markdown(f"💰 **Nuvarande pris:** {latest_price:.2f} {currency}")
            st.markdown(f"🕒 **Senast uppdaterad:** {latest_time}")

            # ====== PRISGRAF ======
            fig = go.Figure()
            fig.add_trace(go.Scatter(x=df.index, y=df["Close"], mode="lines", name="Pris", line=dict(color="green")))
            fig.update_layout(title="Live-pris", xaxis_title="Tid", yaxis_title=f"Pris ({currency})",
                              height=400, template="plotly_white")
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.error("Kunde inte hämta prisdata.")
    else:
        st.warning("Företagsnamnet känns inte igen.")

# ====== TIMER + RERUN ======
countdown_timer(REFRESH_INTERVAL)
st.experimental_rerun()