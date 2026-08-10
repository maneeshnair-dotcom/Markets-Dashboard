# dashboard.py
# ─────────────────────────────────────────────────────────────────────────────
# Nifty50 Signal Dashboard
# Place this file in the SAME folder as your existing analyzer script.
# This file does NOT modify that script at all — it just calls fetch_nifty50_data().
#
# Local run :  streamlit run dashboard.py
# Public URL:  deploy to Streamlit Community Cloud (free) — see README.md
# ─────────────────────────────────────────────────────────────────────────────

import importlib.util, sys, os, time
from datetime import datetime
from zoneinfo import ZoneInfo
import streamlit as st
import pandas as pd
import numpy as np
from kiteconnect import KiteConnect

# ── Header logo (embedded so no extra asset file needs to be committed) ──────
_LOGO_B64 = "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"
import plotly.graph_objects as go
import plotly.express as px

# ── Load the existing analyzer without modifying it ───────────────────────────
ANALYZER_FILE = os.path.join(os.path.dirname(__file__),
                              "nifty50_analyzer_Zerodhafetch.py")

@st.cache_resource(show_spinner=False)
def load_analyzer():
    spec   = importlib.util.spec_from_file_location("nifty50_analyzer", ANALYZER_FILE)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module

# ── Kite login (this dashboard previously had NO way to supply a token —
# fetch_nifty50_data() only reads kite_token.txt off disk. This block ports
# the same login flow from app.py: Streamlit secrets -> token file -> a
# "Login to Kite" button that captures the redirect -> manual paste as a
# last resort. Whatever token is resolved gets written to kite_token.txt,
# which the analyzer module already reads with zero changes needed there.
KITE_API_KEY = "k5d3p1syii84wrz9"
KITE_API_SECRET = "your_api_secret_here"  # from "Show API secret" on developers.kite.trade
KITE_TOKEN_FILE = "kite_token.txt"
IST = ZoneInfo("Asia/Kolkata")


def now_ist() -> datetime:
    return datetime.now(IST).replace(tzinfo=None)


def get_kite_credentials():
    api_key = st.secrets.get("KITE_API_KEY", KITE_API_KEY) if hasattr(st, "secrets") else KITE_API_KEY
    api_secret = st.secrets.get("KITE_API_SECRET", KITE_API_SECRET) if hasattr(st, "secrets") else KITE_API_SECRET
    access_token = None
    if hasattr(st, "secrets") and "KITE_ACCESS_TOKEN" in st.secrets:
        access_token = st.secrets["KITE_ACCESS_TOKEN"]
    elif os.path.exists(KITE_TOKEN_FILE):
        with open(KITE_TOKEN_FILE) as f:
            access_token = f.read().strip()
    return api_key, api_secret, access_token


def kite_token_status() -> str:
    if not os.path.exists(KITE_TOKEN_FILE):
        return "missing"
    mtime = datetime.fromtimestamp(os.path.getmtime(KITE_TOKEN_FILE), tz=IST).replace(tzinfo=None)
    return "fresh" if mtime.date() == now_ist().date() else "stale"


def save_kite_token(access_token: str):
    with open(KITE_TOKEN_FILE, "w") as f:
        f.write(access_token)


def handle_kite_login_callback(api_key: str, api_secret: str):
    request_token = st.query_params.get("request_token")
    if not request_token:
        return
    try:
        temp_kite = KiteConnect(api_key=api_key)
        data = temp_kite.generate_session(request_token, api_secret=api_secret)
        access_token = data["access_token"]
        save_kite_token(access_token)
        st.session_state["kite_access_token"] = access_token
        st.query_params.clear()
        st.success("Kite token refreshed for today.")
        st.rerun()
    except Exception as e:
        st.query_params.clear()
        st.error(f"Token exchange failed: {e}")


# ── Page config ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title  = "Apex Markets Terminal",
    page_icon   = "📈",
    layout      = "wide",
    initial_sidebar_state = "expanded",
)

# ── Custom CSS ────────────────────────────────────────────────────────────────
st.markdown("""
<style>
  /* light corporate-report background */
  .stApp { background: #F4F8FC; color: #00355F; }

  /* sidebar */
  [data-testid="stSidebar"] { background: #FFFFFF; border-right: 1px solid #C9DCEF; }
  [data-testid="stSidebar"] * { color: #00355F; }

  /* expanders in the main body (e.g. the Excel-style column filter) —
     not covered by the sidebar rule above, so force dark text here too */
  [data-testid="stExpander"] { color: #00355F; }
  [data-testid="stExpander"] * { color: #00355F; }
  [data-testid="stExpander"] summary { background: #FFFFFF; border: 1px solid #C9DCEF; border-radius: 8px; }
  [data-testid="stExpander"] [data-testid="stExpanderDetails"] { background: #FFFFFF; }

  /* widget labels anywhere in the main body (multiselect/slider/selectbox titles) */
  [data-testid="stWidgetLabel"] p { color: #00355F !important; }

  /* dropdown boxes (selectbox / multiselect) — dark blue border */
  div[data-baseweb="select"],
  div[data-baseweb="select"] > div,
  div[data-baseweb="select"] > div > div,
  div[data-baseweb="select"] [role="button"] {
    border: 1.5px solid #00355F !important;
    border-radius: 6px !important;
    box-shadow: none !important;
    outline: none !important;
  }
  div[data-baseweb="select"]:hover,
  div[data-baseweb="select"]:focus-within,
  div[data-baseweb="select"] > div:hover,
  div[data-baseweb="select"] > div:focus-within {
    border: 1.5px solid #00355F !important;
    box-shadow: none !important;
  }

  /* metric cards */
  [data-testid="stMetric"] {
    background: #FFFFFF;
    border: 1px solid #C9DCEF;
    border-radius: 10px;
    padding: 16px 20px;
  }
  [data-testid="stMetricLabel"]  { color: #5D7A99 !important; font-size: 12px; }
  [data-testid="stMetricValue"]  { color: #00355F !important; font-size: 28px; font-weight: 700; }

  /* BUY / SELL pill badges */
  .pill-buy     { background:#DFF5E5; color:#1A7A3D; padding:3px 10px;
                  border-radius:20px; font-size:12px; font-weight:600; }
  .pill-sell    { background:#FCE3E3; color:#B42318; padding:3px 10px;
                  border-radius:20px; font-size:12px; font-weight:600; }
  .pill-neutral { background:#E4EFF9; color:#5D7A99; padding:3px 10px;
                  border-radius:20px; font-size:12px; font-weight:600; }

  /* dataframe rows */
  .stDataFrame { border: 1px solid #C9DCEF; border-radius: 8px; }

  /* header */
  .dash-header { display:flex; align-items:center; gap:12px;
                 border-bottom:2px solid #00355F; padding-bottom:16px; margin-bottom:24px; }
  .dash-title  { font-size:26px; font-weight:700; color:#00355F; }
  .dash-sub    { font-size:13px; color:#5D7A99; margin-top:2px; }

  /* section headers */
  .sec-label   { font-size:13px; font-weight:600; color:#5D7A99;
                 letter-spacing:0.08em; text-transform:uppercase; margin-bottom:10px; }

  /* refresh button */
  button[kind="primary"] {
    background: #00355F !important;
    border-color: #00355F !important;
    color: #FFFFFF !important;
    font-weight: 600 !important;
    border-radius: 8px !important;
  }
</style>
""", unsafe_allow_html=True)


# ── Resolve Kite credentials / process a login redirect before anything else ─
kite_api_key, kite_api_secret, kite_access_token = get_kite_credentials()
handle_kite_login_callback(kite_api_key, kite_api_secret)
if "kite_access_token" in st.session_state:
    kite_access_token = st.session_state["kite_access_token"]

# ── Ticker list registry (single FnO list) ────────────────────────────────
_analyzer_mod   = load_analyzer()
TICKER_REGISTRY = getattr(_analyzer_mod, "_TICKER_LIST_REGISTRY", {"Nifty": _analyzer_mod.NIFTY50_TICKERS})
SKYBLUE_TICKERS = getattr(_analyzer_mod, "SKYBLUE_TICKERS", set())

# ── Market Sentiment basket — EDIT THIS LIST to change the default bellwether
# stocks used for the Market Sentiment badge (names are post-cleaning, i.e.
# without ".NS" or "^" — same as they appear in the "Stock Name" column).
# You can also add/remove stocks live from the sidebar without touching code.
DEFAULT_SENTIMENT_BASKET = [
    "NSEI", "BSESN", "NIFTY_TOTAL_MKT", "RELIANCE", "HDFCBANK", "BHARTIARTL",
]

_ALL_KNOWN_STOCK_NAMES = sorted({
    t.replace(".NS", "").replace("^", "")
    for lst in TICKER_REGISTRY.values() for t in lst
})

# ── Sidebar controls (these are PENDING choices — see 'applied' below) ────────
with st.sidebar:
    st.markdown("### ⚙️ Settings")
    list_name_w = st.selectbox("Ticker list", list(TICKER_REGISTRY.keys()), index=0)
    n_days_w   = st.slider("History (days)",    min_value=5,  max_value=600,  value=30,  step=5)
    interval_w = st.selectbox("INTERVAL", ["15m", "30m", "1h", "4h", "1d", "1wk"], index=2)
    buy_thr_w  = st.slider("Composite Score highlight ≥",   min_value=1, max_value=5, value=2,
                            help="Only tints the Score cell green for reference. "
                                 "BUY/SELL is now decided by the rule-based logic (Peak/Trough + "
                                 "Close colour / BB breakout / Volume), not this score.")
    sell_thr_w = st.slider("Composite Score highlight ≤",  min_value=-5, max_value=-1, value=-2,
                            help="Only tints the Score cell red for reference. "
                                 "BUY/SELL is now decided by the rule-based logic, not this score.")
    st.markdown("---")
    sig_filter = st.multiselect("Filter Final Signal",
                                ["BUY", "SELL", "NEUTRAL"],
                                default=["BUY", "SELL", "NEUTRAL"])
    st.markdown("---")
    sentiment_basket_w = st.multiselect(
        "Market Sentiment basket",
        _ALL_KNOWN_STOCK_NAMES,
        default=[t for t in DEFAULT_SENTIMENT_BASKET if t in _ALL_KNOWN_STOCK_NAMES],
        help="Bellwether stocks used to compute the Market Sentiment badge. "
             "Add or remove any stock here — only ones present in the "
             "currently-selected ticker list are actually used for scoring."
    )
    st.markdown("---")
    auto_refresh = st.toggle("AUTO-REFRESH (5 min)", value=False)

    st.markdown("---")
    st.markdown("### 🔐 Kite Login")
    _status = kite_token_status()
    if _status == "fresh":
        st.success("Token generated today ✅")
    elif _status == "stale":
        st.warning("Token is from a previous day — refresh below.")
    else:
        st.warning("No token found — log in below.")
    _temp_kite = KiteConnect(api_key=kite_api_key)
    st.link_button("Login to Kite / Refresh Token", _temp_kite.login_url(), width='stretch')
    st.caption("Opens Zerodha's login in a new tab and captures the token automatically on redirect.")
    if not kite_access_token:
        kite_access_token = st.text_input("Or paste an access token manually", type="password")

    st.markdown("<div style='color:#5D7A99;font-size:12px'>Powered by Zerodha Kite (yfinance fallback for global tickers)</div>",
                unsafe_allow_html=True)

# The analyzer only reads kite_token.txt off disk (not st.secrets or this
# session's widget state), so whatever token was resolved above — from
# secrets, a fresh login, or manual paste — needs to land in that file
# before fetch_nifty50_data() runs.
if kite_access_token:
    save_kite_token(kite_access_token)


# ── Data fetching (cached, clears on Refresh) ─────────────────────────────────
@st.cache_data(ttl=300, show_spinner=False)   # 5-min TTL matches auto-refresh
def get_data(list_name, n_days, interval, buy_thr, sell_thr):
    mod     = load_analyzer()
    tickers = TICKER_REGISTRY[list_name]
    return mod.fetch_nifty50_data(n_days, interval, buy_thr, sell_thr, ticker_list=tickers)


# ── Header ────────────────────────────────────────────────────────────────────
col_title, col_refresh, col_time = st.columns([5, 1.2, 1.8])

with col_refresh:
    st.markdown("<div style='height:45px'></div>", unsafe_allow_html=True)
    do_refresh = st.button("🔄 REFRESH DATA ", type="primary", width='stretch')

with col_time:
    st.markdown("<div style='height:40px'></div>", unsafe_allow_html=True)
    ts_placeholder = st.empty()


# ── Commit pending sidebar picks -> applied params ────────────────────────────
# Sidebar widgets above are just "pending" choices. We only fetch new data when
# the Refresh button is clicked, when auto-refresh's timer fires (bottom of
# script), or on first load. Any other rerun (moving a slider, changing the
# ticker list, etc.) reuses the last-applied params, so get_data() hits its
# cache instead of firing a new request.
if "applied_params" not in st.session_state:
    st.session_state.applied_params = dict(
        list_name=list_name_w, n_days=n_days_w, interval=interval_w,
        buy_thr=buy_thr_w, sell_thr=sell_thr_w,
    )

if do_refresh:
    st.session_state.applied_params = dict(
        list_name=list_name_w, n_days=n_days_w, interval=interval_w,
        buy_thr=buy_thr_w, sell_thr=sell_thr_w,
    )
    st.cache_data.clear()

applied   = st.session_state.applied_params
list_name, n_days, interval, buy_thr, sell_thr = (
    applied["list_name"], applied["n_days"], applied["interval"],
    applied["buy_thr"], applied["sell_thr"],
)

pending_changed = applied != dict(
    list_name=list_name_w, n_days=n_days_w, interval=interval_w,
    buy_thr=buy_thr_w, sell_thr=sell_thr_w,
)

with col_title:
    st.markdown("""
    <div class="dash-header">
      <img src="data:image/png;base64,""" + _LOGO_B64 + """" style="height:56px;width:auto" />
      <div>
        <div class="dash-title">Apex Markets Terminal</div>
        <div class="dash-sub"> Composite Signals: RSI · Stochastic · Bollinger · Volume</div>
      </div>
    </div>""", unsafe_allow_html=True)
    if pending_changed:
        st.caption("⚠️ Sidebar has unapplied changes — CLICK **REFRESH DATA ** to load them.")


# ── Fetch data ────────────────────────────────────────────────────────────────
with st.spinner(f"⏳  Fetching live Market Data For {list_name} tickers..."):
    try:
        df = get_data(list_name, n_days, interval, buy_thr, sell_thr)
        fetch_ok = True
    except Exception as e:
        st.error(f"❌  Data Fetch Failed: {e}")
        st.stop()
        fetch_ok = False

ts_placeholder.markdown(
    f"<div style='color:#5D7A99;font-size:12px;text-align:right;margin-top:8px'>"
    f"Last updated (IST)<br><b style='color:#00355F'>"
    f"{datetime.now(ZoneInfo('Asia/Kolkata')).strftime('%d %b %Y  %H:%M:%S')}</b></div>",
    unsafe_allow_html=True)


# ── Render one full dashboard view for a given fetched dataframe ──────────────
# key_suffix keeps widget keys unique when this is called twice (selected interval
# tab + 1D reference tab).
# ── Market Sentiment (weighted bellwether consensus) ───────────────────────────
def compute_market_sentiment(latest_df, basket):
    """
    For each bellwether stock present in `basket` AND in this run's data,
    score its latest candle from -3 to +3 using three independent signals
    (so no single noisy indicator can flip the result on its own):
        Peak/Trough reversal : Peak -1, Trough +1, neither 0
        Volume confirmation  : Strong_Sell_Vol -1, Strong_Buy_Vol +1, neither 0
        BB position           : Upper_Breakout -1, Lower_Breakout +1, Inside 0
    Then averages across the basket (not requiring unanimous agreement —
    a majority lean is enough) and classifies:
        avg <= -1.0  -> RED    (bearish)
        avg >=  1.0  -> GREEN  (bullish)
        otherwise    -> YELLOW (mixed / no consensus)
    Returns (sentiment, avg_score, per_stock_details, missing_stocks).
    """
    present = latest_df[latest_df["Stock Name"].isin(basket)]
    missing = sorted(set(basket) - set(present["Stock Name"]))

    if present.empty:
        return None, None, [], missing

    details = []
    for _, row in present.iterrows():
        s = 0
        if row.get("Diff_Peak") == "Short":     s -= 1
        elif row.get("Diff_Trough") == "LONG":  s += 1

        if row.get("Volume_Signal") == "Strong_Sell_Vol":   s -= 1
        elif row.get("Volume_Signal") == "Strong_Buy_Vol":  s += 1

        if row.get("BB_Position") == "Upper_Breakout":  s -= 1
        elif row.get("BB_Position") == "Lower_Breakout": s += 1

        details.append((row["Stock Name"], s))

    avg = sum(s for _, s in details) / len(details)
    if avg <= -1.0:
        sentiment = "RED"
    elif avg >= 1.0:
        sentiment = "GREEN"
    else:
        sentiment = "YELLOW"
    return sentiment, avg, details, missing


def render_dashboard_body(df, key_suffix):
    # ── Latest bar per stock ───────────────────────────────────────────────────────
    latest = df.groupby("Stock Name").last().reset_index()
    latest_filt = latest[latest["Final_Signal"].isin(sig_filter)]


    # ── KPI summary — compact text strip (was: 8 large metric cards) ──────────────
    st.markdown('<div class="sec-label">Overview — Last Candle per stock</div>',
                unsafe_allow_html=True)

    buy_stocks          = sorted(latest.loc[latest["Final_Signal"]  == "BUY",     "Stock Name"].tolist())
    sell_stocks         = sorted(latest.loc[latest["Final_Signal"]  == "SELL",    "Stock Name"].tolist())
    neu_stocks          = sorted(latest.loc[latest["Final_Signal"]  == "NEUTRAL", "Stock Name"].tolist())
    peak_stocks         = sorted(latest.loc[latest["Diff_Peak"]     == "Short",   "Stock Name"].tolist())
    trough_stocks       = sorted(latest.loc[latest["Diff_Trough"]   == "LONG",    "Stock Name"].tolist())
    vol_rising_stocks   = sorted(latest.loc[latest["Volume_Trend"]  == "Rising",  "Stock Name"].tolist())
    vol_falling_stocks  = sorted(latest.loc[latest["Volume_Trend"]  == "Falling", "Stock Name"].tolist())
    strong_buy_vol_stocks  = sorted(latest.loc[latest["Volume_Signal"] == "Strong_Buy_Vol",  "Stock Name"].tolist())
    strong_sell_vol_stocks = sorted(latest.loc[latest["Volume_Signal"] == "Strong_Sell_Vol", "Stock Name"].tolist())
    lsma_up_stocks      = sorted(latest.loc[latest["Signal"]        == "LONG",    "Stock Name"].tolist())
    lsma_down_stocks    = sorted(latest.loc[latest["Signal"]        == "SHORT",   "Stock Name"].tolist())

    kpi_items = [
        ("🟢", "BUY",           buy_stocks),
        ("🔴", "SELL",          sell_stocks),
        ("⚪", "NEUTRAL",       neu_stocks),
        ("📊", "Stocks",        latest["Stock Name"].tolist()),
        ("🔺", "Diff Peak",     peak_stocks),
        ("🔻", "Diff Trough",   trough_stocks),
        ("📈", "Vol Rising",    vol_rising_stocks),
        ("📉", "Vol Falling",   vol_falling_stocks),
        ("🟢📶", "Strong Buy Vol",  strong_buy_vol_stocks),
        ("🔴📶", "Strong Sell Vol", strong_sell_vol_stocks),
        ("🟩", "LSMA-WMA ↑",    lsma_up_stocks),
        ("🟥", "LSMA-WMA ↓",    lsma_down_stocks),
    ]

    _pills = "".join(
        f"<span style='display:inline-flex;align-items:center;gap:5px;background:#E4EFF9;"
        f"border:1px solid #C9DCEF;border-radius:6px;padding:4px 11px;margin:2px 4px 2px 0;"
        f"font-size:12.5px;color:#00355F;white-space:nowrap'>{emoji} <b>{label}</b>&nbsp;{len(stocks)}</span>"
        for emoji, label, stocks in kpi_items
    )
    st.markdown(f"<div style='display:flex;flex-wrap:wrap;align-items:center'>{_pills}</div>",
                unsafe_allow_html=True)

    return_lookup = latest.set_index("Stock Name")["Return"]

    def _colored_stock_list(stocks):
        if not stocks:
            return "None"
        spans = []
        for s in stocks:
            ret = return_lookup.get(s)
            try:
                ret = float(ret)
                color = "#1A7A3D" if ret > 0 else ("#B42318" if ret < 0 else "#5D7A99")
            except (TypeError, ValueError):
                color = "#5D7A99"
            spans.append(f"<span style='color:{color};font-weight:600'>{s}</span>")
        return ", ".join(spans)

    with st.popover("🔍 View stock names", key=f"kpi_popover_{key_suffix}"):
        for emoji, label, stocks in kpi_items:
            if label == "Stocks":
                continue
            st.markdown(f"**{emoji} {label} ({len(stocks)})**")
            st.markdown(f"<div style='font-size:13px'>{_colored_stock_list(stocks)}</div>",
                        unsafe_allow_html=True)

    st.markdown("---")


    # ── Market Sentiment badge ──────────────────────────────────────────────────
    sentiment, sent_avg, sent_details, sent_missing = compute_market_sentiment(latest, sentiment_basket_w)

    _SENT_STYLE = {
        "RED":    ("🔴", "BEARISH", "#FCE3E3", "#B42318"),
        "GREEN":  ("🟢", "BULLISH", "#DFF5E5", "#1A7A3D"),
        "YELLOW": ("🟡", "MIXED / NEUTRAL", "#FEF3C7", "#92650A"),
    }

    if sentiment is None:
        st.info("📊 **Market Sentiment**: none of your basket stocks are present in this ticker list. "
                "Adjust the basket in the sidebar or switch ticker lists.")
    else:
        emoji_s, label_s, bg_s, fg_s = _SENT_STYLE[sentiment]
        col_badge, col_pop = st.columns([5, 1])
        with col_badge:
            st.markdown(
                f"<div style='background:{bg_s};border:1px solid {fg_s};border-radius:10px;"
                f"padding:12px 20px;display:flex;align-items:center;gap:10px'>"
                f"<span style='font-size:22px'>{emoji_s}</span>"
                f"<span style='color:{fg_s};font-weight:700;font-size:16px'>Market Sentiment: {label_s}</span>"
                f"<span style='color:{fg_s};font-size:12px;opacity:0.8'>(avg score {sent_avg:+.2f} across "
                f"{len(sent_details)} bellwether stock(s))</span>"
                f"</div>", unsafe_allow_html=True)
        with col_pop:
            with st.popover("Details", key=f"sentiment_popover_{key_suffix}"):
                st.markdown("**Per-stock score** (Peak/Trough + Volume + BB position, range -3 to +3)")
                for name, s in sorted(sent_details, key=lambda x: x[1]):
                    c = "#1A7A3D" if s > 0 else ("#B42318" if s < 0 else "#5D7A99")
                    st.markdown(f"<span style='color:{c};font-weight:600'>{name}: {s:+d}</span>",
                                unsafe_allow_html=True)
                if sent_missing:
                    st.caption(f"Not in this ticker list: {', '.join(sent_missing)}")

    st.markdown("---")


    # ── Main signal table — full Excel-parity view, directly under Overview ───────
    st.markdown('<div class="sec-label">All Stocks — Last Candle Signals (full data, Excel-style colouring)</div>',
                unsafe_allow_html=True)

    # Show every column the analyzer produces (no truncation) — matches the xlsx export
    show_df = latest_filt.copy()

    _signal_order = {"BUY": 0, "SELL": 1, "NEUTRAL": 2}
    show_df["_sort"] = show_df["Final_Signal"].map(_signal_order).fillna(3)
    show_df = show_df.sort_values(["_sort", "Score"],
                                   ascending=[True, False]).drop(columns="_sort").reset_index(drop=True)

    # ── Column filter (Excel-style autofilter — choose ANY NUMBER of columns) ─────
    with st.expander("🔎 Filter table by column(s)  — like an Excel autofilter", key=f"filter_exp_{key_suffix}"):
        filter_cols = st.multiselect("Choose one or more columns to filter", list(show_df.columns), key=f"filtcols_{key_suffix}")
        for fc in filter_cols:
            col_data = show_df[fc]
            if pd.api.types.is_numeric_dtype(col_data) and col_data.notna().any():
                lo, hi = float(col_data.min()), float(col_data.max())
                if lo == hi:
                    st.caption(f"All remaining rows have {fc} = {lo}")
                else:
                    sel_lo, sel_hi = st.slider(f"{fc} range", lo, hi, (lo, hi), key=f"filt_range_{fc}_{key_suffix}")
                    show_df = show_df[col_data.between(sel_lo, sel_hi)]
            else:
                uniq = sorted(col_data.dropna().astype(str).unique().tolist())
                sel_vals = st.multiselect(f"{fc} values", uniq, default=uniq, key=f"filt_vals_{fc}_{key_suffix}")
                show_df = show_df[col_data.astype(str).isin(sel_vals)]
        show_df = show_df.reset_index(drop=True)
        if filter_cols:
            st.caption(f"{len(show_df)} row(s) match all selected filters.")
            show_df = show_df.reset_index(drop=True)


    def style_row(row):
        """Row-wise styling: a white/light-blue zebra stripe as the base for
        every cell (matching the reference report look), then semantic
        overrides (BUY/SELL, RSI, CLOSE vs Gann levels, watchlist, etc.) on
        top — mirrors the same colour scheme used in the .xlsx export."""
        styles = pd.Series("", index=row.index)

        # Zebra striping base — alternating white / light-blue rows
        base_bg = "#FFFFFF" if (row.name % 2 == 0) else "#E4EFF9"
        for col in row.index:
            styles[col] = f"background-color:{base_bg}"

        v = row.get("Final_Signal")
        if v == "BUY":       styles["Final_Signal"] = "background-color:#DFF5E5;color:#1A7A3D;font-weight:700"
        elif v == "SELL":    styles["Final_Signal"] = "background-color:#FCE3E3;color:#B42318;font-weight:700"
        elif v == "NEUTRAL": styles["Final_Signal"] += ";color:#5D7A99"

        try:
            rsi = float(row.get("RSI"))
            if rsi < 30: styles["RSI"] += ";color:#1A7A3D;font-weight:600"
            elif rsi > 70: styles["RSI"] += ";color:#B42318;font-weight:600"
        except (TypeError, ValueError):
            pass

        try:
            score = float(row.get("Score"))
            if score >= buy_thr:  styles["Score"] += ";color:#1A7A3D;font-weight:700"
            elif score <= sell_thr: styles["Score"] += ";color:#B42318;font-weight:700"
        except (TypeError, ValueError):
            pass

        gz = row.get("Gann_Reversal_Zone")
        if gz == "Resistance": styles["Gann_Reversal_Zone"] += ";color:#B42318"
        elif gz == "Support":  styles["Gann_Reversal_Zone"] += ";color:#1A7A3D"

        sd = str(row.get("Stoch_Div"))
        if "Bullish" in sd: styles["Stoch_Div"] += ";color:#1A7A3D;font-weight:600"
        elif "Bearish" in sd: styles["Stoch_Div"] += ";color:#B42318;font-weight:600"

        # Return — green if price rose vs previous candle, red if it fell
        try:
            ret = float(row.get("Return"))
            if ret > 0:   styles["Return"] += ";color:#1A7A3D;font-weight:700"
            elif ret < 0: styles["Return"] += ";color:#B42318;font-weight:700"
        except (TypeError, ValueError):
            pass

        # CLOSE — checked in priority order:
        # 1) Gann level shift vs previous candle (most current/actionable signal)
        #      Level_Dropped → red TEXT (support or resistance moved down)
        #      Support_Up    → green BACKGROUND (support moved up)
        # 2) fall back to the static Above_Resistance / Below_Support position
        #    (same green/red scheme used in the xlsx export) when the level is
        #    unchanged from the previous candle
        level_shift = row.get("Gann_Level_Shift")
        cc = row.get("Close_Color")
        if level_shift == "Support_Up":
            styles["CLOSE"] = "background-color:#DFF5E5;color:#1A7A3D;font-weight:700"
        elif level_shift == "Level_Dropped":
            styles["CLOSE"] += ";color:#B42318;font-weight:700"
        elif cc == "Above_Resistance":  styles["CLOSE"] = "background-color:#FCE3E3;color:#B42318;font-weight:700"
        elif cc == "Below_Support":     styles["CLOSE"] = "background-color:#DFF5E5;color:#1A7A3D;font-weight:700"

        # Stock Name — sky blue watchlist, same as the xlsx export
        if row.get("Stock Name") in SKYBLUE_TICKERS:
            styles["Stock Name"] = "background-color:#ACD4F1;color:#00355F;font-weight:700"

        return styles


    _fmt_2dp = ["OPEN", "HIGH", "LOW", "CLOSE", "VOLUME", "Stoch_K", "Stoch_D",
                "BB_Middle", "BB_Upper", "BB_Lower", "BB_Width",
                "Volume_SMA", "Volume_Ratio", "OBV", "WMA", "LSMA", "LSMA-WMA",
                "Gann_Resistance", "Gann_Support"]
    fmt = {c: "{:,.2f}" for c in _fmt_2dp if c in show_df.columns}
    if "RSI" in show_df.columns:             fmt["RSI"] = "{:.1f}"
    if "Return" in show_df.columns:          fmt["Return"] = "{:+.2f}"
    if "Score" in show_df.columns: fmt["Score"] = "{:+d}"

    styled = (
        show_df.style
        .apply(style_row, axis=1)
        .format(fmt, na_rep="─")
        .set_properties(**{"border": "1px solid #C9DCEF"})
        .set_table_styles([{
            "selector": "th",
            "props": [("background-color","#FFFFFF"), ("color","#00355F"),
                       ("font-size","12px"), ("font-weight","700"),
                       ("border-bottom","2px solid #00355F"),
                       ("border-left","1px solid #C9DCEF"),
                       ("border-right","1px solid #C9DCEF")]
        }])
    )

    st.dataframe(styled, width='stretch', height=2000, key=f"df_main_{key_suffix}",
                 column_config={"Stock Name": st.column_config.TextColumn(pinned=True)})
    st.caption("🔵 Sky-blue = watchlist ticker · 🟢 CLOSE green = broke below Gann support · 🔴 CLOSE red = broke above Gann resistance")

    st.markdown("---")


    # ── Signal distribution / RSI distribution charts ─────────────────────────────
    col_chart1, col_chart2 = st.columns([1, 1])

    with col_chart1:
        st.markdown('<div class="sec-label">Signal Distribution</div>',
                    unsafe_allow_html=True)
        sig_counts = latest["Final_Signal"].value_counts().reset_index()
        sig_counts.columns = ["Signal", "Count"]
        color_map = {"BUY": "#3fb950", "SELL": "#f85149", "NEUTRAL": "#5D7A99"}
        fig_bar = px.bar(sig_counts, x="Signal", y="Count",
                         color="Signal", color_discrete_map=color_map,
                         template="plotly_white", height=220)
        fig_bar.update_layout(showlegend=False, margin=dict(t=10, b=10, l=10, r=10),
                               paper_bgcolor="#FFFFFF", plot_bgcolor="#FFFFFF",
                               font_color="#00355F")
        fig_bar.update_xaxes(showgrid=False)
        fig_bar.update_yaxes(showgrid=True, gridcolor="#E4EFF9")
        st.plotly_chart(fig_bar, width='stretch', key=f"chart_bar_{key_suffix}")

    with col_chart2:
        st.markdown('<div class="sec-label">RSI distribution (last bar per stock)</div>',
                    unsafe_allow_html=True)
        fig_rsi = go.Figure(go.Histogram(
            x=latest["RSI"].dropna(), nbinsx=20,
            marker_color="#7399C6", opacity=0.8))
        fig_rsi.add_vline(x=30, line_dash="dash", line_color="#3fb950",
                          annotation_text="30", annotation_position="top right",
                          annotation_font_color="#3fb950")
        fig_rsi.add_vline(x=70, line_dash="dash", line_color="#f85149",
                          annotation_text="70", annotation_position="top right",
                          annotation_font_color="#f85149")
        fig_rsi.update_layout(template="plotly_white", height=220,
                               margin=dict(t=10, b=10, l=10, r=10),
                               paper_bgcolor="#FFFFFF", plot_bgcolor="#FFFFFF",
                               showlegend=False, font_color="#00355F")
        fig_rsi.update_xaxes(showgrid=False)
        fig_rsi.update_yaxes(showgrid=True, gridcolor="#E4EFF9")
        st.plotly_chart(fig_rsi, width='stretch', key=f"chart_rsi_dist_{key_suffix}")

    st.markdown("---")


    # ── Individual stock deep-dive ────────────────────────────────────────────────
    st.markdown('<div class="sec-label">Stock Deep-Dive</div>',
                unsafe_allow_html=True)

    selected_stock = st.selectbox(
        "Pick a stock",
        options=sorted(df["Stock Name"].unique()),
        index=0,
        key=f"stock_picker_{key_suffix}"
    )

    stock_df = df[df["Stock Name"] == selected_stock].copy()

    # Price + LSMA + WMA chart
    fig_price = go.Figure()
    fig_price.add_trace(go.Candlestick(
        x=stock_df["Date"],
        open=stock_df["OPEN"], high=stock_df["HIGH"],
        low=stock_df["LOW"],   close=stock_df["CLOSE"],
        name="OHLC",
        increasing_line_color="#3fb950", decreasing_line_color="#f85149",
    ))
    fig_price.add_trace(go.Scatter(x=stock_df["Date"], y=stock_df["LSMA"],
        mode="lines", name="LSMA", line=dict(color="#7399C6", width=1.5)))
    fig_price.add_trace(go.Scatter(x=stock_df["Date"], y=stock_df["WMA"],
        mode="lines", name="WMA",  line=dict(color="#d2a679", width=1.5, dash="dot")))
    fig_price.add_trace(go.Scatter(x=stock_df["Date"], y=stock_df["BB_Upper"],
        mode="lines", name="BB Upper", line=dict(color="#6e40c9", width=1, dash="dot")))
    fig_price.add_trace(go.Scatter(x=stock_df["Date"], y=stock_df["BB_Lower"],
        mode="lines", name="BB Lower", line=dict(color="#6e40c9", width=1, dash="dot"),
        fill="tonexty", fillcolor="rgba(110,64,201,0.05)"))

    # BUY / SELL markers
    buy_rows  = stock_df[stock_df["Final_Signal"] == "BUY"]
    sell_rows = stock_df[stock_df["Final_Signal"] == "SELL"]
    if not buy_rows.empty:
        fig_price.add_trace(go.Scatter(
            x=buy_rows["Date"], y=buy_rows["LOW"] * 0.999,
            mode="markers", name="BUY",
            marker=dict(symbol="triangle-up", color="#3fb950", size=10)))
    if not sell_rows.empty:
        fig_price.add_trace(go.Scatter(
            x=sell_rows["Date"], y=sell_rows["HIGH"] * 1.001,
            mode="markers", name="SELL",
            marker=dict(symbol="triangle-down", color="#f85149", size=10)))

    # Gann target lines (last bar values)
    last_tgt = stock_df["Gann_Resistance"].dropna().iloc[-1] if not stock_df["Gann_Resistance"].dropna().empty else None
    last_sup = stock_df["Gann_Support"].dropna().iloc[-1]  if not stock_df["Gann_Support"].dropna().empty else None
    if last_tgt:
        fig_price.add_hline(y=last_tgt, line_dash="dash", line_color="#f0a030",
                             annotation_text=f"Gann T {last_tgt:,.1f}",
                             annotation_position="right")
    if last_sup:
        fig_price.add_hline(y=last_sup, line_dash="dash", line_color="#3fb950",
                             annotation_text=f"Gann S {last_sup:,.1f}",
                             annotation_position="right")

    fig_price.update_layout(
        template="plotly_white", height=420,
        paper_bgcolor="#FFFFFF", plot_bgcolor="#FFFFFF",
        font_color="#00355F", showlegend=True,
        legend=dict(bgcolor="#FFFFFF", bordercolor="#C9DCEF", borderwidth=1),
        margin=dict(t=20, b=20, l=10, r=80),
        xaxis_rangeslider_visible=False,
        xaxis=dict(showgrid=False),
        yaxis=dict(showgrid=True, gridcolor="#E4EFF9"),
    )
    st.plotly_chart(fig_price, width='stretch', key=f"chart_price_{key_suffix}")

    # RSI + Stoch sub-charts
    c_rsi, c_stoch = st.columns(2)

    with c_rsi:
        fig_rsi2 = go.Figure()
        fig_rsi2.add_trace(go.Scatter(x=stock_df["Date"], y=stock_df["RSI"],
            mode="lines", name="RSI", line=dict(color="#7399C6", width=1.5)))
        fig_rsi2.add_hline(y=70, line_dash="dash", line_color="#f85149", line_width=1)
        fig_rsi2.add_hline(y=30, line_dash="dash", line_color="#3fb950", line_width=1)
        fig_rsi2.update_layout(template="plotly_white", height=180,
            paper_bgcolor="#FFFFFF", plot_bgcolor="#FFFFFF",
            margin=dict(t=10,b=10,l=10,r=10), title="RSI (14)",
            font_color="#00355F", showlegend=False,
            xaxis=dict(showgrid=False),
            yaxis=dict(showgrid=True, gridcolor="#E4EFF9", range=[0,100]))
        st.plotly_chart(fig_rsi2, width='stretch', key=f"chart_rsi2_{key_suffix}")

    with c_stoch:
        fig_stoch = go.Figure()
        fig_stoch.add_trace(go.Scatter(x=stock_df["Date"], y=stock_df["Stoch_K"],
            mode="lines", name="%K", line=dict(color="#d2a679", width=1.5)))
        fig_stoch.add_trace(go.Scatter(x=stock_df["Date"], y=stock_df["Stoch_D"],
            mode="lines", name="%D", line=dict(color="#7399C6", width=1, dash="dot")))
        fig_stoch.add_hline(y=80, line_dash="dash", line_color="#f85149", line_width=1)
        fig_stoch.add_hline(y=20, line_dash="dash", line_color="#3fb950", line_width=1)
        fig_stoch.update_layout(template="plotly_white", height=180,
            paper_bgcolor="#FFFFFF", plot_bgcolor="#FFFFFF",
            margin=dict(t=10,b=10,l=10,r=10), title="Stochastic (12,5)",
            font_color="#00355F", showlegend=True,
            legend=dict(bgcolor="#FFFFFF", bordercolor="#C9DCEF", borderwidth=1,
                        orientation="h", y=1.1),
            xaxis=dict(showgrid=False),
            yaxis=dict(showgrid=True, gridcolor="#E4EFF9", range=[0,100]))
        st.plotly_chart(fig_stoch, width='stretch', key=f"chart_stoch_{key_suffix}")

    st.markdown("---")


    # ── Full history table for the selected stock (every row fetched, oldest→newest) ─
    st.markdown(f'<div class="sec-label">{selected_stock} — Full Fetched History ({len(stock_df)} rows)</div>',
                unsafe_allow_html=True)

    stock_hist = stock_df.sort_values("Date").reset_index(drop=True)
    stock_styled = (
        stock_hist.style
        .apply(style_row, axis=1)
        .format(fmt, na_rep="─")
        .set_properties(**{"border": "1px solid #C9DCEF"})
        .set_table_styles([{
            "selector": "th",
            "props": [("background-color","#FFFFFF"), ("color","#00355F"),
                       ("font-size","12px"), ("font-weight","700"),
                       ("border-bottom","2px solid #00355F"),
                       ("border-left","1px solid #C9DCEF"),
                       ("border-right","1px solid #C9DCEF")]
        }])
    )
    st.dataframe(stock_styled, width='stretch', height=400, key=f"df_stock_hist_{key_suffix}",
                 column_config={"Stock Name": st.column_config.TextColumn(pinned=True)})

    stock_csv = stock_hist.to_csv(index=False).encode("utf-8")
    st.download_button(f"⬇️  Download {selected_stock} history CSV", stock_csv,
                        file_name=f"{selected_stock}_history.csv", mime="text/csv",
                        key=f"dl_stock_hist_{key_suffix}")

    st.markdown("---")


    # ── Full data table (expandable) ──────────────────────────────────────────────
    with st.expander("📋  Full raw data table (all tickers, all bars)", key=f"raw_exp_{key_suffix}"):
        search_txt = st.text_input("Search stock name", "", key=f"search_raw_{key_suffix}")
        full_view  = df[df["Stock Name"].str.contains(search_txt, case=False)] if search_txt else df
        st.dataframe(full_view, width='stretch', height=int(38*(len(full_view)+1)+3), key=f"df_raw_{key_suffix}",
                        column_config={"Stock Name": st.column_config.TextColumn(pinned=True)})
        csv = full_view.to_csv(index=False).encode("utf-8")
        st.download_button("⬇️  Download filtered CSV", csv,
                            file_name="nifty50_signals.csv", mime="text/csv",
                            key=f"dl_raw_{key_suffix}")




# ── Reference 1D fetch (always run alongside your selected interval) ──────────
REF_1D_DAYS = max(n_days, 60)   # ensure enough daily bars for indicator warm-up
need_reference_tab = (interval != "1d")

df_1d = None
if need_reference_tab:
    with st.spinner("⏳  Fetching 1D reference data..."):
        try:
            df_1d = get_data(list_name, REF_1D_DAYS, "1d", buy_thr, sell_thr)
        except Exception as e:
            st.warning(f"⚠️  1D reference fetch failed: {e}")
            df_1d = None


# ── Render: two tabs (your selected interval + a fixed 1D reference) ──────────
# so you can always cross-check the intraday/short-interval read against the
# daily picture without changing the Interval filter itself.
if need_reference_tab and df_1d is not None:
    tab_primary, tab_ref = st.tabs([f"📊 {interval}  (Your Selection)", "📅 1D  (Reference)"])
    with tab_primary:
        render_dashboard_body(df, key_suffix="sel")
    with tab_ref:
        render_dashboard_body(df_1d, key_suffix="ref1d")

    # ── Peak/Trough overlap — stocks agreeing on BOTH the selected interval
    # AND the 1D reference for the latest candle (e.g. POWERGRID showing a
    # trough on both 1h and 1D right now) ─────────────────────────────────────
    st.markdown("---")
    st.markdown(f'<div class="sec-label">🔗 Peak / Trough Overlap — {interval} &amp; 1D agree (latest candle)</div>',
                unsafe_allow_html=True)

    latest_sel = df.groupby("Stock Name").last().reset_index()
    latest_ref = df_1d.groupby("Stock Name").last().reset_index()

    peak_sel_set   = set(latest_sel.loc[latest_sel["Diff_Peak"]   == "Short", "Stock Name"])
    peak_ref_set   = set(latest_ref.loc[latest_ref["Diff_Peak"]   == "Short", "Stock Name"])
    trough_sel_set = set(latest_sel.loc[latest_sel["Diff_Trough"] == "LONG",  "Stock Name"])
    trough_ref_set = set(latest_ref.loc[latest_ref["Diff_Trough"] == "LONG",  "Stock Name"])

    peak_overlap   = sorted(peak_sel_set & peak_ref_set)
    trough_overlap = sorted(trough_sel_set & trough_ref_set)

    sel_lookup = latest_sel.set_index("Stock Name")
    ref_lookup = latest_ref.set_index("Stock Name")

    overlap_rows = []
    for name in peak_overlap:
        overlap_rows.append({
            "Stock Name": name, "Type": "Peak",
            f"{interval} Close": sel_lookup.loc[name, "CLOSE"],
            f"{interval} Date":  sel_lookup.loc[name, "Date"],
            "1D Close": ref_lookup.loc[name, "CLOSE"],
            "1D Date":  ref_lookup.loc[name, "Date"],
        })
    for name in trough_overlap:
        overlap_rows.append({
            "Stock Name": name, "Type": "Trough",
            f"{interval} Close": sel_lookup.loc[name, "CLOSE"],
            f"{interval} Date":  sel_lookup.loc[name, "Date"],
            "1D Close": ref_lookup.loc[name, "CLOSE"],
            "1D Date":  ref_lookup.loc[name, "Date"],
        })

    if overlap_rows:
        overlap_df = pd.DataFrame(overlap_rows)

        def _style_overlap_row(row):
            styles = pd.Series("background-color:#FFFFFF", index=row.index)
            if row["Type"] == "Peak":
                styles["Type"] = "background-color:#FCE3E3;color:#B42318;font-weight:700"
            elif row["Type"] == "Trough":
                styles["Type"] = "background-color:#DFF5E5;color:#1A7A3D;font-weight:700"
            return styles

        overlap_styled = (
            overlap_df.style
            .apply(_style_overlap_row, axis=1)
            .format({f"{interval} Close": "{:,.2f}", "1D Close": "{:,.2f}"}, na_rep="─")
            .set_properties(**{"border": "1px solid #C9DCEF"})
            .set_table_styles([{
                "selector": "th",
                "props": [("background-color","#FFFFFF"), ("color","#00355F"),
                           ("font-size","12px"), ("font-weight","700"),
                           ("border-bottom","2px solid #00355F"),
                           ("border-left","1px solid #C9DCEF"),
                           ("border-right","1px solid #C9DCEF")]
            }])
        )
        st.dataframe(overlap_styled, width='stretch', height=int(38*(len(overlap_df)+1)+3),
                     column_config={"Stock Name": st.column_config.TextColumn(pinned=True)})
        st.caption(f"{len(peak_overlap)} stock(s) show a Peak on both {interval} and 1D · "
                   f"{len(trough_overlap)} stock(s) show a Trough on both {interval} and 1D.")
    else:
        st.caption(f"No stocks currently show a matching Peak or Trough on both {interval} and 1D.")

else:
    # Selected interval already IS 1d — no need for a duplicate reference tab
    render_dashboard_body(df, key_suffix="sel")


# ── Download full dataset ──────────────────────────────────────────────────────
st.markdown("---")
st.markdown('<div class="sec-label">📦 Full Dataset</div>', unsafe_allow_html=True)

_full_export_df = pd.concat([df, df_1d], ignore_index=True) if (need_reference_tab and df_1d is not None) else df

_full_csv = _full_export_df.to_csv(index=False).encode("utf-8")
st.download_button(
    "⬇️  Download Full Dataframe (CSV) — all tickers, all bars, every column",
    _full_csv,
    file_name=f"{list_name}_full_data_{datetime.now(ZoneInfo('Asia/Kolkata')).strftime('%Y%m%d_%H%M')}.csv",
    mime="text/csv",
    width='stretch',
    key="download_full_dataframe",
)
st.caption(f"{len(_full_export_df):,} rows × {len(_full_export_df.columns)} columns"
           + (f" (combines {interval} + 1D reference)" if need_reference_tab and df_1d is not None else f" ({interval})"))


# ── Auto-refresh ──────────────────────────────────────────────────────────────
if auto_refresh:
    st.markdown("<div style='text-align:center;color:#5D7A99;font-size:12px'>"
                "⏱ Auto-refreshing every 5 minutes...</div>", unsafe_allow_html=True)
    time.sleep(300)
    st.cache_data.clear()
    st.rerun()
