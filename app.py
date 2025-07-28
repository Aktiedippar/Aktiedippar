import streamlit as st
import yfinance as yf

st.set_page_config(page_title="Aktieanalys", layout="centered")

st.title("📈 Aktieanalys App")

ticker = st.text_input("Skriv in en akties ticker (t.ex. AAPL, EVO.ST)", "EVO.ST")

if ticker:
    stock = yf.Ticker(ticker)
    data = stock.history(period="6mo")

    st.subheader(f"Senaste 6 månaders pris för {ticker}")
    st.line_chart(data['Close'])

    st.subheader("Nyckeltal")
    info = stock.info
    st.write(f"**Företagsnamn:** {info.get('longName')}")
    st.write(f"**Marknadsvärde:** {info.get('marketCap')}")
    st.write(f"**PE-tal (TTM):** {info.get('trailingPE')}")
    st.write(f"**Utdelning (%):** {info.get('dividendYield')}")

