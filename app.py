import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import plotly.express as px
import requests
import io

st.set_page_config(
    page_title="SECTOR INTELLIGENCE & MOMENTUM TERMINAL",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ---------------------------------------------------------
# SESSION STATE & THEME DEFINITIONS
# ---------------------------------------------------------
if "selected_sector" not in st.session_state:
    st.session_state.selected_sector = "Information Technology"
if "theme_choice" not in st.session_state:
    st.session_state.theme_choice = "Slate (Balanced)"

THEMES = {
    "Slate (Balanced)": {
        "body_bg": "#1E293B",
        "text_color": "#F8FAFC",
        "sidebar_bg": "#0F172A",
        "sidebar_border": "#334155",
        "card_bg": "#334155",
        "card_border": "#64748B",
        "card_hover": "#475569",
        "banner_bg": "#0F172A",
        "banner_text": "#38BDF8",
        "banner_border": "#334155",
        "th_bg": "#0F172A",
        "th_text": "#F8FAFC",
        "th_hover": "#1E293B",
        "table_bg": "#1E293B",
        "table_border": "#475569",
        "td_border": "#334155",
        "td_text": "#F1F5F9",
        "tr_hover": "#334155",
        "pos_bg": "#064E3B",
        "pos_text": "#6EE7B7",
        "neg_bg": "#7F1D1D",
        "neg_text": "#FCA5A5",
        "badge_bull_bg": "#059669",
        "badge_bull_text": "#FFFFFF",
        "badge_bear_bg": "#DC2626",
        "badge_bear_text": "#FFFFFF",
        "tab_bg": "#334155",
        "tab_text": "#CBD5E1",
        "tab_active_bg": "#0F172A",
        "tab_active_text": "#38BDF8",
        "metric_bg": "#334155",
        "metric_border": "#64748B",
        "metric_label": "#94A3B8",
        "metric_val": "#F8FAFC",
        "plotly_plot_bg": "#1E293B",
        "plotly_paper_bg": "#1E293B",
        "plotly_grid": "#334155",
        "plotly_line": "#64748B",
        "spark_pos": "#34D399",
        "spark_neg": "#F87171"
    },
    "Dark (Terminal)": {
        "body_bg": "#090D16",
        "text_color": "#F3F4F6",
        "sidebar_bg": "#030712",
        "sidebar_border": "#1F2937",
        "card_bg": "#111827",
        "card_border": "#374151",
        "card_hover": "#1F2937",
        "banner_bg": "#111827",
        "banner_text": "#10B981",
        "banner_border": "#374151",
        "th_bg": "#030712",
        "th_text": "#E5E7EB",
        "th_hover": "#1F2937",
        "table_bg": "#0B0F19",
        "table_border": "#374151",
        "td_border": "#1F2937",
        "td_text": "#F3F4F6",
        "tr_hover": "#1F2937",
        "pos_bg": "#064E3B",
        "pos_text": "#34D399",
        "neg_bg": "#7F1D1D",
        "neg_text": "#F87171",
        "badge_bull_bg": "#10B981",
        "badge_bull_text": "#000000",
        "badge_bear_bg": "#EF4444",
        "badge_bear_text": "#FFFFFF",
        "tab_bg": "#111827",
        "tab_text": "#9CA3AF",
        "tab_active_bg": "#1F2937",
        "tab_active_text": "#10B981",
        "metric_bg": "#111827",
        "metric_border": "#374151",
        "metric_label": "#9CA3AF",
        "metric_val": "#F9FAFB",
        "plotly_plot_bg": "#0B0F19",
        "plotly_paper_bg": "#0B0F19",
        "plotly_grid": "#1F2937",
        "plotly_line": "#4B5563",
        "spark_pos": "#10B981",
        "spark_neg": "#EF4444"
    },
    "Light (Classic)": {
        "body_bg": "#FFFFFF",
        "text_color": "#0F172A",
        "sidebar_bg": "#F8FAFC",
        "sidebar_border": "#CBD5E1",
        "card_bg": "#F8FAFC",
        "card_border": "#475569",
        "card_hover": "#E2E8F0",
        "banner_bg": "#1E293B",
        "banner_text": "#F8FAFC",
        "banner_border": "#0F172A",
        "th_bg": "#0F172A",
        "th_text": "#F8FAFC",
        "th_hover": "#1E293B",
        "table_bg": "#FFFFFF",
        "table_border": "#334155",
        "td_border": "#CBD5E1",
        "td_text": "#0F172A",
        "tr_hover": "#F1F5F9",
        "pos_bg": "#DCFCE7",
        "pos_text": "#14532D",
        "neg_bg": "#FEE2E2",
        "neg_text": "#7F1D1D",
        "badge_bull_bg": "#15803D",
        "badge_bull_text": "#FFFFFF",
        "badge_bear_bg": "#B91C1C",
        "badge_bear_text": "#FFFFFF",
        "tab_bg": "#E2E8F0",
        "tab_text": "#0F172A",
        "tab_active_bg": "#0F172A",
        "tab_active_text": "#FFFFFF",
        "metric_bg": "#F8FAFC",
        "metric_border": "#475569",
        "metric_label": "#475569",
        "metric_val": "#0F172A",
        "plotly_plot_bg": "#F8FAFC",
        "plotly_paper_bg": "#FFFFFF",
        "plotly_grid": "#E2E8F0",
        "plotly_line": "#475569",
        "spark_pos": "#15803D",
        "spark_neg": "#B91C1C"
    }
}

# ---------------------------------------------------------
# SIDEBAR SETTINGS MENU
# ---------------------------------------------------------
st.sidebar.markdown("<div class='section-banner' style='margin-bottom:12px;'>SYSTEM SETTINGS</div>", unsafe_allow_html=True)
theme_select = st.sidebar.selectbox(
    "TERMINAL THEME PRESET",
    list(THEMES.keys()),
    index=list(THEMES.keys()).index(st.session_state.theme_choice)
)
if theme_select != st.session_state.theme_choice:
    st.session_state.theme_choice = theme_select
    st.rerun()

thm = THEMES[st.session_state.theme_choice]

if st.sidebar.button("FORCE REFRESH DATA", use_container_width=True):
    st.cache_data.clear()
    st.rerun()

def render_html(html_code):
    clean = "\n".join(line.strip() for line in html_code.splitlines() if line.strip())
    if hasattr(st, "html"):
        st.html(clean)
    else:
        st.markdown(clean, unsafe_allow_html=True)

# ---------------------------------------------------------
# DYNAMIC THEMED CSS (STRICT RECTANGULAR, NO EMOJIS)
# ---------------------------------------------------------
css_styling = f"""
<style>
    .stApp {{
        background-color: {thm['body_bg']} !important;
        color: {thm['text_color']} !important;
    }}
    .block-container {{
        padding-top: 4.2rem !important;
        padding-bottom: 2rem !important;
        padding-left: 1.5rem !important;
        padding-right: 1.5rem !important;
        font-family: -apple-system, BlinkMacSystemFont, "Inter", "Segoe UI", Roboto, sans-serif !important;
        background-color: {thm['body_bg']} !important;
    }}
    section[data-testid="stSidebar"] {{
        background-color: {thm['sidebar_bg']} !important;
        border-right: 1px solid {thm['sidebar_border']} !important;
    }}
    section[data-testid="stSidebar"] * {{
        color: {thm['text_color']} !important;
    }}
    
    /* UNIVERSAL SELECTBOX FIX */
    div[data-testid="stSelectbox"] div[data-baseweb="select"],
    div[data-testid="stSelectbox"] div[data-baseweb="select"] > div,
    div[data-baseweb="select"],
    div[data-baseweb="select"] > div,
    div[data-baseweb="select"] div,
    div[data-baseweb="select"] span {{
        background-color: {thm['card_bg']} !important;
        color: {thm['text_color']} !important;
        border-color: {thm['card_border']} !important;
        border-radius: 0px !important;
    }}
    div[data-baseweb="select"] svg {{
        fill: {thm['text_color']} !important;
        color: {thm['text_color']} !important;
    }}
    div[data-baseweb="popover"],
    div[data-baseweb="popover"] > div,
    div[data-baseweb="popover"] ul,
    div[data-baseweb="popover"] li {{
        background-color: {thm['card_bg']} !important;
        color: {thm['text_color']} !important;
        border-color: {thm['card_border']} !important;
        border-radius: 0px !important;
    }}
    div[data-baseweb="popover"] li:hover,
    div[data-baseweb="popover"] li[aria-selected="true"] {{
        background-color: {thm['card_hover']} !important;
        color: {thm['banner_text']} !important;
    }}

    /* Sidebar Button Styling */
    section[data-testid="stSidebar"] div[data-testid="stButton"] {{
        margin-top: 14px !important;
    }}
    section[data-testid="stSidebar"] div[data-testid="stButton"] > button {{
        background-color: {thm['card_bg']} !important;
        color: {thm['text_color']} !important;
        border: 1px solid {thm['card_border']} !important;
        border-radius: 0px !important;
        font-size: 11px !important;
        font-weight: 700 !important;
        letter-spacing: 0.5px !important;
        padding: 8px 12px !important;
        width: 100% !important;
    }}
    section[data-testid="stSidebar"] div[data-testid="stButton"] > button:hover {{
        background-color: {thm['card_hover']} !important;
        border-color: {thm['banner_text']} !important;
    }}

    /* Table Typography & Colors */
    h1, h2, h3, h4, h5, h6, p, span, label {{
        color: {thm['text_color']} !important;
        font-family: -apple-system, BlinkMacSystemFont, "Inter", "Segoe UI", Roboto, sans-serif !important;
    }}
    .sheet-table {{
        width: 100%;
        border-collapse: collapse;
        font-family: -apple-system, BlinkMacSystemFont, "Inter", "Segoe UI", Roboto, sans-serif;
        font-size: 12px;
        background-color: {thm['table_bg']};
        border: 1px solid {thm['table_border']};
        margin-bottom: 16px;
        font-variant-numeric: tabular-nums;
    }}
    .sheet-table th {{
        background-color: {thm['th_bg']};
        color: {thm['th_text']};
        font-weight: 700;
        padding: 7px 8px;
        border: 1px solid {thm['table_border']};
        text-align: left;
        white-space: nowrap;
        text-transform: uppercase;
        font-size: 11px;
        user-select: none;
    }}
    .sortable-th {{
        cursor: pointer;
        transition: background-color 0.15s ease;
    }}
    .sortable-th:hover {{
        background-color: {thm['th_hover']} !important;
        color: #38BDF8 !important;
    }}
    .sheet-table td {{
        padding: 5px 8px;
        border: 1px solid {thm['td_border']};
        color: {thm['td_text']};
        white-space: nowrap;
    }}
    .sheet-table tr:hover {{
        background-color: {thm['tr_hover']};
    }}
    .section-banner {{
        background-color: {thm['banner_bg']};
        color: {thm['banner_text']};
        font-weight: 700;
        font-size: 11.5px;
        letter-spacing: 0.8px;
        padding: 6px 10px;
        border-radius: 0px !important;
        border: 1px solid {thm['banner_border']};
        border-bottom: none;
        text-transform: uppercase;
    }}
    .pos-cell {{
        background-color: {thm['pos_bg']} !important;
        color: {thm['pos_text']} !important;
        font-weight: 700;
    }}
    .neg-cell {{
        background-color: {thm['neg_bg']} !important;
        color: {thm['neg_text']} !important;
        font-weight: 700;
    }}
    .bullish-badge {{
        background-color: {thm['badge_bull_bg']};
        color: {thm['badge_bull_text']};
        font-weight: 700;
        padding: 2px 6px;
        border-radius: 0px !important;
        display: inline-block;
        font-size: 10px;
        text-transform: uppercase;
    }}
    .bearish-badge {{
        background-color: {thm['badge_bear_bg']};
        color: {thm['badge_bear_text']};
        font-weight: 700;
        padding: 2px 6px;
        border-radius: 0px !important;
        display: inline-block;
        font-size: 10px;
        text-transform: uppercase;
    }}

    /* Ribbon Button Styler */
    div[data-testid*="olumn"] div[data-testid="stButton"] > button,
    div[data-testid="stButton"] > button {{
        border-radius: 0px !important;
        border: 1px solid {thm['card_border']} !important;
        background-color: {thm['card_bg']} !important;
        color: {thm['text_color']} !important;
        padding: 4px 1px !important;
        min-height: 44px !important;
        height: auto !important;
        width: 100% !important;
        display: flex !important;
        flex-direction: column !important;
        align-items: center !important;
        justify-content: center !important;
    }}
    div[data-testid*="olumn"] div[data-testid="stButton"] > button:hover,
    div[data-testid="stButton"] > button:hover {{
        background-color: {thm['card_hover']} !important;
        border-color: {thm['banner_text']} !important;
    }}
    div[data-testid="stButton"] button p,
    div[data-testid="stButton"] button div,
    div[data-testid="stButton"] button span {{
        color: {thm['text_color']} !important;
        white-space: pre-line !important;
        white-space: pre-wrap !important;
        word-break: normal !important;
        text-overflow: clip !important;
        overflow: visible !important;
        font-size: 9.5px !important;
        font-weight: 700 !important;
        line-height: 1.2 !important;
        text-align: center !important;
        margin: 0 !important;
        padding: 0 !important;
    }}

    .stTabs [data-baseweb="tab"] {{
        border-radius: 0px !important;
        font-weight: 700;
        font-size: 11.5px;
        padding: 6px 16px;
        border: 1px solid {thm['card_border']};
        background: {thm['tab_bg']};
        color: {thm['tab_text']};
    }}
    .stTabs [aria-selected="true"] {{
        background: {thm['tab_active_bg']} !important;
        color: {thm['tab_active_text']} !important;
        border-color: {thm['tab_active_bg']} !important;
    }}
    div[data-testid="stMetric"] {{
        border: 1px solid {thm['metric_border']} !important;
        padding: 8px 12px !important;
        background: {thm['metric_bg']} !important;
        border-radius: 0px !important;
    }}
    div[data-testid="stMetricLabel"] {{
        font-size: 11px !important;
        text-transform: uppercase !important;
        font-weight: 700 !important;
        color: {thm['metric_label']} !important;
    }}
    div[data-testid="stMetricValue"] {{
        font-weight: 800 !important;
        color: {thm['metric_val']} !important;
    }}
</style>
"""
render_html(css_styling)

# ---------------------------------------------------------
# DYNAMIC S&P 500 CONSTITUENT SCRAPER
# ---------------------------------------------------------
@st.cache_data(ttl=43200)
def get_live_sp500_sectors():
    url = "https://en.wikipedia.org/wiki/List_of_S%26P_500_companies"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36"
    }
    try:
        resp = requests.get(url, headers=headers, timeout=10)
        tables = pd.read_html(io.StringIO(resp.text))
        df = tables[0]
        df["Symbol"] = df["Symbol"].str.replace(".", "-", regex=False)
        sector_dict = {}
        for sector, group in df.groupby("GICS Sector"):
            sector_dict[sector] = group["Symbol"].tolist()
        return sector_dict
    except Exception:
        return {
            "Information Technology": ["AAPL", "MSFT", "NVDA", "AVGO", "ORCL", "CRM", "AMD", "QCOM", "ADBE", "CSCO", "ACN", "TXN", "INTU", "NOW", "AMAT", "MU", "ADI", "LRCX", "KLAC", "PANW", "SNPS", "CDNS", "MRVL"],
            "Health Care": ["LLY", "UNH", "JNJ", "ABBV", "MRK", "TMO", "ABT", "ISRG", "PFE", "DHR", "BMY", "AMGN", "GILD", "VRTX", "MDT", "SYK", "ELV", "BSX", "CI", "REGN", "BDX", "ZTS"],
            "Financials": ["BRK-B", "JPM", "V", "MA", "BAC", "WFC", "MS", "GS", "SPGI", "BLK", "C", "PGR", "CB", "MMC", "AXP", "SCHW", "AON", "ICE", "MCO", "USB", "PNC", "TRV"],
            "Consumer Discretionary": ["AMZN", "TSLA", "HD", "MCD", "NKE", "LOW", "BKNG", "SBUX", "TJX", "TGT", "LULU", "MAR", "HLT", "ORLY", "AZO", "CMG", "ROST", "YUM", "EBAY", "DRI", "EXPE"],
            "Communication Services": ["GOOGL", "GOOG", "META", "NFLX", "DIS", "TMUS", "VZ", "T", "CMCSA", "CHTR", "WBD", "EA", "TTWO", "OMC", "IPG", "FOXA", "FOX", "NWSA", "NWS", "LYV", "SPOT", "DASH", "PINS", "ROKU"],
            "Industrials": ["GE", "CAT", "RTX", "UNP", "HON", "BA", "DE", "LMT", "UPS", "ETN", "GEV", "WM", "ITW", "GD", "NSC", "CSX", "PH", "EMR", "PCAR", "FDX", "TT", "CARR"],
            "Consumer Staples": ["WMT", "PG", "COST", "KO", "PEP", "PM", "MDLZ", "MO", "CL", "KMB", "GIS", "STZ", "SYY", "ADM", "KDP", "HSY", "KR", "EL", "CAG", "CHD", "MKC"],
            "Energy": ["XOM", "CVX", "COP", "SLB", "EOG", "MPC", "PSX", "VLO", "OXY", "HES", "KMI", "WMB", "BKR", "HAL", "DVN", "OKE", "FANG", "TRGP", "CTRA", "MRO", "EQT"],
            "Real Estate": ["PLD", "AMT", "EQIX", "WELL", "PSA", "SPG", "O", "CCI", "DLR", "VICI", "EXR", "AVB", "EQR", "CBRE", "SBAC", "WY", "IRM", "INVH", "MAA", "ESS", "KIM"],
            "Materials": ["LIN", "SHW", "FCX", "ECL", "APD", "NEM", "CTVA", "DOW", "PPG", "MLM", "VMC", "CF", "FMC", "ALB", "IFF", "PKG", "IP", "BALL", "NUE", "STLD"],
            "Utilities": ["NEE", "SO", "DUK", "CEG", "SRE", "AEP", "PCG", "XEL", "ED", "PEG", "ETR", "WEC", "D", "FE", "PPL", "ES", "AEE", "CMS", "CNP", "DTE", "NI"]
        }

SECTOR_DATASETS = get_live_sp500_sectors()

# ---------------------------------------------------------
# LIVE MOVERS SCREENER
# ---------------------------------------------------------
@st.cache_data(ttl=300)
def rank_live_sector_stocks(sector_tickers, mode="Top Movers Today (Largest % Swings)"):
    if mode == "Standard Index Order" or len(sector_tickers) <= 1:
        return sector_tickers
    try:
        data = yf.download(sector_tickers, period="5d", progress=False, group_by="ticker")
        scored = []
        for t in sector_tickers:
            try:
                sub = data[t] if len(sector_tickers) > 1 else data
                close = sub["Close"].dropna()
                vol = sub["Volume"].dropna()
                if len(close) < 2:
                    continue
                chg = float((close.iloc[-1] - close.iloc[-2]) / close.iloc[-2] * 100)
                v_today = float(vol.iloc[-1]) if len(vol) > 0 else 0
                scored.append({"ticker": t, "abs_chg": abs(chg), "chg": chg, "vol": v_today})
            except Exception:
                continue

        if mode == "Top Movers Today (Largest % Swings)":
            scored = sorted(scored, key=lambda x: x["abs_chg"], reverse=True)
        elif mode == "Top Gainers Today":
            scored = sorted(scored, key=lambda x: x["chg"], reverse=True)
        elif mode == "Top Losers Today":
            scored = sorted(scored, key=lambda x: x["chg"])
        elif mode == "Highest Volume Today":
            scored = sorted(scored, key=lambda x: x["vol"], reverse=True)

        return [s["ticker"] for s in scored]
    except Exception:
        return sector_tickers

# ---------------------------------------------------------
# CACHED DETAILED DATA FETCHER
# ---------------------------------------------------------
@st.cache_data(ttl=300)
def fetch_ticker_data(tickers):
    data_dict = {}
    for t in tickers:
        try:
            ticker = t.strip().upper()
            stock = yf.Ticker(ticker)
            df = stock.history(period="6mo")
            if df.empty or len(df) < 22:
                continue
            
            close = df["Close"].dropna()
            high = df["High"].dropna()
            low = df["Low"].dropna()
            volume = df["Volume"].dropna()

            ema_9 = close.ewm(span=9, adjust=False).mean()
            ema_21 = close.ewm(span=21, adjust=False).mean()

            hist_30 = close.iloc[-22:] if len(close) >= 22 else close
            gain_30 = ((close.iloc[-1] - hist_30.iloc[0]) / hist_30.iloc[0]) * 100

            delta = close.diff()
            gain = delta.clip(lower=0)
            loss = -delta.clip(upper=0)
            avg_gain = gain.ewm(alpha=1/14, min_periods=14, adjust=False).mean()
            avg_loss = loss.ewm(alpha=1/14, min_periods=14, adjust=False).mean()
            rs = avg_gain / avg_loss.replace(0, np.nan)
            rsi_series = 100.0 - (100.0 / (1.0 + rs))
            rsi_14 = float(rsi_series.iloc[-1]) if not pd.isna(rsi_series.iloc[-1]) else None

            if len(close) >= 50:
                sma_50_val = close.rolling(50).mean().iloc[-1]
                sma_50_dist = float(((close.iloc[-1] - sma_50_val) / sma_50_val) * 100) if sma_50_val > 0 else None
            else:
                sma_50_dist = None

            if len(volume) >= 21:
                vol_prior_20 = volume.iloc[-21:-1].mean()
                rvol = float(volume.iloc[-1] / vol_prior_20) if vol_prior_20 > 0 else 1.0
            else:
                rvol = 1.0

            info = stock.info or {}
            market_cap = info.get("marketCap", None)
            pe_ratio = info.get("trailingPE", None)
            fwd_pe = info.get("forwardPE", None)
            peg_ratio = info.get("pegRatio", None)
            beta = info.get("beta", None)
            div_yield = info.get("dividendYield", None)
            if div_yield:
                div_yield = div_yield * 100 if div_yield < 1.0 else div_yield
            short_name = info.get("shortName", ticker)

            clean_spark = [float(p) for p in hist_30.tolist() if not pd.isna(p)]

            data_dict[ticker] = {
                "name": short_name,
                "price": float(close.iloc[-1]),
                "change_dlr": float(close.iloc[-1] - close.iloc[-2]),
                "change_pct": float((close.iloc[-1] - close.iloc[-2]) / close.iloc[-2] * 100),
                "gain_30": float(gain_30),
                "ema_9": float(ema_9.iloc[-1]),
                "ema_21": float(ema_21.iloc[-1]),
                "rsi": rsi_14,
                "sma_50_dist": sma_50_dist,
                "rvol": rvol,
                "day_low": float(low.iloc[-1]),
                "day_high": float(high.iloc[-1]),
                "vol": int(volume.iloc[-1]),
                "market_cap": market_cap,
                "pe_ratio": pe_ratio,
                "fwd_pe": fwd_pe,
                "peg_ratio": peg_ratio,
                "beta": beta,
                "div_yield": div_yield,
                "sparkline": clean_spark,
                "bullish": bool(ema_9.iloc[-1] >= ema_21.iloc[-1])
            }
        except Exception:
            continue
    return data_dict

def make_svg_sparkline(prices, is_positive=True, width=90, height=18):
    if not prices or len(prices) < 2:
        return '<span style="color:#64748B; font-size:10px;">--</span>'
    min_p, max_p = min(prices), max(prices)
    rng = max_p - min_p if max_p != min_p else 1.0
    pts = []
    step = width / (len(prices) - 1)
    for i, p in enumerate(prices):
        x = i * step
        y = height - ((p - min_p) / rng * (height - 4) + 2)
        pts.append(f"{x:.1f},{y:.1f}")
    color = thm["spark_pos"] if is_positive else thm["spark_neg"]
    return f'<svg width="{width}" height="{height}" style="display:block; margin:auto;"><polyline fill="none" stroke="{color}" stroke-width="1.6" points="{" ".join(pts)}"/></svg>'

def fmt_mcap(val):
    if not val or pd.isna(val):
        return "--"
    if val >= 1e12:
        return f"${val / 1e12:.2f}T"
    if val >= 1e9:
        return f"${val / 1e9:.2f}B"
    return f"${val / 1e6:.2f}M"

# ---------------------------------------------------------
# SECTOR REGISTRY & TOP RIBBON
# ---------------------------------------------------------
SECTOR_MAP = {
    "XLK": ("Information Technology", "TECH"),
    "XLV": ("Health Care", "HLTH"),
    "XLF": ("Financials", "FINC"),
    "XLY": ("Consumer Discretionary", "COND"),
    "XLC": ("Communication Services", "COMM"),
    "XLI": ("Industrials", "INDU"),
    "XLP": ("Consumer Staples", "CONS"),
    "XLE": ("Energy", "ENGY"),
    "XLU": ("Utilities", "UTIL"),
    "XLRE": ("Real Estate", "REAL"),
    "XLB": ("Materials", "MATR")
}

BENCHMARKS_EXTRA = [
    ("SPY", "S&P"),
    ("QQQ", "NDX"),
    ("DIA", "DOW")
]

ALL_BENCH_TICKERS = list(SECTOR_MAP.keys()) + [b[0] for b in BENCHMARKS_EXTRA]
bench_data = fetch_ticker_data(ALL_BENCH_TICKERS)
spy_gain_30 = bench_data.get("SPY", {}).get("gain_30", 0.0)

st.markdown("#### >> MARKET OVERVIEW")

cols = st.columns(len(ALL_BENCH_TICKERS))
for i, ticker in enumerate(ALL_BENCH_TICKERS):
    with cols[i]:
        if ticker in SECTOR_MAP:
            sec_name, label = SECTOR_MAP[ticker]
            is_clickable_sector = True
        else:
            sec_name = None
            label = next(b[1] for b in BENCHMARKS_EXTRA if b[0] == ticker)
            is_clickable_sector = False
            
        if ticker in bench_data:
            d = bench_data[ticker]
            sign = "+" if d["change_pct"] >= 0 else ""
            btn_text = f"{label}  \n{ticker} {sign}{d['change_pct']:.1f}%"
        else:
            btn_text = f"{label}  \n{ticker} --"
            
        if st.button(btn_text, key=f"bench_btn_{ticker}", use_container_width=True):
            if is_clickable_sector:
                st.session_state.selected_sector = sec_name
                st.rerun()

st.markdown("<div style='height:4px;'></div>", unsafe_allow_html=True)

# ---------------------------------------------------------
# TABS SETUP
# ---------------------------------------------------------
tab_portfolio, tab_sector, tab_scatter, tab_rankings, tab_commodities, tab_glossary = st.tabs([
    "PORTFOLIO POSITIONS",
    "SECTOR INTELLIGENCE",
    "MOMENTUM SCATTER MATRIX",
    "COMPOSITE FACTOR RANKINGS",
    "COMMODITIES & DERIVATIVES",
    "TERMINAL GLOSSARY"
])

# ---------------------------------------------------------
# PORTFOLIO LOADER
# ---------------------------------------------------------
@st.cache_data(ttl=60)
def load_portfolio_holdings():
    import glob
    csv_files = glob.glob("Portfolio_Positions*.csv")
    if not csv_files:
        return []
    try:
        df = pd.read_csv(csv_files[0], on_bad_lines='skip')
    except Exception:
        return []
        
    df.columns = [str(c).strip().lower() for c in df.columns]
    symbol_col = next((c for c in df.columns if "symbol" in c), None)
    qty_col = next((c for c in df.columns if "quantity" in c or "qty" in c or "shares" in c), None)
    avg_cost_col = next((c for c in df.columns if "average cost" in c or "avg cost" in c), None)
    total_cost_col = next((c for c in df.columns if "cost basis total" in c or "total cost" in c), None)

    if not symbol_col:
        return []

    holdings = []
    for _, row in df.iterrows():
        symbol = str(row.get(symbol_col, "")).strip().upper()
        if not symbol or symbol in ["NAN", "NONE", ""] or any(
            symbol.startswith(prefix) for prefix in ["PENDING", "THE DATA", "BROKERAGE", "DATE", "ACCOUNT"]
        ):
            continue
        if "**" in symbol or symbol in ["SPAXX", "FDRXX", "FCASH"]:
            continue
        try:
            qty_raw = str(row.get(qty_col, 0)).replace(",", "").strip() if qty_col else "0"
            qty = float(qty_raw) if qty_raw not in ["nan", "None", "--", "n/a", ""] else 0.0
            if qty <= 0:
                continue

            cost = 0.0
            if avg_cost_col:
                cost_raw = str(row.get(avg_cost_col, "0")).replace("$", "").replace(",", "").strip()
                if cost_raw not in ["nan", "None", "--", "n/a", "", "null"]:
                    cost = float(cost_raw)
            elif total_cost_col:
                tot_raw = str(row.get(total_cost_col, "0")).replace("$", "").replace(",", "").strip()
                if tot_raw not in ["nan", "None", "--", "n/a", "", "null"]:
                    cost = float(tot_raw) / qty

            holdings.append({"ticker": symbol, "shares": qty, "cost": cost})
        except Exception:
            continue
            
    agg_holdings = {}
    for h in holdings:
        t = h["ticker"]
        if t not in agg_holdings:
            agg_holdings[t] = {"ticker": t, "shares": h["shares"], "total_cost": h["shares"] * h["cost"]}
        else:
            agg_holdings[t]["shares"] += h["shares"]
            agg_holdings[t]["total_cost"] += h["shares"] * h["cost"]
            
    result = []
    for t, item in agg_holdings.items():
        avg_c = item["total_cost"] / item["shares"] if item["shares"] > 0 else 0.0
        result.append({"ticker": t, "shares": round(item["shares"], 4), "cost": avg_c})
    return result

# ---------------------------------------------------------
# TAB 1: PORTFOLIO
# ---------------------------------------------------------
with tab_portfolio:
    st.markdown("<div class='section-banner'>PORTFOLIO AUDIT // REAL-TIME PERFORMANCE</div>", unsafe_allow_html=True)
    portfolio_holdings = load_portfolio_holdings()
    
    if not portfolio_holdings:
        portfolio_holdings = [
            {"ticker": "NVDA", "shares": 50, "cost": 115.50},
            {"ticker": "AAPL", "shares": 30, "cost": 175.00},
            {"ticker": "MSFT", "shares": 20, "cost": 410.00}
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
            
            position_daily_gain_dlr = d["change_dlr"] * shares
            total_daily_gain_dlr += position_daily_gain_dlr
            
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
                "daily_pct": d["change_pct"],
                "overall_dlr": overall_gain_dlr,
                "overall_pct": overall_gain_pct,
                "bullish": d["bullish"],
                "sparkline": d["sparkline"]
            })
    
    if port_rows:
        total_overall_gain_dlr = total_market_value - total_cost_basis
        total_overall_gain_pct = (total_overall_gain_dlr / total_cost_basis) * 100 if total_cost_basis > 0 else 0.0
        prev_close_val = total_market_value - total_daily_gain_dlr
        total_daily_pct = (total_daily_gain_dlr / prev_close_val) * 100 if prev_close_val > 0 else 0.0
        
        k1, k2, k3, k4 = st.columns(4)
        k1.metric("PORTFOLIO VALUE", f"${total_market_value:,.2f}")
        k2.metric("DAILY GAIN/LOSS", f"${total_daily_gain_dlr:+,.2f}", f"{total_daily_pct:+.2f}%")
        k3.metric("TOTAL UNREALIZED", f"${total_overall_gain_dlr:+,.2f}", f"{total_overall_gain_pct:+.2f}%")
        k4.metric("TOTAL COST BASIS", f"${total_cost_basis:,.2f}")
        
        st.markdown("<div style='height:8px;'></div>", unsafe_allow_html=True)
        port_rows = sorted(port_rows, key=lambda x: x["mval"], reverse=True)
        
        port_html = f"""
        <div style="overflow-x: auto; margin-bottom: 20px;">
        <table id="portfolio-table" class="sheet-table">
            <thead>
                <tr>
                    <th class="sortable-th" onclick="sortPortfolioTable(0, 'str')">TICKER <span class="arrow"></span></th>
                    <th class="sortable-th" onclick="sortPortfolioTable(1, 'str')">ASSET NAME <span class="arrow"></span></th>
                    <th class="sortable-th" onclick="sortPortfolioTable(2, 'num')">SHARES <span class="arrow"></span></th>
                    <th class="sortable-th" onclick="sortPortfolioTable(3, 'num')">AVG COST <span class="arrow"></span></th>
                    <th class="sortable-th" onclick="sortPortfolioTable(4, 'num')">MARK PRICE <span class="arrow"></span></th>
                    <th class="sortable-th" onclick="sortPortfolioTable(5, 'num')">MARKET VALUE <span class="arrow">▼</span></th>
                    <th class="sortable-th" onclick="sortPortfolioTable(6, 'num')">TODAY ($) <span class="arrow"></span></th>
                    <th class="sortable-th" onclick="sortPortfolioTable(7, 'num')">TODAY (%) <span class="arrow"></span></th>
                    <th class="sortable-th" onclick="sortPortfolioTable(8, 'num')">UNREALIZED ($) <span class="arrow"></span></th>
                    <th class="sortable-th" onclick="sortPortfolioTable(9, 'num')">UNREALIZED (%) <span class="arrow"></span></th>
                    <th style="text-align:center;">SIGNAL</th>
                    <th style="text-align:center;">30D TREND</th>
                </tr>
            </thead>
            <tbody>
        """
        for r in port_rows:
            c_daily = "pos-cell" if r["daily_dlr"] >= 0 else "neg-cell"
            c_overall = "pos-cell" if r["overall_dlr"] >= 0 else "neg-cell"
            s_daily_dlr = "+" if r["daily_dlr"] >= 0 else ""
            s_daily_pct = "+" if r["daily_pct"] >= 0 else ""
            s_overall_dlr = "+" if r["overall_dlr"] >= 0 else ""
            s_overall_pct = "+" if r["overall_pct"] >= 0 else ""
            cue = '<span class="bullish-badge">BULL</span>' if r["bullish"] else '<span class="bearish-badge">BEAR</span>'
            spark = make_svg_sparkline(r["sparkline"], is_positive=(r["overall_dlr"] >= 0))
            
            port_html += f"""
            <tr>
                <td style="font-weight:700;" data-val="{r['ticker']}">{r['ticker']}</td>
                <td data-val="{r['name']}">{r['name']}</td>
                <td data-val="{r['shares']}">{r['shares']:,}</td>
                <td data-val="{r['cost']}">$ {r['cost']:.2f}</td>
                <td data-val="{r['price']}">$ {r['price']:.2f}</td>
                <td data-val="{r['mval']}">$ {r['mval']:,.2f}</td>
                <td class="{c_daily}" data-val="{r['daily_dlr']}">{s_daily_dlr}$ {r['daily_dlr']:,.2f}</td>
                <td class="{c_daily}" data-val="{r['daily_pct']}">{s_daily_pct}{r['daily_pct']:.2f}%</td>
                <td class="{c_overall}" data-val="{r['overall_dlr']}">{s_overall_dlr}$ {r['overall_dlr']:,.2f}</td>
                <td class="{c_overall}" data-val="{r['overall_pct']}">{s_overall_pct}{r['overall_pct']:.2f}%</td>
                <td style="text-align:center;">{cue}</td>
                <td style="text-align:center;">{spark}</td>
            </tr>
            """
        port_html += """
            </tbody>
        </table>
        </div>
        <script>
        function sortPortfolioTable(colIdx, type) {
            const table = document.getElementById("portfolio-table");
            if (!table) return;
            const tbody = table.querySelector("tbody");
            const rows = Array.from(tbody.querySelectorAll("tr"));
            const th = table.querySelectorAll("th")[colIdx];
            const isAsc = th.getAttribute("data-sort") === "asc";
            const dir = isAsc ? -1 : 1;
            table.querySelectorAll("th .arrow").forEach(el => el.textContent = "");
            th.querySelector(".arrow").textContent = isAsc ? " ▼" : " ▲";
            th.setAttribute("data-sort", isAsc ? "desc" : "asc");
            rows.sort((a, b) => {
                const cellA = a.children[colIdx].getAttribute("data-val");
                const cellB = b.children[colIdx].getAttribute("data-val");
                if (type === 'num') {
                    return ((parseFloat(cellA) || 0) - (parseFloat(cellB) || 0)) * dir;
                } else {
                    return cellA.localeCompare(cellB) * dir;
                }
            });
            rows.forEach(r => tbody.appendChild(r));
        }
        </script>
        """
        render_html(port_html)
    else:
        st.info("NO PORTFOLIO POSITIONS AVAILABLE.")

# ---------------------------------------------------------
# TAB 2: SECTOR EXPLORER
# ---------------------------------------------------------
with tab_sector:
    col_sel, col_tgl_f, col_tgl_t = st.columns([1.5, 1, 1.2])
    with col_sel:
        sector_list = list(SECTOR_DATASETS.keys())
        default_idx = sector_list.index(st.session_state.selected_sector) if st.session_state.selected_sector in sector_list else 0
        selected_sector = st.selectbox("SELECT SECTOR BENCHMARK", sector_list, index=default_idx)
        st.session_state.selected_sector = selected_sector
        
    with col_tgl_f:
        st.markdown("<div style='height:28px;'></div>", unsafe_allow_html=True)
        show_fundamentals = st.toggle("Fundamentals (P/E, Fwd P/E, PEG, Beta, Div %)", value=False)
        
    with col_tgl_t:
        st.markdown("<div style='height:28px;'></div>", unsafe_allow_html=True)
        show_technicals = st.toggle("Advanced Technicals (14D RSI, 50D Spread, RVOL, RS vs SPY)", value=False)

    sector_tickers = SECTOR_DATASETS[selected_sector][:25]
    sec_data = fetch_ticker_data(sector_tickers)

    rows = []
    for t in sector_tickers:
        if t in sec_data:
            d = sec_data[t]
            rs_spy = round(d["gain_30"] - spy_gain_30, 2)
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
                "pe": f"{d['pe_ratio']:.1f}" if d["pe_ratio"] else "--",
                "fwd_pe": f"{d['fwd_pe']:.1f}" if d["fwd_pe"] else "--",
                "peg": f"{d['peg_ratio']:.2f}" if d["peg_ratio"] else "--",
                "beta": f"{d['beta']:.2f}" if d["beta"] else "--",
                "div": f"{d['div_yield']:.2f}%" if d["div_yield"] else "--",
                "rsi": d["rsi"],
                "sma_50_dist": d["sma_50_dist"],
                "rvol": d["rvol"],
                "rs_spy": rs_spy,
                "bullish": d["bullish"],
                "sparkline": d["sparkline"]
            })

    if rows:
        col_l, col_r = st.columns(2)

        def build_extra_th():
            html = ""
            if show_fundamentals:
                html += '<th>FWD P/E</th><th>PEG</th><th>BETA</th><th>DIV %</th>'
            if show_technicals:
                html += '<th>14D RSI</th><th>50D SPREAD</th><th>RVOL</th><th>RS vs SPY</th>'
            return html

        def build_extra_td(r):
            html = ""
            if show_fundamentals:
                html += f'<td>{r["fwd_pe"]}</td><td>{r["peg"]}</td><td>{r["beta"]}</td><td>{r["div"]}</td>'
            if show_technicals:
                rsi_val = f'{r["rsi"]:.1f}' if r["rsi"] is not None else '--'
                c_rsi = 'neg-cell' if (r["rsi"] and r["rsi"] >= 70) else ('pos-cell' if (r["rsi"] and r["rsi"] <= 30) else '')
                if r["sma_50_dist"] is not None:
                    c_50 = "pos-cell" if r["sma_50_dist"] >= 0 else "neg-cell"
                    s_50 = "+" if r["sma_50_dist"] >= 0 else ""
                    v_50 = f'{s_50}{r["sma_50_dist"]:.1f}%'
                else:
                    c_50, v_50 = "", "--"
                rvol_val = f'{r["rvol"]:.2f}x' if r["rvol"] is not None else '--'
                c_rvol = 'pos-cell' if (r["rvol"] and r["rvol"] >= 1.5) else ''
                c_rs = "pos-cell" if r["rs_spy"] >= 0 else "neg-cell"
                s_rs = "+" if r["rs_spy"] >= 0 else ""
                v_rs = f'{s_rs}{r["rs_spy"]:.1f}%'
                html += f'<td class="{c_rsi}">{rsi_val}</td><td class="{c_50}">{v_50}</td><td class="{c_rvol}">{rvol_val}</td><td class="{c_rs}">{v_rs}</td>'
            return html

        with col_l:
            sorted_mcap = sorted(rows, key=lambda x: (x["mcap"] or 0), reverse=True)[:20]
            tbl_html = '<div style="overflow-x: auto; margin-bottom: 20px;">'
            tbl_html += f'<div class="section-banner">MARKET CAP CONSTITUENTS [TOP {len(sorted_mcap)}]</div>'
            tbl_html += f'<table class="sheet-table"><thead><tr><th>TICKER</th><th>ASSET NAME</th><th>PRICE</th><th>TODAY ($)</th><th>TODAY (%)</th><th>30D (%)</th><th>CAP</th><th>P/E</th>{build_extra_th()}<th>SIGNAL</th><th style="text-align:center;">30D TREND</th></tr></thead><tbody>'
            for r in sorted_mcap:
                c_dlr = "pos-cell" if r["chg_dlr"] >= 0 else "neg-cell"
                c_pct = "pos-cell" if r["chg_pct"] >= 0 else "neg-cell"
                c_30 = "pos-cell" if r["gain_30"] >= 0 else "neg-cell"
                s_dlr = "+" if r["chg_dlr"] >= 0 else ""
                s_pct = "+" if r["chg_pct"] >= 0 else ""
                s_30 = "+" if r["gain_30"] >= 0 else ""
                cue = '<span class="bullish-badge">BULL</span>' if r["bullish"] else '<span class="bearish-badge">BEAR</span>'
                spark = make_svg_sparkline(r["sparkline"], is_positive=(r["gain_30"] >= 0))
                tbl_html += f'<tr><td style="font-weight:700;">{r["ticker"]}</td><td style="max-width:110px; overflow:hidden; text-overflow:ellipsis;">{r["name"]}</td><td>${r["price"]:.2f}</td><td class="{c_dlr}">{s_dlr}${r["chg_dlr"]:.2f}</td><td class="{c_pct}">{s_pct}{r["chg_pct"]:.2f}%</td><td class="{c_30}">{s_30}{r["gain_30"]:.2f}%</td><td>{r["mcap_fmt"]}</td><td>{r["pe"]}</td>{build_extra_td(r)}<td style="text-align:center;">{cue}</td><td style="text-align:center;">{spark}</td></tr>'
            tbl_html += '</tbody></table></div>'
            render_html(tbl_html)

        with col_r:
            sorted_mom = sorted(rows, key=lambda x: x["gain_30"], reverse=True)[:10]
            tbl_html2 = '<div style="overflow-x: auto; margin-bottom: 20px;">'
            tbl_html2 += '<div class="section-banner">RELATIVE STRENGTH // TOP 10 (30-DAY GAINERS)</div>'
            tbl_html2 += f'<table class="sheet-table"><thead><tr><th>TICKER</th><th>ASSET NAME</th><th>PRICE</th><th>30D (%)</th><th>TODAY (%)</th><th>CAP</th><th>P/E</th>{build_extra_th()}<th>SIGNAL</th><th style="text-align:center;">30D TREND</th></tr></thead><tbody>'
            for r in sorted_mom:
                c_pct = "pos-cell" if r["chg_pct"] >= 0 else "neg-cell"
                c_30 = "pos-cell" if r["gain_30"] >= 0 else "neg-cell"
                s_pct = "+" if r["chg_pct"] >= 0 else ""
                s_30 = "+" if r["gain_30"] >= 0 else ""
                cue = '<span class="bullish-badge">BULL</span>' if r["bullish"] else '<span class="bearish-badge">BEAR</span>'
                spark = make_svg_sparkline(r["sparkline"], is_positive=(r["gain_30"] >= 0))
                tbl_html2 += f'<tr><td style="font-weight:700;">{r["ticker"]}</td><td style="max-width:120px; overflow:hidden; text-overflow:ellipsis;">{r["name"]}</td><td>${r["price"]:.2f}</td><td class="{c_30}">{s_30}{r["gain_30"]:.2f}%</td><td class="{c_pct}">{s_pct}{r["chg_pct"]:.2f}%</td><td>{r["mcap_fmt"]}</td><td>{r["pe"]}</td>{build_extra_td(r)}<td style="text-align:center;">{cue}</td><td style="text-align:center;">{spark}</td></tr>'
            tbl_html2 += '</tbody></table></div>'
            render_html(tbl_html2)

# ---------------------------------------------------------
# TAB 3: DYNAMIC LIVE MOMENTUM SCATTER MATRIX
# ---------------------------------------------------------
METRIC_REGISTRY = {
    "Daily Gain (%) (Today's percentage price change)": "Daily Gain (%)",
    "30D Gain (%) (Trailing 22-session momentum return)": "30D Gain (%)",
    "RS vs SPY Alpha (%) (Compares stock return directly against SPY)": "RS vs SPY Alpha (%)",
    "14D RSI (Momentum oscillator: >70 overbought, <30 oversold)": "14D RSI",
    "50D SMA Spread (%) (% distance above/below 50-day moving average)": "50D SMA Spread (%)",
    "RVOL (Today's volume vs 20-day average; >1.5x is heavy)": "RVOL (Volume Multiplier)",
    "Forward P/E (Price-to-earnings based on next 12M expected EPS)": "Forward P/E",
    "Trailing P/E (Price-to-earnings based on past 12M actual net earnings)": "Trailing P/E",
    "PEG Ratio (P/E divided by growth rate; <1.0 is undervalued)": "PEG Ratio",
    "Beta (Market volatility sensitivity; S&P 500 = 1.0)": "Beta (Risk)",
    "Market Cap (Total corporate equity valuation size)": "Market Cap",
    "Dividend Yield (%) (Annual cash dividend divided by share price)": "Dividend Yield (%)"
}

with tab_scatter:
    st.markdown("<div class='section-banner'>LIVE MARKET MATRIX // DYNAMIC CONSTITUENT EXPLORER</div>", unsafe_allow_html=True)
    
    r1_col1, r1_col2, r1_col3, r1_col4 = st.columns([1.2, 1.3, 1, 1.2])
    with r1_col1:
        scatter_sector = st.selectbox(
            "SELECT SECTOR FOR MATRIX", 
            list(SECTOR_DATASETS.keys()), 
            index=list(SECTOR_DATASETS.keys()).index(st.session_state.selected_sector)
        )
    with r1_col2:
        screener_mode = st.selectbox(
            "LIVE MARKET SCREENER (DAILY RANKING)",
            [
                "Top Movers Today (Largest % Swings)",
                "Top Gainers Today",
                "Top Losers Today",
                "Highest Volume Today",
                "Standard Index Order"
            ],
            index=0
        )
    with r1_col3:
        stock_count = st.select_slider(
            "STOCKS TO DISPLAY",
            options=[5, 10, 15, 20, 25, 30, 40, 50],
            value=40
        )
    with r1_col4:
        custom_input = st.text_input("ADD CUSTOM TICKERS (COMMA-SEPARATED)", placeholder="e.g. PLTR, SMCI, TSM")

    r2_col1, r2_col2, r2_col3, r2_col4 = st.columns(4)

    x_opts = [
        "30D Gain (%) (Trailing 22-session momentum return)",
        "RS vs SPY Alpha (%) (Compares stock return directly against SPY)",
        "50D SMA Spread (%) (% distance above/below 50-day moving average)",
        "14D RSI (Momentum oscillator: >70 overbought, <30 oversold)"
    ]
    with r2_col1:
        x_label = st.selectbox("X-AXIS (MOMENTUM)", x_opts, index=0)
        x_col = METRIC_REGISTRY[x_label]

    y_opts = [
        "Daily Gain (%) (Today's percentage price change)",
        "14D RSI (Momentum oscillator: >70 overbought, <30 oversold)",
        "50D SMA Spread (%) (% distance above/below 50-day moving average)",
        "RVOL (Today's volume vs 20-day average; >1.5x is heavy)"
    ]
    with r2_col2:
        y_label = st.selectbox("Y-AXIS (VELOCITY)", y_opts, index=0)
        y_col = METRIC_REGISTRY[y_label]

    color_opts = [
        "Daily Gain (%) (Today's percentage price change)",
        "RS vs SPY Alpha (%) (Compares stock return directly against SPY)",
        "14D RSI (Momentum oscillator: >70 overbought, <30 oversold)",
        "50D SMA Spread (%) (% distance above/below 50-day moving average)",
        "RVOL (Today's volume vs 20-day average; >1.5x is heavy)",
        "Forward P/E (Price-to-earnings based on next 12M expected EPS)",
        "Trailing P/E (Price-to-earnings based on past 12M actual net earnings)",
        "PEG Ratio (P/E divided by growth rate; <1.0 is undervalued)",
        "Beta (Market volatility sensitivity; S&P 500 = 1.0)"
    ]
    with r2_col3:
        color_label = st.selectbox("COLOR DIMENSION", color_opts, index=0)
        color_col = METRIC_REGISTRY[color_label]

    size_opts = [
        "Market Cap (Total corporate equity valuation size)",
        "RVOL (Today's volume vs 20-day average; >1.5x is heavy)",
        "Dividend Yield (%) (Annual cash dividend divided by share price)"
    ]
    with r2_col4:
        size_label = st.selectbox("BUBBLE SIZE", size_opts, index=0)
        size_col = METRIC_REGISTRY[size_label]

    all_sector_tickers = SECTOR_DATASETS[scatter_sector]
    ranked_tickers = rank_live_sector_stocks(all_sector_tickers, mode=screener_mode)
    selected_matrix_tickers = ranked_tickers[:int(stock_count)]

    if custom_input:
        extra_tickers = [t.strip().upper() for t in custom_input.split(",") if t.strip()]
        active_matrix_tickers = list(dict.fromkeys(selected_matrix_tickers + extra_tickers))
    else:
        active_matrix_tickers = selected_matrix_tickers

    matrix_data = fetch_ticker_data(active_matrix_tickers)

    plot_rows = []
    for t in active_matrix_tickers:
        if t in matrix_data:
            d = matrix_data[t]
            plot_rows.append({
                "Ticker": t,
                "Name": d["name"],
                "30D Gain (%)": round(d["gain_30"], 2),
                "Daily Gain (%)": round(d["change_pct"], 2),
                "14D RSI": round(d["rsi"], 1) if d["rsi"] is not None else None,
                "50D SMA Spread (%)": round(d["sma_50_dist"], 2) if d["sma_50_dist"] is not None else None,
                "RVOL (Volume Multiplier)": round(d["rvol"], 2) if d["rvol"] is not None else 1.0,
                "RS vs SPY Alpha (%)": round(d["gain_30"] - spy_gain_30, 2),
                "Trailing P/E": round(d["pe_ratio"], 1) if d["pe_ratio"] else None,
                "Forward P/E": round(d["fwd_pe"], 1) if d["fwd_pe"] else None,
                "PEG Ratio": round(d["peg_ratio"], 2) if d["peg_ratio"] else None,
                "Beta (Risk)": round(d["beta"], 2) if d["beta"] else None,
                "Dividend Yield (%)": round(d["div_yield"], 2) if d["div_yield"] else 0.1,
                "Price": f"${d['price']:.2f}",
                "Market Cap": d["market_cap"] if (d["market_cap"] and not pd.isna(d["market_cap"])) else 1e9,
                "Cap Label": fmt_mcap(d["market_cap"])
            })

    if plot_rows:
        df_plot = pd.DataFrame(plot_rows)

        if color_col in ["Daily Gain (%)", "50D SMA Spread (%)", "RS vs SPY Alpha (%)"]:
            color_scale = [thm["spark_neg"], "#64748B", thm["spark_pos"]]
            c_mid = 0.0
        elif color_col == "14D RSI":
            color_scale = ["#3B82F6", thm["spark_pos"], "#F59E0B", thm["spark_neg"]]
            c_mid = 50.0
        elif "P/E" in color_col or "PEG" in color_col:
            color_scale = [thm["spark_pos"], "#F59E0B", thm["spark_neg"]]
            c_mid = None
        else:
            color_scale = ["#1E293B", "#3B82F6", "#EF4444"]
            c_mid = 1.0

        fig = px.scatter(
            df_plot,
            x=x_col,
            y=y_col,
            text="Ticker",
            size=size_col,
            size_max=30,
            color=color_col,
            color_continuous_scale=color_scale,
            color_continuous_midpoint=c_mid,
            hover_name="Name",
            hover_data={
                "Ticker": False,
                "Price": True,
                "30D Gain (%)": ":.2f",
                "Daily Gain (%)": ":.2f",
                "14D RSI": True,
                "50D SMA Spread (%)": True,
                "RS vs SPY Alpha (%)": True,
                "Trailing P/E": True,
                "Forward P/E": True,
                "PEG Ratio": True,
                "Beta (Risk)": True,
                "Cap Label": True,
                size_col: False
            }
        )

        ref_x = 50.0 if x_col == "14D RSI" else 0.0
        ref_y = 50.0 if y_col == "14D RSI" else (1.0 if "RVOL" in y_col else 0.0)
        fig.add_hline(y=ref_y, line_dash="dash", line_color=thm["plotly_line"], line_width=1.2)
        fig.add_vline(x=ref_x, line_dash="dash", line_color=thm["plotly_line"], line_width=1.2)

        fig.update_traces(
            textposition="top center",
            textfont=dict(family="Inter, Segoe UI, sans-serif", size=11, color=thm["text_color"]),
            marker=dict(line=dict(width=1.2, color=thm["card_border"]), opacity=0.9)
        )

        fig.update_layout(
            height=600,
            margin=dict(l=40, r=40, t=30, b=40),
            plot_bgcolor=thm["plotly_plot_bg"],
            paper_bgcolor=thm["plotly_paper_bg"],
            font=dict(family="Inter, Segoe UI, sans-serif", size=11, color=thm["text_color"]),
            xaxis=dict(
                title=dict(text=f"<b>{x_col.upper()}</b>", font=dict(size=12, color=thm["text_color"])),
                gridcolor=thm["plotly_grid"],
                zeroline=False,
                tickfont=dict(color=thm["text_color"])
            ),
            yaxis=dict(
                title=dict(text=f"<b>{y_col.upper()}</b>", font=dict(size=12, color=thm["text_color"])),
                gridcolor=thm["plotly_grid"],
                zeroline=False,
                tickfont=dict(color=thm["text_color"])
            )
        )

        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("NO DATA AVAILABLE FOR SELECTED MATRIX.")

# ---------------------------------------------------------
# TAB 4: COMPOSITE FACTOR RANKING LEADERBOARD (NEW)
# ---------------------------------------------------------
with tab_rankings:
    st.markdown("<div class='section-banner'>MULTI-FACTOR COMPOSITE LEADERBOARD // QUANTITATIVE FACTOR SCORING</div>", unsafe_allow_html=True)
    st.markdown(
        f"<p style='font-size:11.5px; color:{thm['card_border']}; margin-top:4px; margin-bottom:12px;'>"
        f"Each constituent is ranked from 1 to N across 6 metrics (30D Momentum, RS vs SPY Alpha, RVOL, 14D RSI, Forward P/E, PEG Ratio). "
        f"<b>Lowest Average Score = #1 Ranked Stock</b> (Rank 1.0 is the best possible score)."
        f"</p>",
        unsafe_allow_html=True
    )

    rk_col1, rk_col2, rk_col3 = st.columns([1.5, 1.2, 1.2])
    with rk_col1:
        rank_sector = st.selectbox(
            "SELECT SECTOR FOR RANKINGS",
            list(SECTOR_DATASETS.keys()),
            index=list(SECTOR_DATASETS.keys()).index(st.session_state.selected_sector),
            key="rank_sector_sel"
        )
    with rk_col2:
        rank_stock_count = st.select_slider(
            "STOCKS TO EVALUATE",
            options=[10, 20, 30, 40, 50],
            value=40,
            key="rank_count_slider"
        )
    with rk_col3:
        rank_custom_input = st.text_input(
            "ADD CUSTOM TICKERS TO POOL",
            placeholder="e.g. PLTR, SMCI, TSM",
            key="rank_custom_txt"
        )

    all_rank_tickers = SECTOR_DATASETS[rank_sector][:int(rank_stock_count)]
    if rank_custom_input:
        extras = [t.strip().upper() for t in rank_custom_input.split(",") if t.strip()]
        eval_tickers = list(dict.fromkeys(all_rank_tickers + extras))
    else:
        eval_tickers = all_rank_tickers

    eval_data = fetch_ticker_data(eval_tickers)

    rank_raw = []
    for t in eval_tickers:
        if t in eval_data:
            d = eval_data[t]
            rs_spy = d["gain_30"] - spy_gain_30
            rank_raw.append({
                "ticker": t,
                "name": d["name"],
                "price": d["price"],
                "gain_30": d["gain_30"],
                "rs_spy": rs_spy,
                "rvol": d["rvol"] if d["rvol"] else 1.0,
                "rsi": d["rsi"] if d["rsi"] else 50.0,
                "fwd_pe": d["fwd_pe"] if (d["fwd_pe"] and d["fwd_pe"] > 0) else 9999.0,
                "fwd_pe_disp": f"{d['fwd_pe']:.1f}" if (d["fwd_pe"] and d["fwd_pe"] > 0) else "--",
                "peg": d["peg_ratio"] if (d["peg_ratio"] and d["peg_ratio"] > 0) else 999.0,
                "peg_disp": f"{d['peg_ratio']:.2f}" if (d["peg_ratio"] and d["peg_ratio"] > 0) else "--",
                "mcap_fmt": fmt_mcap(d["market_cap"]),
                "bullish": d["bullish"],
                "sparkline": d["sparkline"]
            })

    if rank_raw:
        df_rank = pd.DataFrame(rank_raw)
        
        # Calculate quantitative ranks (1 = best)
        df_rank["r_mom"] = df_rank["gain_30"].rank(ascending=False, method="min").astype(int)
        df_rank["r_alpha"] = df_rank["rs_spy"].rank(ascending=False, method="min").astype(int)
        df_rank["r_rvol"] = df_rank["rvol"].rank(ascending=False, method="min").astype(int)
        df_rank["r_rsi"] = df_rank["rsi"].rank(ascending=False, method="min").astype(int)
        df_rank["r_val"] = df_rank["fwd_pe"].rank(ascending=True, method="min").astype(int)
        df_rank["r_peg"] = df_rank["peg"].rank(ascending=True, method="min").astype(int)

        # Composite score = average rank across the 6 factors
        rank_cols = ["r_mom", "r_alpha", "r_rvol", "r_rsi", "r_val", "r_peg"]
        df_rank["composite_score"] = df_rank[rank_cols].mean(axis=1)
        df_rank = df_rank.sort_values(by="composite_score", ascending=True).reset_index(drop=True)
        df_rank["final_rank"] = df_rank.index + 1

        # Summary KPI Cards for Top 3
        top_cols = st.columns(3)
        for idx in range(min(3, len(df_rank))):
            with top_cols[idx]:
                leader = df_rank.iloc[idx]
                st.metric(
                    label=f"RANK #{leader['final_rank']} LEADER // {leader['ticker']}",
                    value=f"Score: {leader['composite_score']:.1f}",
                    delta=f"{leader['gain_30']:+.1f}% 30D | RVOL {leader['rvol']:.2f}x"
                )

        st.markdown("<div style='height:12px;'></div>", unsafe_allow_html=True)

        # Leaderboard Table HTML
        rk_html = f"""
        <div style="overflow-x: auto; margin-bottom: 20px;">
        <table class="sheet-table">
            <thead>
                <tr>
                    <th style="text-align:center;">RANK</th>
                    <th>TICKER</th>
                    <th>ASSET NAME</th>
                    <th style="text-align:center; background-color:{thm['banner_bg']}; color:{thm['banner_text']};">AVG SCORE</th>
                    <th>PRICE</th>
                    <th>30D MOM (RNK)</th>
                    <th>RS ALPHA (RNK)</th>
                    <th>RVOL (RNK)</th>
                    <th>14D RSI (RNK)</th>
                    <th>FWD P/E (RNK)</th>
                    <th>PEG (RNK)</th>
                    <th>MKT CAP</th>
                    <th style="text-align:center;">30D TREND</th>
                </tr>
            </thead>
            <tbody>
        """
        for _, row in df_rank.iterrows():
            c_mom = "pos-cell" if row["gain_30"] >= 0 else "neg-cell"
            c_alpha = "pos-cell" if row["rs_spy"] >= 0 else "neg-cell"
            c_score = "pos-cell" if row["final_rank"] <= (len(df_rank) // 3) else ""
            spark = make_svg_sparkline(row["sparkline"], is_positive=(row["gain_30"] >= 0))
            badge_color = thm["badge_bull_bg"] if row["final_rank"] <= 3 else thm["card_bg"]
            badge_text = "#FFFFFF" if row["final_rank"] <= 3 else thm["text_color"]

            rk_html += f"""
            <tr>
                <td style="text-align:center; font-weight:800; background-color:{badge_color}; color:{badge_text};">#{row['final_rank']}</td>
                <td style="font-weight:700;">{row['ticker']}</td>
                <td style="max-width:120px; overflow:hidden; text-overflow:ellipsis;">{row['name']}</td>
                <td class="{c_score}" style="text-align:center; font-weight:800; font-size:12.5px;">{row['composite_score']:.1f}</td>
                <td>${row['price']:.2f}</td>
                <td class="{c_mom}">{row['gain_30']:+.1f}% (#{row['r_mom']})</td>
                <td class="{c_alpha}">{row['rs_spy']:+.1f}% (#{row['r_alpha']})</td>
                <td>{row['rvol']:.2f}x (#{row['r_rvol']})</td>
                <td>{row['rsi']:.1f} (#{row['r_rsi']})</td>
                <td>{row['fwd_pe_disp']} (#{row['r_val']})</td>
                <td>{row['peg_disp']} (#{row['r_peg']})</td>
                <td>{row['mcap_fmt']}</td>
                <td style="text-align:center;">{spark}</td>
            </tr>
            """
        rk_html += """
            </tbody>
        </table>
        </div>
        """
        render_html(rk_html)
    else:
        st.info("NO STOCKS AVAILABLE TO RANK IN THIS CONFIGURATION.")

# ---------------------------------------------------------
# TAB 5: COMMODITIES TAB
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
    comm_html += '<div class="section-banner">COMMODITIES & DERIVATIVE FUTURES (ENERGY, METALS, AG & LEVERAGED BENCHMARKS)</div>'
    comm_html += f'<table class="sheet-table"><thead><tr><th>GROUP</th><th>UNDERLYING BENCHMARK</th><th>TICKER</th><th>FUND NAME</th><th>EXPOSURE</th><th>PRICE</th><th>TODAY ($)</th><th>TODAY (%)</th><th>DAY RANGE</th><th>9 EMA</th><th>21 EMA</th><th>30D (%)</th><th>VOLUME</th><th>EXPENSE</th><th>SIGNAL</th><th style="text-align:center;">30D TREND</th></tr></thead><tbody>'
    
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
            cue = '<span class="bullish-badge">BULL</span>' if d["bullish"] else '<span class="bearish-badge">BEAR</span>'
            spark = make_svg_sparkline(d["sparkline"], is_positive=(d["gain_30"] >= 0))

            comm_html += f'<tr><td>{c["group"]}</td><td>{c["benchmark"]}</td><td style="font-weight:700;">{t}</td><td>{c["name"]}</td><td>{c["leverage"]}</td><td>${d["price"]:.2f}</td><td class="{c_dlr}">{s_dlr}${d["change_dlr"]:.2f}</td><td class="{c_pct}">{s_pct}{d["change_pct"]:.2f}%</td><td>${d["day_low"]:.2f} - ${d["day_high"]:.2f}</td><td>${d["ema_9"]:.2f}</td><td>${d["ema_21"]:.2f}</td><td class="{c_30}">{s_30}{d["gain_30"]:.2f}%</td><td>{d["vol"]:,}</td><td>{c["expense"]}</td><td style="text-align:center;">{cue}</td><td style="text-align:center;">{spark}</td></tr>'
    comm_html += '</tbody></table></div>'
    render_html(comm_html)

# ---------------------------------------------------------
# TAB 6: TERMINAL GLOSSARY & REFERENCE GUIDE (ZERO EMOJIS)
# ---------------------------------------------------------
with tab_glossary:
    st.markdown("<div class='section-banner'>TERMINAL GLOSSARY // INSTITUTIONAL VALUATION & METRIC REFERENCE</div>", unsafe_allow_html=True)
    
    g_col1, g_col2 = st.columns(2)
    
    with g_col1:
        st.markdown(f"""
        ### VALUATION & MULTIPLES
        * **Trailing P/E (Price-to-Earnings):** Current share price divided by actual net income per share over the trailing 12 months (TTM). Backward-looking, but audited.
        * **Forward P/E:** Current share price divided by Wall Street consensus EPS estimates over the upcoming 12 months. Highlights whether earnings are expected to expand (compressing the multiple) or contract.
        * **PEG Ratio (Price/Earnings-to-Growth):** $\\text{{P/E Ratio}} \\div \\text{{Annual Expected EPS Growth Rate}}$. A PEG under **1.0** traditionally indicates a company is undervalued relative to its growth trajectory.
        * **Market Capitalization (Cap):** Total equity value of a firm ($\\text{{Shares Outstanding}} \\times \\text{{Share Price}}$). Categorized as Mega-Cap ($200B+), Large-Cap ($10B–$200B), Mid-Cap ($2B–$10B), and Small-Cap (<$2B).

        ---

        ### EARNINGS & ACCOUNTING STANDARDS
        * **EPS (Earnings Per Share):** The net portion of a company's profit allocated to each share of common stock ($\\text{{Net Income}} \\div \\text{{Shares Outstanding}}$).
        * **GAAP Net Income:** Earnings calculated under strict, standardized Generally Accepted Accounting Principles. Mandatory for official SEC 10-K/10-Q filings.
        * **Non-GAAP ("Adjusted") Earnings:** Operational metrics reported by management that remove non-cash expenses (e.g., stock-based compensation, goodwill impairments) to portray core recurring profitability. Tech and SaaS firms frequently look profitable on Non-GAAP while technically losing money on a GAAP basis.
        """)
        
    with g_col2:
        st.markdown(f"""
        ### ADVANCED TECHNICAL INDICATORS & SIGNALS
        * **14D RSI (Relative Strength Index):** Velocity oscillator measured from 0 to 100. Readings above **70** indicate overbought/extended conditions; readings below **30** indicate oversold washouts. Healthy growth stocks typically hold support between **45 and 55** during pullbacks.
        * **50D Spread (% Distance from 50 SMA):** Quantitative extension relative to the institutional 50-day moving average. Positive values confirm an ongoing uptrend; values exceeding **+12% to +15%** flag severe overextension where institutional buying typically pauses.
        * **RVOL (Relative Volume):** Ratio of today's volume to the 20-day historical average. An RVOL above **1.50x** confirms heavy institutional participation and authentic breakouts/rotations, while an RVOL below **0.70x** signals low-conviction chop.
        * **RS vs. SPY (30D Alpha):** Net 30-day percentage outperformance against the S&P 500 ($\\text{{Stock 30D \\%}} - \\text{{SPY 30D \\%}}$). Positive values highlight the true leaders attracting rotated institutional capital.
        * **9 & 21 EMA Signal:** Short-term trend confirmation. Marked **BULL** when the fast 9 EMA holds above the 21 EMA, and **BEAR** when short-term momentum breaks down.
        * **Beta ($\\beta$):** Systematic market sensitivity (S&P 500 = 1.0). A Beta of 1.8 indicates the asset moves with nearly 80% higher amplitude than the broader index.
        """)
