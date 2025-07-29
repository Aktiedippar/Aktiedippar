import streamlit as st
import pandas as pd
import yfinance as yf
import altair as alt
from datetime import datetime, timedelta

# Appkonfiguration
st.set_page_config(page_title="Aktiegraf", layout="wide")

# Titel och sökfält
st.markdown("<h2 style='color:#012D5A;'>📈 Aktieanalys</h2>", unsafe_allow_html=True)
ticker_input = st.text_input("🔍 Sök efter företag (t.ex. 'Tesla', 'Saab')", "")
st.caption("Exempel: Tesla, Saab, Evolution, Volvo, Ericsson")

# Kontroll: tomt input
if ticker_input.strip() == "":
    st.info("Skriv ett företagsnamn för att börja.")
    st.stop()

# Omvandla användarens input till rätt ticker
ticker_map = {
    "tesla": "TSLA",
    "saab": "SAAB-B.ST",
    "evolution": "EVO.ST",
    "volvo": "VOLCAR-B.ST",
    "ericsson": "ERIC-B.ST",
    "apple": "AAPL",
    "microsoft": "MSFT",
    "google": "GOOGL"
}
ticker = ticker_map.get(ticker_input.lower(), ticker_input.upper())

# Ladda aktiedata
@st.cache_data(ttl=3600)
def load_data(ticker):
    end = datetime.today()
    start = end - timedelta(days=90)
    try:
        df = yf.download(ticker, start=start, end=end)
        df = df[["Open", "Close", "Volume"]]
        df.dropna(inplace=True)
        df.index = pd.to_datetime(df.index)
        return df
    except Exception:
        return pd.DataFrame()

df = load_data(ticker)

if df.empty:
    st.warning(f"Ingen data hittades för '{ticker_input}' ({ticker}). Kontrollera att företagsnamnet är korrekt.")
    st.stop()

# Debug: visa shape och de sista Close-värdena
st.write("📦 Debug – DataFrame shape:", df.shape)
st.write("📉 Debug – Sista Close-värden:", df["Close"].tail())

# Kontroll: finns Close-data?
if "Close" not in df.columns or df["Close"].dropna().empty:
    st.warning("Ingen stängningsdata tillgänglig för vald aktie.")
    st.stop()

# Felsäker hantering av senaste stängningspris
try:
    latest_close = df["Close"].dropna().iloc[-1]
    st.write(f"💰 Senaste stängningspris: **{latest_close:.2f} SEK**")
except Exception as e:
    st.warning(f"Kunde inte hämta stängningspris. Fel: {e}")
    st.stop()

# Glidande medelvärden
df["SMA 20"] = df["Close"].rolling(window=20).mean()
df["SMA 50"] = df["Close"].rolling(window=50).mean()

# Rensa bort rader där båda SMA är NaN (för att undvika grafbugg)
df = df.dropna(subset=["SMA 20", "SMA 50"], how="all")

# Hämta min/max för Y-axel (för proportionell graf)
min_price = float(df["Close"].min())
max_price = float(df["Close"].max())

# Altair-graf
base = alt.Chart(df.reset_index()).encode(
    x=alt.X("Date:T", title="Datum"),
    y=alt.Y("Close:Q", title="Stängningspris (SEK)",
            scale=alt.Scale(domain=[min_price * 0.95, max_price * 1.05]))
)

close_line = base.mark_line(color="#1f77b4", strokeWidth=2).encode(
    tooltip=["Date:T", "Close:Q"]
)

sma20_line = base.mark_line(color="orange", strokeDash=[4, 2]).encode(
    y="SMA 20:Q",
    tooltip=["Date:T", "SMA 20:Q"]
)

sma50_line = base.mark_line(color="green", strokeDash=[2, 2]).encode(
    y="SMA 50:Q",
    tooltip=["Date:T", "SMA 50:Q"]
)

chart = (close_line + sma20_line + sma50_line).properties(
    width=1000,
    height=400
).configure_axis(
    grid=False
).configure_view(
    strokeWidth=0
)

st.altair_chart(chart, use_container_width=True)

# Visa data som tabell
st.subheader("📊 Data de senaste 3 månaderna")
st.dataframe(df[["Open", "Close", "Volume"]].sort_index(ascending=False).round(2))
