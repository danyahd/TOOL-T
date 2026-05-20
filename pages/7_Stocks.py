import streamlit as st
import yfinance as yf
import plotly.graph_objects as go
import pandas as pd
from core.ai import analyze_stock

st.set_page_config(page_title="Stocks", page_icon="📈", layout="wide")
st.title("📈 Stocks & Indices")
st.caption("Real-time data for major indices and stocks via Yahoo Finance.")

groq_key = st.session_state.get("groq_api_key", "")
if not groq_key:
    try:
        groq_key = st.secrets.get("GROQ_API_KEY", "")
    except Exception:
        pass

INDICES = {
    "S&P 500": "^GSPC",
    "NASDAQ": "^IXIC",
    "Dow Jones": "^DJI",
    "Russell 2000": "^RUT",
    "VIX (Fear Index)": "^VIX",
}

TOP_STOCKS = {
    "Apple": "AAPL",
    "NVIDIA": "NVDA",
    "Microsoft": "MSFT",
    "Tesla": "TSLA",
    "Amazon": "AMZN",
    "Meta": "META",
    "Google": "GOOGL",
    "Berkshire Hathaway": "BRK-B",
    "JPMorgan": "JPM",
    "Netflix": "NFLX",
}


@st.cache_data(ttl=300)
def fetch_quote(ticker: str) -> dict:
    try:
        t = yf.Ticker(ticker)
        info = t.fast_info
        prev = info.previous_close or 1
        price = info.last_price or 0
        change = price - prev
        change_pct = (change / prev) * 100
        return {
            "price": price,
            "change": change,
            "change_pct": change_pct,
            "volume": getattr(info, "three_month_average_volume", 0) or 0,
            "market_cap": getattr(info, "market_cap", 0) or 0,
        }
    except Exception:
        return {}


@st.cache_data(ttl=300)
def fetch_history(ticker: str, period: str = "1mo") -> pd.DataFrame:
    try:
        return yf.Ticker(ticker).history(period=period)
    except Exception:
        return pd.DataFrame()


def fmt_price(p):
    return f"${p:,.2f}"


def fmt_change(c, pct):
    arrow = "▲" if c >= 0 else "▼"
    color = "green" if c >= 0 else "red"
    return f"<span style='color:{color}'>{arrow} {abs(c):.2f} ({abs(pct):.2f}%)</span>"


# ── Indices ──────────────────────────────────────────────────────────────────
st.subheader("Major Indices")
cols = st.columns(len(INDICES))
for col, (name, ticker) in zip(cols, INDICES.items()):
    q = fetch_quote(ticker)
    if q:
        delta = q["change_pct"]
        with col:
            st.metric(
                name,
                fmt_price(q["price"]),
                f"{delta:+.2f}%",
                delta_color="normal",
            )
    else:
        col.caption(f"{name}: N/A")

st.markdown("---")

# ── Stock Lookup ──────────────────────────────────────────────────────────────
st.subheader("Stock Lookup")
tab1, tab2 = st.tabs(["Top Stocks", "Search Any Ticker"])

with tab1:
    selected = st.multiselect(
        "Select stocks to view",
        list(TOP_STOCKS.keys()),
        default=["Apple", "NVIDIA", "Tesla"],
    )
    tickers = {name: TOP_STOCKS[name] for name in selected}

with tab2:
    custom = st.text_input("Enter ticker symbol (e.g. AAPL, AMD, SHOP)", "").upper().strip()
    if custom:
        tickers = {custom: custom}

if not tickers:
    st.info("Select at least one stock above.")
    st.stop()

# ── Chart period ──────────────────────────────────────────────────────────────
period = st.radio("Chart period", ["5d", "1mo", "3mo", "6mo", "1y"], horizontal=True, index=1)

for name, ticker in tickers.items():
    q = fetch_quote(ticker)
    hist = fetch_history(ticker, period)

    if not q:
        st.warning(f"Could not fetch data for {ticker}.")
        continue

    with st.container():
        c1, c2, c3, c4 = st.columns([2, 1.5, 1.5, 1.5])
        with c1:
            label = name if name != ticker else ticker
            st.markdown(f"### {label} `{ticker}`")
        with c2:
            st.metric("Price", fmt_price(q["price"]))
        with c3:
            st.metric("24h Change", f"{q['change_pct']:+.2f}%", delta_color="normal")
        with c4:
            mcap = q["market_cap"]
            mcap_fmt = f"${mcap/1e12:.2f}T" if mcap >= 1e12 else f"${mcap/1e9:.1f}B" if mcap >= 1e9 else "N/A"
            st.metric("Market Cap", mcap_fmt)

        if not hist.empty:
            fig = go.Figure()
            is_up = q["change_pct"] >= 0
            color = "#22c55e" if is_up else "#ef4444"
            fill_color = "rgba(34,197,94,0.08)" if is_up else "rgba(239,68,68,0.08)"
            fig.add_trace(go.Scatter(
                x=hist.index,
                y=hist["Close"],
                mode="lines",
                line=dict(color=color, width=2),
                fill="tozeroy",
                fillcolor=fill_color,
                name="Price",
            ))
            fig.update_layout(
                height=220,
                margin=dict(l=0, r=0, t=10, b=0),
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)",
                xaxis=dict(showgrid=False, color="#888"),
                yaxis=dict(showgrid=True, gridcolor="#333", color="#888"),
                showlegend=False,
            )
            st.plotly_chart(fig, use_container_width=True)

        # AI Analysis
        ai_key = f"stock_analysis_{ticker}"
        if groq_key:
            if st.button(f"🤖 Analyze {ticker}", key=f"btn_{ticker}"):
                with st.spinner(f"Analyzing {ticker}..."):
                    try:
                        result = analyze_stock(
                            groq_key,
                            ticker=ticker,
                            name=name,
                            price=q["price"],
                            change_pct=q["change_pct"],
                            market_cap=q["market_cap"],
                            volume=q["volume"],
                        )
                        st.session_state[ai_key] = result
                    except Exception as e:
                        msg = str(e)
                        if "auth" in msg.lower() or "401" in msg:
                            st.error("Invalid Groq API key. Update it in Streamlit Secrets.")
                        else:
                            st.error(f"AI analysis failed: {msg}")

        if ai_key in st.session_state:
            result = st.session_state[ai_key]
            verdict = result.get("verdict", "WATCH")
            styles = {"BUY": ("#22c55e", "🟢"), "WATCH": ("#f59e0b", "🟡"), "AVOID": ("#ef4444", "🔴")}
            color, emoji = styles.get(verdict, ("#f59e0b", "🟡"))
            st.markdown(
                f"<div style='background:#1e1e2e;border-left:4px solid {color};padding:12px 16px;border-radius:6px;margin-top:8px'>"
                f"<strong style='color:{color};font-size:1.1em'>{emoji} {verdict}</strong><br><br>"
                f"<strong>Analysis:</strong> {result.get('reasoning','')}<br><br>"
                f"<strong>Red Flag:</strong> {result.get('red_flag','None')}<br><br>"
                + ("".join(f"<li>{s}</li>" for s in result.get("suggestions", [])))
                + f"<strong>Tip:</strong> {result.get('coaching_tip','')}</div>",
                unsafe_allow_html=True,
            )
        elif not groq_key:
            st.caption("Add your Groq API key in the Checklist sidebar to enable AI analysis.")

        st.markdown("---")
