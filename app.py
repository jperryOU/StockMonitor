import streamlit as st
import yfinance as yf
import pandas_ta as ta
import pandas as pd

st.set_page_config(page_title="Tactical Screener", layout="wide")
st.title("Tactical Stock Screener")

# Sidebar inputs
tickers_input = st.sidebar.text_input("Watchlist", "CRDO, AAPL, NVDA, MRVL, AVGO")
ticker_list = [t.strip().upper() for t in tickers_input.split(",") if t.strip()]

st.write("### Active Technical Setups")

results = []
for ticker in ticker_list:
    try:
        df = yf.download(ticker, period="3mo", interval="1d", progress=False)
        if len(df) >= 21:
            # Ensure series are 1D
            close = df["Close"].squeeze()
            df["EMA_9"] = ta.ema(close, length=9)
            df["EMA_21"] = ta.ema(close, length=21)
            df["RSI"] = ta.rsi(close, length=14)

            last_price = float(close.iloc[-1])
            last_rsi = float(df["RSI"].iloc[-1])
            ema9 = float(df["EMA_9"].iloc[-1])
            ema21 = float(df["EMA_21"].iloc[-1])

            bullish = last_price > ema9 > ema21

            results.append({
                "Ticker": ticker,
                "Price": f"${last_price:.2f}",
                "RSI (14)": round(last_rsi, 1),
                "Trend (P > 9 > 21)": "✅ Bullish" if bullish else "⚠️ Neutral/Down"
            })
    except Exception as e:
        st.warning(f"Could not load data for {ticker}")

if results:
    st.dataframe(pd.DataFrame(results), use_container_width=True)
else:
    st.info("No data available.")
