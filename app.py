import streamlit as st
import yfinance as yf
import pandas as pd

st.set_page_config(page_title="Tactical Screener", layout="wide")
st.title("Tactical Stock Screener")

# Sidebar inputs
tickers_input = st.sidebar.text_input("Watchlist", "CRDO, AAPL, NVDA, MRVL, AVGO")
ticker_list = [t.strip().upper() for t in tickers_input.split(",") if t.strip()]

st.write("### Active Technical Setups")

def calculate_rsi(series, period=14):
    delta = series.diff()
    gain = delta.where(delta > 0, 0.0)
    loss = -delta.where(delta < 0, 0.0)
    avg_gain = gain.ewm(alpha=1/period, min_periods=period, adjust=False).mean()
    avg_loss = loss.ewm(alpha=1/period, min_periods=period, adjust=False).mean()
    rs = avg_gain / avg_loss
    return 100 - (100 / (1 + rs))

results = []
for ticker in ticker_list:
    try:
        df = yf.download(ticker, period="3mo", interval="1d", progress=False)
        if len(df) >= 21:
            close = df["Close"].squeeze()
            
            # Native Pandas Calculations (Zero external TA dependencies)
            ema_9 = close.ewm(span=9, adjust=False).mean()
            ema_21 = close.ewm(span=21, adjust=False).mean()
            rsi_14 = calculate_rsi(close, period=14)

            last_price = float(close.iloc[-1])
            last_rsi = float(rsi_14.iloc[-1])
            last_ema9 = float(ema_9.iloc[-1])
            last_ema21 = float(ema_21.iloc[-1])

            bullish = last_price > last_ema9 > last_ema21

            results.append({
                "Ticker": ticker,
                "Price": f"${last_price:.2f}",
                "RSI (14)": round(last_rsi, 1),
                "9 EMA": f"${last_ema9:.2f}",
                "21 EMA": f"${last_ema21:.2f}",
                "Trend (P > 9 > 21)": "✅ Bullish" if bullish else "⚠️ Neutral/Down"
            })
    except Exception as e:
        st.warning(f"Could not load data for {ticker}")

if results:
    st.dataframe(pd.DataFrame(results), use_container_width=True)
else:
    st.info("No data available.")
