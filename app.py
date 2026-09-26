import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np

st.set_page_config(
    page_title="Sector & Commodity Intelligence",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ---------------------------------------------------------
# CACHED DATA FETCHER
# ---------------------------------------------------------
@st.cache_data(ttl=300)  # Caches data for 5 minutes
def fetch_ticker_data(tickers):
    data_dict = {}
    for t in tickers:
        try:
            ticker = t.strip().upper()
            stock = yf.Ticker(ticker)
            df = stock.history(period="3mo")
            if df.empty or len(df) < 21:
                continue
            
            close = df["Close"].dropna()
            high = df["High"].dropna()
            low = df["Low"].dropna()
            volume = df["Volume"].dropna()

            # Technical indicators
            ema_9 = close.ewm(span=9, adjust=False).mean()
            ema_21 = close.ewm(span=21, adjust=False).mean()
            
            # 30-Day Return
            hist_30 = close.iloc[-22:] if len(close) >= 22 else close
            gain_30 = ((close.iloc[-1] - hist_30.iloc[0]) / hist_30.iloc[0]) * 100

            # Day & 52-Wk Range
            info = stock.info or {}
            market_cap = info.get("marketCap", None)
            pe_ratio = info.get("trailingPE", None)
            long_name = info.get("shortName", ticker)

            # Sparkline sequence (normalized 30-day close history)
            spark_series = hist_30.tolist()

            data_dict[ticker] = {
                "name": long_name,
                "price": float(close.iloc[-1]),
                "change_dlr": float(close.iloc[-1] - close.iloc[-2]),
                "change_pct": float((close.iloc[-1] - close.iloc[-2]) / close.iloc[-2] * 100),
                "gain_30": float(gain_30),
                "ema_9": float(ema_9.iloc[-1]),
                "ema_21": float(ema_21.iloc[-1]),
                "day_low": float(low.iloc[-1]),
                "day_high": float(high.iloc[-1]),
                "vol": int(volume.iloc[-1]),
                "low_52": float(close.min()),
                "high_52": float(close.max()),
                "market_cap": market_cap,
                "pe_ratio": pe_ratio,
                "sparkline": spark_series,
                "bullish": bool(ema_9.iloc[-1] > ema_21.iloc[-1])
            }
        except Exception:
            continue
    return data_dict

# ---------------------------------------------------------
# 1. TOP MACRO & SECTOR BENCHMARK RIBBON
# ---------------------------------------------------------
st.markdown("### 🌐 Real-Time Sector Intelligence & Macro Benchmarks")

benchmarks = [
    "SPY", "QQQ", "DIA", "XLK", "XLV", "XLF", 
    "XLY", "XLC", "XLI", "XLP", "XLE", "XLU", "XLRE", "XLB"
]

bench_data = fetch_ticker_data(benchmarks)

# Display in a clean responsive grid
cols = st.columns(len(benchmarks))
for i, ticker in enumerate(benchmarks):
    with cols[i]:
        if ticker in bench_data:
            d = bench_data[ticker]
            st.metric(
                label=ticker,
                value=f"${d['price']:.2f}",
                delta=f"{d['change_pct']:+.2f}%"
            )
        else:
            st.metric(label=ticker, value="--", delta="--")

st.markdown("---")

# ---------------------------------------------------------
# TABS FOR NAVIGATION
# ---------------------------------------------------------
tab_sector, tab_commodities = st.tabs(["📊 Active Sector Explorer", "🛢️ Commodity & Derivative Futures"])

# ---------------------------------------------------------
# 2. ACTIVE SECTOR EXPLORER TAB
# ---------------------------------------------------------
SECTOR_DATASETS = {
    "Communication Services": [
        "GOOGL", "META", "NFLX", "VZ", "DIS", "TMUS", "T", "SPOT", 
        "DASH", "CMCSA", "WBD", "LYV", "TTWO", "FOXA", "OMN", "CHTR", "PINS", "MTCH", "SNAP", "EA"
    ],
    "Technology": [
        "AAPL", "NVDA", "MSFT", "AVGO", "ORCL", "CRM", "AMD", "QCOM", "ADBE", "INTC", "TXN", "MU", "CRDO", "MRVL"
    ],
    "Financials": [
        "JPM", "V", "MA", "BAC", "WFC", "MS", "GS", "BLK", "C", "AXP", "SCHW", "PGR"
    ],
    "Energy": [
        "XOM", "CVX", "COP", "SLB", "EOG", "MPC", "PSX", "VLO", "OXY", "KMI", "WMB"
    ]
}

def format_market_cap(val):
    if not val or pd.isna(val):
        return "--"
    if val >= 1e12:
        return f"${val / 1e12:.2f}T"
    if val >= 1e9:
        return f"${val / 1e9:.2f}B"
    return f"${val / 1e6:.2f}M"

with tab_sector:
    selected_sector = st.selectbox("Select Sector", list(SECTOR_DATASETS.keys()), index=0)
    sector_tickers = SECTOR_DATASETS[selected_sector]
    sec_data = fetch_ticker_data(sector_tickers)

    rows = []
    for t in sector_tickers:
        if t in sec_data:
            d = sec_data[t]
            rows.append({
                "Ticker": t,
                "Company Name": d["name"],
                "Price": d["price"],
                "Change ($)": d["change_dlr"],
                "Change (%)": d["change_pct"],
                "30-Day Gain (%)": d["gain_30"],
                "Market Cap": format_market_cap(d["market_cap"]),
                "P/E Ratio": f"{d['pe_ratio']:.2f}" if d["pe_ratio"] else "--",
                "Momentum Cue": "▲ Bullish" if d["bullish"] else "▼ Bearish",
                "30-Day Trend": d["sparkline"],
                "raw_mcap": d["market_cap"] or 0,
                "raw_gain": d["gain_30"]
            })

    if rows:
        df_sec = pd.DataFrame(rows)
        
        col_left, col_right = st.columns(2)
        
        # Table 1: Top Market Cap Giants
        with col_left:
            st.markdown("#### 🏢 Top Market Cap Leaders")
            df_mcap = df_sec.sort_values(by="raw_mcap", ascending=False).drop(columns=["raw_mcap", "raw_gain"])
            st.dataframe(
                df_mcap,
                column_config={
                    "Price": st.column_config.NumberColumn(format="$%.2f"),
                    "Change ($)": st.column_config.NumberColumn(format="$%.2f"),
                    "Change (%)": st.column_config.NumberColumn(format="%+.2f%%"),
                    "30-Day Gain (%)": st.column_config.NumberColumn(format="%+.2f%%"),
                    "30-Day Trend": st.column_config.LineChartColumn("30-Day Trend")
                },
                hide_index=True,
                use_container_width=True
            )
            
        # Table 2: Top Momentum Gainers (30-Day)
        with col_right:
            st.markdown("#### 🚀 Top 30-Day Momentum Leaders")
            df_mom = df_sec.sort_values(by="raw_gain", ascending=False).drop(columns=["raw_mcap", "raw_gain"]).head(10)
            st.dataframe(
                df_mom,
                column_config={
                    "Price": st.column_config.NumberColumn(format="$%.2f"),
                    "Change ($)": st.column_config.NumberColumn(format="$%.2f"),
                    "Change (%)": st.column_config.NumberColumn(format="%+.2f%%"),
                    "30-Day Gain (%)": st.column_config.NumberColumn(format="%+.2f%%"),
                    "30-Day Trend": st.column_config.LineChartColumn("30-Day Trend")
                },
                hide_index=True,
                use_container_width=True
            )

# ---------------------------------------------------------
# 3. COMMODITY & DERIVATIVE FUTURES TAB
# ---------------------------------------------------------
COMMODITIES_REGISTRY = [
    # Crude Oil
    {"group": "Crude Oil", "benchmark": "WTI Light Sweet Crude", "ticker": "USO", "name": "United States Oil Fund LP", "leverage": "1x Spot / Front-Month", "expense": "0.60%"},
    {"group": "Crude Oil", "benchmark": "Bloomberg WTI Crude Subindex", "ticker": "UCO", "name": "ProShares Ultra Bloomberg Crude", "leverage": "2x Daily Leveraged Long", "expense": "0.95%"},
    {"group": "Crude Oil", "benchmark": "Bloomberg WTI Crude Subindex", "ticker": "SCO", "name": "ProShares UltraShort Bloomberg Crude", "leverage": "-2x Leveraged Inverse", "expense": "0.95%"},
    {"group": "Crude Oil", "benchmark": "WTI Crude Futures (12-Month)", "ticker": "USL", "name": "United States 12 Month Oil Fund", "leverage": "1x 12-Month Strip Curve", "expense": "0.90%"},
    {"group": "Crude Oil", "benchmark": "ICE Brent Crude Futures", "ticker": "BNO", "name": "United States Brent Oil Fund LP", "leverage": "1x Front-Month Brent", "expense": "1.02%"},
    # Refined Products
    {"group": "Refined Products", "benchmark": "NYMEX RBOB Gasoline", "ticker": "UGA", "name": "United States Gasoline Fund LP", "leverage": "1x Front-Month RBOB Gas", "expense": "0.97%"},
    {"group": "Refined Products", "benchmark": "DBIQ Optimum Yield Energy", "ticker": "DBE", "name": "Invesco DB Energy Fund", "leverage": "1x Multi-Fuel & Heating Oil", "expense": "0.77%"},
    {"group": "Refined Products", "benchmark": "MVIS Global Oil Refiners", "ticker": "CRAK", "name": "VanEck Oil Refiners ETF", "leverage": "1x Crack Spread Refiners", "expense": "0.60%"},
    # Natural Gas
    {"group": "Natural Gas", "benchmark": "Henry Hub Natural Gas", "ticker": "UNG", "name": "United States Natural Gas Fund", "leverage": "1x Front-Month Nat Gas", "expense": "1.06%"},
    {"group": "Natural Gas", "benchmark": "Bloomberg Nat Gas Subindex", "ticker": "BOIL", "name": "ProShares Ultra Bloomberg Nat Gas", "leverage": "2x Daily Leveraged Long", "expense": "0.95%"},
    {"group": "Natural Gas", "benchmark": "Bloomberg Nat Gas Subindex", "ticker": "KOLD", "name": "ProShares UltraShort Nat Gas", "leverage": "-2x Leveraged Inverse", "expense": "0.95%"},
    # Biofuels
    {"group": "Biofuels", "benchmark": "CBOT Corn Futures", "ticker": "CORN", "name": "Teucrium Corn Fund", "leverage": "1x Ethanol Feedstock", "expense": "0.26%"},
    {"group": "Biofuels", "benchmark": "US Ethanol Production", "ticker": "GPRE", "name": "Green Plains Inc.", "leverage": "1x Pure Ethanol Refiner", "expense": "Operating"},
    {"group": "Biofuels", "benchmark": "Renewable Fuels", "ticker": "AMTX", "name": "Aemetis, Inc.", "leverage": "1x Biodiesel & RNG Producer", "expense": "Operating"},
    # Metals
    {"group": "Metals", "benchmark": "COMEX Gold Futures (/GC)", "ticker": "GLD", "name": "SPDR Gold Trust", "leverage": "1x Physical Gold Bullion", "expense": "0.40%"},
    {"group": "Metals", "benchmark": "COMEX Silver Futures (/SI)", "ticker": "SLV", "name": "iShares Silver Trust", "leverage": "1x Physical Silver Bullion", "expense": "0.50%"},
    {"group": "Metals", "benchmark": "COMEX Copper Futures (/HG)", "ticker": "CPER", "name": "United States Copper Index Fund", "leverage": "1x Front-Month Copper", "expense": "0.88%"},
    # Broad Commodities
    {"group": "Broad Commodities", "benchmark": "DBIQ Diversified Commodity", "ticker": "DBC", "name": "Invesco DB Commodity Index", "leverage": "1x Multi-Commodity Strip", "expense": "0.85%"},
    {"group": "Broad Commodities", "benchmark": "Energy Select Sector", "ticker": "XLE", "name": "Energy Select Sector SPDR", "leverage": "1x Large-Cap Energy", "expense": "0.09%"}
]

with tab_commodities:
    st.markdown("#### ⚡ Commodity & Derivative Futures (Energy, Metals, Ag & Leveraged Funds)")
    
    selected_group = st.selectbox(
        "Filter by Commodity Group", 
        ["All"] + sorted(list(set(c["group"] for c in COMMODITIES_REGISTRY)))
    )

    active_comms = [c for c in COMMODITIES_REGISTRY if selected_group == "All" or c["group"] == selected_group]
    comm_tickers = [c["ticker"] for c in active_comms]
    comm_data = fetch_ticker_data(comm_tickers)

    comm_rows = []
    for c in active_comms:
        t = c["ticker"]
        if t in comm_data:
            d = comm_data[t]
            comm_rows.append({
                "Group": c["group"],
                "Benchmark": c["benchmark"],
                "Ticker": t,
                "Fund Name": c["name"],
                "Leverage": c["leverage"],
                "Price": d["price"],
                "Change ($)": d["change_dlr"],
                "Change (%)": d["change_pct"],
                "Day Range": f"${d['day_low']:.2f} - ${d['day_high']:.2f}",
                "9 EMA": d["ema_9"],
                "21 EMA": d["ema_21"],
                "30D Gain": d["gain_30"],
                "Volume": f"{d['vol']:,}",
                "Expense": c["expense"],
                "Momentum": "▲ Bullish" if d["bullish"] else "▼ Bearish",
                "30-Day Trend": d["sparkline"]
            })

    if comm_rows:
        df_comm = pd.DataFrame(comm_rows)
        st.dataframe(
            df_comm,
            column_config={
                "Price": st.column_config.NumberColumn(format="$%.2f"),
                "Change ($)": st.column_config.NumberColumn(format="$%.2f"),
                "Change (%)": st.column_config.NumberColumn(format="%+.2f%%"),
                "9 EMA": st.column_config.NumberColumn(format="$%.2f"),
                "21 EMA": st.column_config.NumberColumn(format="$%.2f"),
                "30D Gain": st.column_config.NumberColumn(format="%+.2f%%"),
                "30-Day Trend": st.column_config.LineChartColumn("30-Day Trend")
            },
            hide_index=True,
            use_container_width=True
        )

# Sidebar utilities
st.sidebar.markdown("### Settings")
if st.sidebar.button("🔄 Force Refresh Quotes"):
    st.cache_data.clear()
    st.rerun()
