import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np

st.set_page_config(
    page_title="Sector Intelligence & Momentum",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Helper function to prevent Markdown from interpreting indented HTML as code
def render_html(html_code):
    clean = "\n".join(line.strip() for line in html_code.splitlines() if line.strip())
    if hasattr(st, "html"):
        st.html(clean)
    else:
        st.markdown(clean, unsafe_allow_html=True)

# ---------------------------------------------------------
# CUSTOM TERMINAL / SPREADSHEET CSS
# ---------------------------------------------------------
css_styling = """
<style>
    .block-container {
        padding-top: 1.5rem !important;
        padding-bottom: 2rem !important;
        padding-left: 2rem !important;
        padding-right: 2rem !important;
    }
    .benchmark-container {
        display: flex;
        flex-wrap: wrap;
        gap: 6px;
        margin-bottom: 16px;
    }
    .bench-card {
        flex: 1 1 115px;
        min-width: 110px;
        border: 1px solid #D0D7DE;
        background: #FFFFFF;
        text-align: center;
        padding: 5px 3px;
        border-radius: 2px;
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
    }
    .bench-title {
        font-size: 10.5px;
        font-weight: 600;
        color: #24292F;
        border-bottom: 1px solid #E1E4E8;
        padding-bottom: 2px;
        margin-bottom: 2px;
        white-space: nowrap;
    }
    .bench-price {
        font-size: 11px;
        font-weight: 600;
        white-space: nowrap;
    }
    .sheet-table {
        width: 100%;
        border-collapse: collapse;
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
        font-size: 11.5px;
        background-color: #FFFFFF;
        border: 1px solid #D0D7DE;
        margin-bottom: 20px;
    }
    .sheet-table th {
        background-color: #1A365D;
        color: #FFFFFF;
        font-weight: 600;
        padding: 5px 8px;
        border: 1px solid #2D3748;
        text-align: left;
        white-space: nowrap;
    }
    .sheet-table td {
        padding: 4.5px 8px;
        border: 1px solid #E1E4E8;
        color: #24292F;
        white-space: nowrap;
    }
    .sheet-table tr:hover {
        background-color: #F8FAFC;
    }
    .section-banner {
        background-color: #0C2340;
        color: #FFFFFF;
        font-weight: bold;
        font-size: 12px;
        letter-spacing: 0.5px;
        padding: 7px 10px;
        border-top-left-radius: 3px;
        border-top-right-radius: 3px;
        text-transform: uppercase;
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
    }
    .pos-cell {
        background-color: #E6F4EA !important;
        color: #137333 !important;
        font-weight: 500;
    }
    .neg-cell {
        background-color: #FCE8E6 !important;
        color: #C5221F !important;
        font-weight: 500;
    }
    .bullish-badge {
        background-color: #E6F4EA;
        color: #137333;
        font-weight: 600;
        padding: 1px 5px;
        border-radius: 3px;
        display: inline-block;
    }
    .bearish-badge {
        background-color: #FCE8E6;
        color: #C5221F;
        font-weight: 600;
        padding: 1px 5px;
        border-radius: 3px;
        display: inline-block;
    }
</style>
"""
render_html(css_styling)

# ---------------------------------------------------------
# CACHED DATA FETCHER
# ---------------------------------------------------------
@st.cache_data(ttl=300)
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

            ema_9 = close.ewm(span=9, adjust=False).mean()
            ema_21 = close.ewm(span=21, adjust=False).mean()

            hist_30 = close.iloc[-22:] if len(close) >= 22 else close
            gain_30 = ((close.iloc[-1] - hist_30.iloc[0]) / hist_30.iloc[0]) * 100

            info = stock.info or {}
            market_cap = info.get("marketCap", None)
            pe_ratio = info.get("trailingPE", None)
            short_name = info.get("shortName", ticker)

            data_dict[ticker] = {
                "name": short_name,
                "price": float(close.iloc[-1]),
                "change_dlr": float(close.iloc[-1] - close.iloc[-2]),
                "change_pct": float((close.iloc[-1] - close.iloc[-2]) / close.iloc[-2] * 100),
                "gain_30": float(gain_30),
                "ema_9": float(ema_9.iloc[-1]),
                "ema_21": float(ema_21.iloc[-1]),
                "day_low": float(low.iloc[-1]),
                "day_high": float(high.iloc[-1]),
                "vol": int(volume.iloc[-1]),
                "market_cap": market_cap,
                "pe_ratio": pe_ratio,
                "sparkline": hist_30.tolist(),
                "bullish": bool(ema_9.iloc[-1] > ema_21.iloc[-1])
            }
        except Exception:
            continue
    return data_dict

def make_svg_sparkline(prices, is_positive=True, width=100, height=20):
    if not prices or len(prices) < 2:
        return ""
    min_p, max_p = min(prices), max(prices)
    rng = max_p - min_p if max_p != min_p else 1.0
    pts = []
    step = width / (len(prices) - 1)
    for i, p in enumerate(prices):
        x = i * step
        y = height - ((p - min_p) / rng * (height - 6) + 3)
        pts.append(f"{x:.1f},{y:.1f}")
    color = "#137333" if is_positive else "#C5221F"
    return f'<svg width="{width}" height="{height}" style="display:block; margin:auto;"><polyline fill="none" stroke="{color}" stroke-width="1.8" points="{" ".join(pts)}"/></svg>'

def fmt_mcap(val):
    if not val or pd.isna(val):
        return "--"
    if val >= 1e12:
        return f"${val / 1e12:.2f}T"
    if val >= 1e9:
        return f"${val / 1e9:.2f}B"
    return f"${val / 1e6:.2f}M"

# ---------------------------------------------------------
# 1. TOP MACRO & SECTOR BENCHMARK RIBBON
# ---------------------------------------------------------
st.markdown("### 🌐 REAL-TIME SECTOR INTELLIGENCE & MOMENTUM DASHBOARD")
st.markdown("<p style='font-size:12px; color:#57606A; margin-top:-10px;'>GICS Sector SPDR Benchmarks • Interactive Sector Explorer • Top Market Cap Giants • Top Momentum Gainers</p>", unsafe_allow_html=True)

benchmarks_meta = [
    ("XLK", "XLK • Tech"),
    ("XLV", "XLV • Health"),
    ("XLF", "XLF • Financials"),
    ("XLY", "XLY • Cons Disc"),
    ("XLC", "XLC • Commun."),
    ("XLI", "XLI • Industrials"),
    ("XLP", "XLP • Staples"),
    ("XLE", "XLE • Energy"),
    ("XLU", "XLU • Utilities"),
    ("XLRE", "XLRE • Real Est"),
    ("XLB", "XLB • Materials"),
    ("SPY", "SPY • S&P 500"),
    ("QQQ", "QQQ • Nasdaq"),
    ("DIA", "DIA • Dow Jones")
]

bench_data = fetch_ticker_data([b[0] for b in benchmarks_meta])

bench_html = '<div class="benchmark-container">'
for ticker, label in benchmarks_meta:
    if ticker in bench_data:
        d = bench_data[ticker]
        color = "#137333" if d["change_pct"] >= 0 else "#C5221F"
        sign = "+" if d["change_pct"] >= 0 else ""
        bench_html += f'<div class="bench-card"><div class="bench-title">{label}</div><div class="bench-price" style="color: {color};">${d["price"]:.2f} ({sign}{d["change_pct"]:.2f}%)</div></div>'
    else:
        bench_html += f'<div class="bench-card"><div class="bench-title">{label}</div><div class="bench-price" style="color: #57606A;">--</div></div>'
bench_html += '</div>'
render_html(bench_html)

# ---------------------------------------------------------
# TABS SETUP
# ---------------------------------------------------------

tab_portfolio, tab_sector, tab_commodities = st.tabs(["💼 PORTFOLIO VIEWER", "📊 ACTIVE SECTOR EXPLORER", "🛢️ COMMODITY & DERIVATIVE FUTURES"])

# ---------------------------------------------------------
# PORTFOLIO TAB
# ---------------------------------------------------------
with tab_portfolio:
    st.markdown("<div class='section-banner'>PORTFOLIO HOLDINGS & PERFORMANCE</div>", unsafe_allow_html=True)
    
    # User holdings configuration (Ticker, Shares, Avg Cost)
    portfolio_holdings = [
        {"ticker": "NVDA", "shares": 50, "cost": 115.50},
        {"ticker": "AAPL", "shares": 30, "cost": 175.00},
        {"ticker": "MSFT", "shares": 20, "cost": 410.00},
        {"ticker": "CRDO", "shares": 100, "cost": 32.50},
        {"ticker": "MRVL", "shares": 40, "cost": 72.00},
        {"ticker": "AVGO", "shares": 15, "cost": 140.00}
    ]
    
    port_tickers = [h["ticker"] for h in portfolio_holdings]
    port_data = fetch_ticker_data(port_tickers)
    
    total_market_value = 0.0
    total_cost_basis = 0.0
    total_daily_gain_dlr = 0.0
    
    port_rows = []
    for h in portfolio_holdings:
        t = h["ticker"]
        shares = h["shares"]
        cost = h["cost"]
        cost_basis = shares * cost
        total_cost_basis += cost_basis
        
        if t in port_data:
            d = port_data[t]
            price = d["price"]
            market_value = shares * price
            total_market_value += market_value
            
            # Daily Return
            daily_change_dlr_per_share = d["change_dlr"]
            position_daily_gain_dlr = daily_change_dlr_per_share * shares
            total_daily_gain_dlr += position_daily_gain_dlr
            daily_change_pct = d["change_pct"]
            
            # Overall Gain / Loss
            overall_gain_dlr = market_value - cost_basis
            overall_gain_pct = (overall_gain_dlr / cost_basis) * 100 if cost_basis > 0 else 0.0
            
            port_rows.append({
                "ticker": t,
                "name": d["name"],
                "shares": shares,
                "cost": cost,
                "price": price,
                "mval": market_value,
                "daily_dlr": position_daily_gain_dlr,
                "daily_pct": daily_change_pct,
                "overall_dlr": overall_gain_dlr,
                "overall_pct": overall_gain_pct,
                "bullish": d["bullish"],
                "sparkline": d["sparkline"]
            })
    
    if port_rows:
        total_overall_gain_dlr = total_market_value - total_cost_basis
        total_overall_gain_pct = (total_overall_gain_dlr / total_cost_basis) * 100 if total_cost_basis > 0 else 0.0
        total_daily_pct = (total_daily_gain_dlr / (total_market_value - total_daily_gain_dlr)) * 100 if (total_market_value - total_daily_gain_dlr) > 0 else 0.0
        
        # Summary KPI Metrics Cards
        k1, k2, k3, k4 = st.columns(4)
        k1.metric("Total Portfolio Value", f"${total_market_value:,.2f}")
        k2.metric("Daily Return", f"${total_daily_gain_dlr:+,.2f}", f"{total_daily_pct:+.2f}%")
        k3.metric("Total Unrealized Gain", f"${total_overall_gain_dlr:+,.2f}", f"{total_overall_gain_pct:+.2f}%")
        k4.metric("Total Cost Basis", f"${total_cost_basis:,.2f}")
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        # Render Portfolio Table
        port_html = '<div style="overflow-x: auto; margin-bottom: 20px;">'
        port_html += '<table class="sheet-table"><thead><tr><th>Ticker</th><th>Company Name</th><th>Shares</th><th>Avg Cost</th><th>Current Price</th><th>Market Value</th><th>Daily Gain ($)</th><th>Daily Gain (%)</th><th>Overall Gain ($)</th><th>Overall Gain (%)</th><th>Momentum</th><th>30-Day Trend</th></tr></thead><tbody>'
        
        for r in port_rows:
            c_daily = "pos-cell" if r["daily_dlr"] >= 0 else "neg-cell"
            c_overall = "pos-cell" if r["overall_dlr"] >= 0 else "neg-cell"
            s_daily_dlr = "+" if r["daily_dlr"] >= 0 else ""
            s_daily_pct = "+" if r["daily_pct"] >= 0 else ""
            s_overall_dlr = "+" if r["overall_dlr"] >= 0 else ""
            s_overall_pct = "+" if r["overall_pct"] >= 0 else ""
            
            cue = '<span class="bullish-badge">▲ Bullish</span>' if r["bullish"] else '<span class="bearish-badge">▼ Bearish</span>'
            spark = make_svg_sparkline(r["sparkline"], is_positive=(r["overall_dlr"] >= 0))
            
            port_html += f'<tr><td style="font-weight:600;">{r["ticker"]}</td><td>{r["name"]}</td><td>{r["shares"]:,}</td><td>${r["cost"]:.2f}</td><td>${r["price"]:.2f}</td><td>${r["mval"]:,.2f}</td><td class="{c_daily}">{s_daily_dlr}${r["daily_dlr"]:,.2f}</td><td class="{c_daily}">{s_daily_pct}{r["daily_pct']:.2f}%</td><td class="{c_overall}">{s_overall_dlr}${r["overall_dlr"]:,.2f}</td><td class="{c_overall}">{s_overall_pct}{r["overall_pct']:.2f}%</td><td style="text-align:center;">{cue}</td><td>{spark}</td></tr>'
        
        port_html += '</tbody></table></div>'
        render_html(port_html)
    else:
        st.info("No portfolio data available.")

SECTOR_DATASETS = {
    "Information Technology": [
        "AAPL", "NVDA", "MSFT", "AVGO", "ORCL", "CRM", "AMD", "QCOM", "ADBE", "INTC", "TXN", "MU", "CRDO", "MRVL"
    ],
    "Health Care": [
        "LLY", "UNH", "JNJ", "ABBV", "MRK", "TMO", "ABT", "PFE", "AMGN", "DHR", "BMY", "ISRG"
    ],
    "Financials": [
        "JPM", "V", "MA", "BAC", "WFC", "MS", "GS", "BLK", "C", "AXP", "SCHW", "PGR"
    ],
    "Consumer Discretionary": [
        "AMZN", "TSLA", "HD", "MCD", "NKE", "SBUX", "LOW", "BKNG", "TJX", "TGT", "MAR", "CMG"
    ],
    "Communication Services": [
        "GOOGL", "META", "NFLX", "VZ", "DIS", "TMUS", "T", "SPOT", "DASH", "CMCSA", "WBD", "EA"
    ],
    "Industrials": [
        "GE", "CAT", "RTX", "UNP", "HON", "UPS", "BA", "DE", "LMT", "GEV", "ETN", "WM"
    ],
    "Consumer Staples": [
        "WMT", "PG", "COST", "KO", "PEP", "PM", "MO", "MDLZ", "CL", "TGT", "GIS", "SYY"
    ],
    "Energy": [
        "XOM", "CVX", "COP", "SLB", "EOG", "MPC", "PSX", "VLO", "OXY", "KMI", "WMB"
    ],
    "Real Estate": [
        "PLD", "AMT", "EQIX", "SPG", "O", "WELL", "PSA", "VICI", "CCI", "DLR", "SBAC", "EXR"
    ],
    "Materials": [
        "LIN", "SHW", "FCX", "APD", "NEM", "ECL", "CTVA", "DOW", "PPG", "MLM", "VMC", "CF"
    ],
    "Utilities": [
        "NEE", "SO", "DUK", "CEG", "SRE", "AEP", "PCG", "XEL", "ED", "PEG", "ETR", "FE"
    ]
}

with tab_sector:
    col_sel, col_note = st.columns([1, 3])
    with col_sel:
        selected_sector = st.selectbox("Select Sector", list(SECTOR_DATASETS.keys()), index=0)
    with col_note:
        st.markdown("<p style='font-size:12px; color:#57606A; margin-top:28px;'>• Showing Top 20 Market Cap Leaders & Top 10 30-Day Gainers</p>", unsafe_allow_html=True)

    sector_tickers = SECTOR_DATASETS[selected_sector]
    sec_data = fetch_ticker_data(sector_tickers)

    rows = []
    for t in sector_tickers:
        if t in sec_data:
            d = sec_data[t]
            rows.append({
                "ticker": t,
                "name": d["name"],
                "sector": selected_sector,
                "price": d["price"],
                "chg_dlr": d["change_dlr"],
                "chg_pct": d["change_pct"],
                "gain_30": d["gain_30"],
                "mcap": d["market_cap"],
                "mcap_fmt": fmt_mcap(d["market_cap"]),
                "pe": f"{d['pe_ratio']:.2f}" if d["pe_ratio"] else "--",
                "bullish": d["bullish"],
                "sparkline": d["sparkline"]
            })

    if rows:
        col_l, col_r = st.columns(2)

        # 1. TOP MARKET CAP LEADERS
        with col_l:
            sorted_mcap = sorted(rows, key=lambda x: (x["mcap"] or 0), reverse=True)
            tbl_html = '<div style="overflow-x: auto; margin-bottom: 20px;">'
            tbl_html += '<div class="section-banner">TOP 20 MARKET CAP LEADERS</div>'
            tbl_html += '<table class="sheet-table"><thead><tr><th>Ticker</th><th>Company Name</th><th>Price</th><th>Change ($)</th><th>Change (%)</th><th>30D Gain</th><th>Market Cap</th><th>P/E</th><th>Momentum</th><th>30-Day Trend</th></tr></thead><tbody>'
            for r in sorted_mcap:
                c_dlr = "pos-cell" if r["chg_dlr"] >= 0 else "neg-cell"
                c_pct = "pos-cell" if r["chg_pct"] >= 0 else "neg-cell"
                c_30 = "pos-cell" if r["gain_30"] >= 0 else "neg-cell"
                s_dlr = "+" if r["chg_dlr"] >= 0 else ""
                s_pct = "+" if r["chg_pct"] >= 0 else ""
                s_30 = "+" if r["gain_30"] >= 0 else ""
                cue = '<span class="bullish-badge">▲ Bullish</span>' if r["bullish"] else '<span class="bearish-badge">▼ Bearish</span>'
                spark = make_svg_sparkline(r["sparkline"], is_positive=(r["gain_30"] >= 0))

                tbl_html += f'<tr><td style="font-weight:600;">{r["ticker"]}</td><td style="max-width:120px; overflow:hidden; text-overflow:ellipsis;">{r["name"]}</td><td>${r["price"]:.2f}</td><td class="{c_dlr}">{s_dlr}${r["chg_dlr"]:.2f}</td><td class="{c_pct}">{s_pct}{r["chg_pct"]:.2f}%</td><td class="{c_30}">{s_30}{r["gain_30"]:.2f}%</td><td>{r["mcap_fmt"]}</td><td>{r["pe"]}</td><td style="text-align:center;">{cue}</td><td>{spark}</td></tr>'
            tbl_html += '</tbody></table></div>'
            render_html(tbl_html)

        # 2. TOP 10 MOMENTUM LEADERS
        with col_r:
            sorted_mom = sorted(rows, key=lambda x: x["gain_30"], reverse=True)[:10]
            tbl_html2 = '<div style="overflow-x: auto; margin-bottom: 20px;">'
            tbl_html2 += '<div class="section-banner">TOP 10 30-DAY GAINERS (MOMENTUM LEADERS)</div>'
            tbl_html2 += '<table class="sheet-table"><thead><tr><th>Ticker</th><th>Company Name</th><th>Price</th><th>30D Gain</th><th>Today Change</th><th>Market Cap</th><th>Momentum</th><th>30-Day Trend</th></tr></thead><tbody>'
            for r in sorted_mom:
                c_pct = "pos-cell" if r["chg_pct"] >= 0 else "neg-cell"
                c_30 = "pos-cell" if r["gain_30"] >= 0 else "neg-cell"
                s_pct = "+" if r["chg_pct"] >= 0 else ""
                s_30 = "+" if r["gain_30"] >= 0 else ""
                cue = '<span class="bullish-badge">▲ Bullish</span>' if r["bullish"] else '<span class="bearish-badge">▼ Bearish</span>'
                spark = make_svg_sparkline(r["sparkline"], is_positive=(r["gain_30"] >= 0))

                tbl_html2 += f'<tr><td style="font-weight:600;">{r["ticker"]}</td><td style="max-width:120px; overflow:hidden; text-overflow:ellipsis;">{r["name"]}</td><td>${r["price"]:.2f}</td><td class="{c_30}">{s_30}{r["gain_30"]:.2f}%</td><td class="{c_pct}">{s_pct}{r["chg_pct"]:.2f}%</td><td>{r["mcap_fmt"]}</td><td style="text-align:center;">{cue}</td><td>{spark}</td></tr>'
            tbl_html2 += '</tbody></table></div>'
            render_html(tbl_html2)

# ---------------------------------------------------------
# 3. COMMODITIES TAB
# ---------------------------------------------------------
COMMODITIES_REGISTRY = [
    {"group": "Crude Oil", "benchmark": "WTI Light Sweet Crude", "ticker": "USO", "name": "United States Oil Fund LP", "leverage": "1x Spot / Front-Month", "expense": "0.60%"},
    {"group": "Crude Oil", "benchmark": "Bloomberg WTI Crude Subindex", "ticker": "UCO", "name": "ProShares Ultra Bloomberg Crude", "leverage": "2x Daily Leveraged Long", "expense": "0.95%"},
    {"group": "Crude Oil", "benchmark": "Bloomberg WTI Crude Subindex", "ticker": "SCO", "name": "ProShares UltraShort Bloomberg Crude", "leverage": "-2x Leveraged Inverse", "expense": "0.95%"},
    {"group": "Crude Oil", "benchmark": "WTI Crude Futures (12-Month)", "ticker": "USL", "name": "United States 12 Month Oil Fund", "leverage": "1x 12-Month Strip Curve", "expense": "0.90%"},
    {"group": "Crude Oil", "benchmark": "ICE Brent Crude Futures", "ticker": "BNO", "name": "United States Brent Oil Fund LP", "leverage": "1x Front-Month Brent", "expense": "1.02%"},
    {"group": "Refined Products", "benchmark": "NYMEX RBOB Gasoline", "ticker": "UGA", "name": "United States Gasoline Fund LP", "leverage": "1x Front-Month RBOB Gas", "expense": "0.97%"},
    {"group": "Refined Products", "benchmark": "DBIQ Optimum Yield Energy", "ticker": "DBE", "name": "Invesco DB Energy Fund", "leverage": "1x Multi-Fuel & Heating Oil", "expense": "0.77%"},
    {"group": "Refined Products", "benchmark": "MVIS Global Oil Refiners", "ticker": "CRAK", "name": "VanEck Oil Refiners ETF", "leverage": "1x Crack Spread Refiners", "expense": "0.60%"},
    {"group": "Natural Gas", "benchmark": "Henry Hub Natural Gas", "ticker": "UNG", "name": "United States Natural Gas Fund", "leverage": "1x Front-Month Nat Gas", "expense": "1.06%"},
    {"group": "Natural Gas", "benchmark": "Bloomberg Nat Gas Subindex", "ticker": "BOIL", "name": "ProShares Ultra Bloomberg Nat Gas", "leverage": "2x Daily Leveraged Long", "expense": "0.95%"},
    {"group": "Natural Gas", "benchmark": "Bloomberg Nat Gas Subindex", "ticker": "KOLD", "name": "ProShares UltraShort Nat Gas", "leverage": "-2x Leveraged Inverse", "expense": "0.95%"},
    {"group": "Biofuels", "benchmark": "CBOT Corn Futures", "ticker": "CORN", "name": "Teucrium Corn Fund", "leverage": "1x Ethanol Feedstock", "expense": "0.26%"},
    {"group": "Biofuels", "benchmark": "US Ethanol Production", "ticker": "GPRE", "name": "Green Plains Inc.", "leverage": "1x Pure Ethanol Refiner", "expense": "Operating"},
    {"group": "Biofuels", "benchmark": "Renewable Fuels", "ticker": "AMTX", "name": "Aemetis, Inc.", "leverage": "1x Biodiesel & RNG Producer", "expense": "Operating"},
    {"group": "Metals", "benchmark": "COMEX Gold Futures (/GC)", "ticker": "GLD", "name": "SPDR Gold Trust", "leverage": "1x Physical Gold Bullion", "expense": "0.40%"},
    {"group": "Metals", "benchmark": "COMEX Silver Futures (/SI)", "ticker": "SLV", "name": "iShares Silver Trust", "leverage": "1x Physical Silver Bullion", "expense": "0.50%"},
    {"group": "Metals", "benchmark": "COMEX Copper Futures (/HG)", "ticker": "CPER", "name": "United States Copper Index Fund", "leverage": "1x Front-Month Copper", "expense": "0.88%"},
    {"group": "Broad Commodities", "benchmark": "DBIQ Diversified Commodity", "ticker": "DBC", "name": "Invesco DB Commodity Index", "leverage": "1x Multi-Commodity Strip", "expense": "0.85%"},
    {"group": "Broad Commodities", "benchmark": "Energy Select Sector", "ticker": "XLE", "name": "Energy Select Sector SPDR", "leverage": "1x Large-Cap Energy", "expense": "0.09%"}
]

with tab_commodities:
    comm_tickers = [c["ticker"] for c in COMMODITIES_REGISTRY]
    comm_data = fetch_ticker_data(comm_tickers)

    comm_html = '<div style="overflow-x: auto; margin-top: 10px;">'
    comm_html += '<div class="section-banner">COMMODITY & DERIVATIVE FUTURES (ENERGY, METALS, AG & LEVERAGED FUNDS)</div>'
    comm_html += '<table class="sheet-table"><thead><tr><th>Commodity Group</th><th>Underlying Benchmark</th><th>Ticker</th><th>Fund Name</th><th>Exposure / Leverage</th><th>Current Price</th><th>Change ($)</th><th>Change (%)</th><th>Day Range</th><th>9 EMA</th><th>21 EMA</th><th>30D Gain</th><th>Volume</th><th>Expense</th><th>Momentum</th><th>30-Day Trend</th></tr></thead><tbody>'
    
    for c in COMMODITIES_REGISTRY:
        t = c["ticker"]
        if t in comm_data:
            d = comm_data[t]
            c_dlr = "pos-cell" if d["change_dlr"] >= 0 else "neg-cell"
            c_pct = "pos-cell" if d["change_pct"] >= 0 else "neg-cell"
            c_30 = "pos-cell" if d["gain_30"] >= 0 else "neg-cell"
            s_dlr = "+" if d["change_dlr"] >= 0 else ""
            s_pct = "+" if d["change_pct"] >= 0 else ""
            s_30 = "+" if d["gain_30"] >= 0 else ""
            cue = '<span class="bullish-badge">▲ Bullish</span>' if d["bullish"] else '<span class="bearish-badge">▼ Bearish</span>'
            spark = make_svg_sparkline(d["sparkline"], is_positive=(d["gain_30"] >= 0))

            comm_html += f'<tr><td>{c["group"]}</td><td>{c["benchmark"]}</td><td style="font-weight:600;">{t}</td><td>{c["name"]}</td><td>{c["leverage"]}</td><td>${d["price"]:.2f}</td><td class="{c_dlr}">{s_dlr}${d["change_dlr"]:.2f}</td><td class="{c_pct}">{s_pct}{d["change_pct"]:.2f}%</td><td>${d["day_low"]:.2f} - ${d["day_high"]:.2f}</td><td>${d["ema_9"]:.2f}</td><td>${d["ema_21"]:.2f}</td><td class="{c_30}">{s_30}{d["gain_30"]:.2f}%</td><td>{d["vol"]:,}</td><td>{c["expense"]}</td><td style="text-align:center;">{cue}</td><td>{spark}</td></tr>'
    comm_html += '</tbody></table></div>'
    render_html(comm_html)

# Sidebar utilities
st.sidebar.markdown("### Controls")
if st.sidebar.button("🔄 Force Refresh Data"):
    st.cache_data.clear()
    st.rerun()