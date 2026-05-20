import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from core.database import init_db
from core.market_data import COINS, get_prices, get_ohlc, classify_trend, classify_volume, get_support_resistance

st.set_page_config(
    page_title="Trading Assistant",
    page_icon="📊",
    layout="wide",
)

init_db()


@st.cache_data(ttl=300)
def cached_prices():
    return get_prices()


@st.cache_data(ttl=300)
def cached_ohlc(coin_id: str, days: int):
    return get_ohlc(coin_id, days=days)


def calculate_rsi(closes: pd.Series, period: int = 14) -> pd.Series:
    delta = closes.diff()
    gain = delta.clip(lower=0)
    loss = -delta.clip(upper=0)
    avg_gain = gain.ewm(com=period - 1, adjust=False).mean()
    avg_loss = loss.ewm(com=period - 1, adjust=False).mean()
    rs = avg_gain / avg_loss
    return 100 - (100 / (1 + rs))


def find_swing_levels(df: pd.DataFrame, n: int = 3) -> tuple[list, list]:
    """Find significant swing highs (resistance) and swing lows (support)."""
    supports, resistances = [], []
    for i in range(n, len(df) - n):
        window_highs = df["high"].iloc[i - n: i + n + 1]
        window_lows = df["low"].iloc[i - n: i + n + 1]
        if df["high"].iloc[i] == window_highs.max():
            resistances.append(df["high"].iloc[i])
        if df["low"].iloc[i] == window_lows.min():
            supports.append(df["low"].iloc[i])
    return supports, resistances


def ema_trend(close: float, ema20: float, ema50: float) -> tuple[str, str]:
    if close > ema20 > ema50:
        return "Uptrend", "#22c55e"
    elif close < ema20 < ema50:
        return "Downtrend", "#ef4444"
    return "Sideways", "#f59e0b"


def entry_signal(price: float, change: float, ohlc: list) -> tuple[str, str, str, list]:
    """
    Returns (signal, emoji, color, reasons).
    signal: GREEN / YELLOW / RED
    Scores each condition and totals them up.
    """
    if not ohlc or price <= 0:
        return "UNKNOWN", "⚪", "#888", ["Not enough data"]

    df = pd.DataFrame(ohlc, columns=["ts", "open", "high", "low", "close"])
    df["ema20"] = df["close"].ewm(span=20, adjust=False).mean()
    df["ema50"] = df["close"].ewm(span=50, adjust=False).mean()
    df["rsi"] = calculate_rsi(df["close"])

    ema20 = float(df["ema20"].iloc[-1])
    ema50 = float(df["ema50"].iloc[-1])
    rsi = float(df["rsi"].iloc[-1])
    support, resistance = get_support_resistance(ohlc)

    score = 0
    reasons = []

    # EMA alignment
    if price > ema20 > ema50:
        score += 2
        reasons.append("✅ EMA aligned — uptrend")
    elif price < ema20 < ema50:
        score -= 2
        reasons.append("🔴 EMA bearish — downtrend")
    else:
        reasons.append("⚠️ EMAs mixed — no clear trend")

    # RSI
    if 40 <= rsi <= 60:
        score += 2
        reasons.append(f"✅ RSI neutral ({rsi:.0f}) — not stretched")
    elif rsi < 30:
        score += 1
        reasons.append(f"💡 RSI oversold ({rsi:.0f}) — possible reversal zone")
    elif rsi > 70:
        score -= 2
        reasons.append(f"🔴 RSI overbought ({rsi:.0f}) — bad time to buy")
    else:
        score += 1
        reasons.append(f"⚠️ RSI at {rsi:.0f} — acceptable")

    # Support / resistance proximity
    if support and resistance:
        dist_sup = (price - support) / price * 100
        dist_res = (resistance - price) / price * 100
        if dist_sup <= 5:
            score += 2
            reasons.append(f"✅ Near support ({dist_sup:.1f}% below) — good entry zone")
        elif dist_res <= 3:
            score -= 2
            reasons.append(f"🔴 Near resistance ({dist_res:.1f}% above) — bad entry zone")
        else:
            reasons.append(f"⚠️ Mid-range (sup {dist_sup:.1f}% / res {dist_res:.1f}%)")

    # 24h momentum
    if 0 < change <= 5:
        score += 1
        reasons.append(f"✅ Healthy momentum (+{change:.1f}%)")
    elif change > 5:
        score -= 1
        reasons.append(f"⚠️ Strong move already (+{change:.1f}%) — late entry risk")
    elif change < -5:
        score -= 1
        reasons.append(f"⚠️ Sharp drop ({change:.1f}%) — wait for stabilisation")

    if score >= 5:
        return "GREEN", "🟢", "#22c55e", reasons
    elif score >= 2:
        return "YELLOW", "🟡", "#f59e0b", reasons
    else:
        return "RED", "🔴", "#ef4444", reasons


# ── Market Snapshot ───────────────────────────────────────────────────────────
st.title("📊 Trading Assistant")
st.caption("Your personal discipline tool — not a prediction machine.")

st.subheader("Market Snapshot")

with st.spinner("Fetching prices..."):
    prices = cached_prices()

if not prices:
    st.error("Could not fetch market data. Check your internet connection.")
    st.stop()

coin_items = list(COINS.items())
COLS_PER_ROW = 4

for row_start in range(0, len(coin_items), COLS_PER_ROW):
    row_items = coin_items[row_start: row_start + COLS_PER_ROW]
    cols = st.columns(COLS_PER_ROW)

    for col_idx, (symbol, coin_id) in enumerate(row_items):
        data = prices.get(coin_id, {})
        price = data.get("usd", 0)
        change = data.get("usd_24h_change", 0) or 0
        vol = data.get("usd_24h_vol", 0) or 0

        trend, trend_icon = classify_trend(change)
        vol_str = classify_volume(vol, symbol)

        ohlc = cached_ohlc(coin_id, 7)
        support, resistance = get_support_resistance(ohlc)

        with cols[col_idx]:
            with st.container(border=True):
                st.markdown(f"### {symbol}")
                st.metric("Price", f"${price:,.2f}", f"{change:+.2f}%")
                st.markdown(f"**Trend:** {trend} {trend_icon}")
                st.markdown(f"**Volume:** {vol_str}")

                if support and resistance and price > 0:
                    dist_sup = (price - support) / price * 100
                    dist_res = (resistance - price) / price * 100
                    st.markdown(f"**Support:** ${support:,.2f} — {dist_sup:.1f}% below")
                    st.markdown(f"**Resistance:** ${resistance:,.2f} — {dist_res:.1f}% above")

# ── Entry Signal Traffic Light ────────────────────────────────────────────────
st.divider()
st.subheader("Entry Signal")
st.caption("Based on EMA alignment, RSI, support/resistance proximity, and 24h momentum.")

sig_rows = [coin_items[i: i + COLS_PER_ROW] for i in range(0, len(coin_items), COLS_PER_ROW)]

for row_items in sig_rows:
    cols = st.columns(COLS_PER_ROW)
    for col_idx, (symbol, coin_id) in enumerate(row_items):
        data = prices.get(coin_id, {})
        price = data.get("usd", 0)
        change = data.get("usd_24h_change", 0) or 0
        ohlc = cached_ohlc(coin_id, 7)

        signal, emoji, color, reasons = entry_signal(price, change, ohlc)

        with cols[col_idx]:
            with st.container(border=True):
                st.markdown(
                    f"<div style='display:flex;align-items:center;gap:8px'>"
                    f"<span style='font-size:28px'>{emoji}</span>"
                    f"<span style='font-size:20px;font-weight:bold'>{symbol}</span>"
                    f"<span style='color:{color};font-weight:bold'>{signal}</span>"
                    f"</div>",
                    unsafe_allow_html=True,
                )
                for r in reasons:
                    st.markdown(f"<small>{r}</small>", unsafe_allow_html=True)

# ── Price Chart ───────────────────────────────────────────────────────────────
st.divider()
st.subheader("Price Chart")

ctrl1, ctrl2, ctrl3 = st.columns([2, 2, 1])
with ctrl1:
    selected_symbol = st.selectbox("Coin", list(COINS.keys()), label_visibility="collapsed")
with ctrl2:
    days_options = {"7 days (4h candles)": 7, "14 days (4h candles)": 14, "30 days (daily)": 30, "90 days (daily)": 90}
    selected_tf_label = st.selectbox("Timeframe", list(days_options.keys()), label_visibility="collapsed")
with ctrl3:
    show_ema = st.checkbox("Show EMAs", value=True)

selected_days = days_options[selected_tf_label]
selected_coin_id = COINS[selected_symbol]

with st.spinner(f"Loading {selected_symbol} chart..."):
    ohlc_data = cached_ohlc(selected_coin_id, selected_days)

if not ohlc_data:
    st.warning("Could not load chart data. Try again in a moment.")
else:
    df = pd.DataFrame(ohlc_data, columns=["timestamp", "open", "high", "low", "close"])
    df["date"] = pd.to_datetime(df["timestamp"], unit="ms")

    # Indicators
    df["ema20"] = df["close"].ewm(span=20, adjust=False).mean()
    df["ema50"] = df["close"].ewm(span=50, adjust=False).mean()
    df["rsi"] = calculate_rsi(df["close"])

    current_price = (prices.get(selected_coin_id) or {}).get("usd", float(df["close"].iloc[-1]))
    last_ema20 = float(df["ema20"].iloc[-1])
    last_ema50 = float(df["ema50"].iloc[-1])
    last_rsi = float(df["rsi"].iloc[-1])

    trend_label, trend_color = ema_trend(current_price, last_ema20, last_ema50)

    # Swing-based support / resistance (up to 2 levels each)
    raw_supports, raw_resistances = find_swing_levels(df)
    key_supports = sorted([s for s in raw_supports if s < current_price], reverse=True)[:2]
    key_resistances = sorted([r for r in raw_resistances if r > current_price])[:2]

    # ── Build chart ──
    fig = make_subplots(
        rows=2, cols=1,
        shared_xaxes=True,
        row_heights=[0.72, 0.28],
        vertical_spacing=0.04,
    )

    # Candlesticks
    fig.add_trace(go.Candlestick(
        x=df["date"],
        open=df["open"], high=df["high"], low=df["low"], close=df["close"],
        name=selected_symbol,
        increasing_line_color="#22c55e", decreasing_line_color="#ef4444",
        increasing_fillcolor="#22c55e", decreasing_fillcolor="#ef4444",
    ), row=1, col=1)

    # EMAs
    if show_ema:
        fig.add_trace(go.Scatter(
            x=df["date"], y=df["ema20"],
            name="EMA 20", line=dict(color="#f97316", width=1.5),
        ), row=1, col=1)
        fig.add_trace(go.Scatter(
            x=df["date"], y=df["ema50"],
            name="EMA 50", line=dict(color="#60a5fa", width=1.5),
        ), row=1, col=1)

    # Support levels
    support_colors = ["#3b82f6", "#93c5fd"]
    for i, lvl in enumerate(key_supports):
        dist = (current_price - lvl) / current_price * 100
        fig.add_hline(
            y=lvl, line_dash="dash",
            line_color=support_colors[i], line_width=1.5,
            annotation_text=f"S{i+1} ${lvl:,.2f} ({dist:.1f}% below)",
            annotation_position="bottom left",
            annotation_font_color=support_colors[i],
            row=1, col=1,
        )

    # Resistance levels
    resistance_colors = ["#f59e0b", "#fcd34d"]
    for i, lvl in enumerate(key_resistances):
        dist = (lvl - current_price) / current_price * 100
        fig.add_hline(
            y=lvl, line_dash="dash",
            line_color=resistance_colors[i], line_width=1.5,
            annotation_text=f"R{i+1} ${lvl:,.2f} ({dist:.1f}% above)",
            annotation_position="top left",
            annotation_font_color=resistance_colors[i],
            row=1, col=1,
        )

    # Current price
    fig.add_hline(
        y=current_price, line_dash="dot",
        line_color="#a855f7", line_width=1,
        annotation_text=f"Now ${current_price:,.2f}",
        annotation_position="top right",
        annotation_font_color="#a855f7",
        row=1, col=1,
    )

    # Trend label annotation (top-left of chart)
    fig.add_annotation(
        text=f"<b>{trend_label}</b>",
        xref="paper", yref="paper",
        x=0.01, y=0.97,
        showarrow=False,
        font=dict(size=15, color=trend_color),
        bgcolor="rgba(0,0,0,0.35)",
        bordercolor=trend_color,
        borderwidth=1,
        borderpad=5,
    )

    # RSI subplot
    fig.add_trace(go.Scatter(
        x=df["date"], y=df["rsi"],
        name="RSI", line=dict(color="#c084fc", width=1.5),
        fill="tozeroy", fillcolor="rgba(192,132,252,0.08)",
    ), row=2, col=1)

    # RSI reference lines
    for level, color, label in [(70, "#ef4444", "Overbought 70"), (30, "#22c55e", "Oversold 30")]:
        fig.add_hline(
            y=level, line_dash="dot", line_color=color, line_width=1,
            annotation_text=label, annotation_position="right",
            annotation_font_color=color, row=2, col=1,
        )

    fig.update_layout(
        height=620,
        xaxis_rangeslider_visible=False,
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        xaxis2=dict(gridcolor="rgba(128,128,128,0.15)"),
        yaxis=dict(gridcolor="rgba(128,128,128,0.15)", tickprefix="$"),
        yaxis2=dict(gridcolor="rgba(128,128,128,0.15)", range=[0, 100], title="RSI"),
        margin=dict(l=0, r=0, t=10, b=0),
        legend=dict(orientation="h", yanchor="bottom", y=1.01, xanchor="left", x=0),
    )

    st.plotly_chart(fig, use_container_width=True)

    # ── Info row below chart ──
    rsi_label = "Overbought ⚠️" if last_rsi > 70 else "Oversold 💡" if last_rsi < 30 else "Neutral"
    ema_signal = "Price above both EMAs — bullish" if current_price > last_ema20 > last_ema50 \
        else "Price below both EMAs — bearish" if current_price < last_ema20 < last_ema50 \
        else "Mixed EMAs — no clear trend"

    m1, m2, m3, m4, m5 = st.columns(5)
    m1.metric("Trend (EMA)", trend_label)
    m2.metric("EMA 20", f"${last_ema20:,.2f}")
    m3.metric("EMA 50", f"${last_ema50:,.2f}")
    m4.metric("RSI (14)", f"{last_rsi:.1f}", rsi_label)
    if key_supports:
        dist = (current_price - key_supports[0]) / current_price * 100
        m5.metric("Nearest Support", f"${key_supports[0]:,.2f}", f"{dist:.1f}% below")
    elif key_resistances:
        dist = (key_resistances[0] - current_price) / current_price * 100
        m5.metric("Nearest Resistance", f"${key_resistances[0]:,.2f}", f"{dist:.1f}% above", delta_color="inverse")

    st.caption(f"EMA signal: {ema_signal}")

    with st.expander("📖 Chart Legend"):
        st.table({
            "Element": [
                "Green / Red candles",
                "Orange line (EMA 20)",
                "Blue line (EMA 50)",
                "Blue dashed lines (S1, S2)",
                "Yellow dashed lines (R1, R2)",
                "Purple dotted line",
                "Trend label (top-left badge)",
                "RSI panel (bottom)",
            ],
            "What it shows": [
                "Price action",
                "Short-term trend",
                "Medium-term trend",
                "2 nearest swing support levels with % distance",
                "2 nearest swing resistance levels with % distance",
                "Current live price",
                "Uptrend / Downtrend / Sideways based on EMAs",
                "Overbought >70, Oversold <30",
            ],
        })

st.divider()
st.info("Use the sidebar to open the Trade Checklist, Journal, or Weekly Review.")
