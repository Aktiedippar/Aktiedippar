import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objs as go
from datetime import datetime

st.set_page_config(page_title="Aktieanalys", layout="wide")
st.title("📈 Aktieanalysverktyg")

# Inmatning
user_input = st.text_input("Sök företagsnamn (t.ex. 'Tesla', 'Saab', 'Evolution'):")

# Namn till ticker
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
        ticker_obj = yf.Ticker(ticker)
        latest_price = ticker_obj.info.get("regularMarketPrice")
        currency = ticker_obj.info.get("currency", "SEK")  # fallback

        if latest_price is not None:
            # Visa pris i stor text + tidpunkt
            st.markdown(f"💰 **Nuvarande pris:** {latest_price:.2f} {currency}")
            st.markdown(f"📅 **Tidpunkt:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

            # Temporär DataFrame för graf
            live_df = pd.DataFrame({
                "Tid": [datetime.now()],
                "Pris": [latest_price]
            })

            # Rita graf
            fig = go.Figure()
            fig.add_trace(go.Scatter(
                x=live_df["Tid"],
                y=live_df["Pris"],
                name="Nuvarande pris",
                line=dict(color="green", width=3)
            ))

            fig.update_layout(
                title="📈 Nuvarande prisgraf",
                xaxis_title="Tidpunkt",
                yaxis_title=f"Pris ({currency})",
                height=400,
                template="plotly_white",
                margin=dict(l=40, r=40, t=40, b=40)
            )

            st.plotly_chart(fig, use_container_width=True)
        else:
            st.warning("Kunde inte hämta aktuellt pris just nu.")
    else:
        st.warning("Företagsnamnet känns inte igen.")