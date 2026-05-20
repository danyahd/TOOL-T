import streamlit as st
from core.market_data import get_trending
from core.ai import analyze_coin

st.set_page_config(page_title="Early Alpha", page_icon="🔍", layout="wide")
st.title("🔍 Early Alpha — Trending Coins")
st.caption("Top trending coins on CoinGecko right now, sorted by momentum. High volume + rising price = strong market interest.")

groq_key = st.session_state.get("groq_api_key", "")
if not groq_key:
    try:
        groq_key = st.secrets.get("GROQ_API_KEY", "")
    except Exception:
        pass

with st.spinner("Fetching trending data..."):
    coins = get_trending()

if not coins:
    st.error("Could not fetch trending data. Check your CoinGecko API key.")
    st.stop()

# Filters
col1, col2 = st.columns(2)
with col1:
    min_change = st.slider("Min 24h change (%)", -20, 50, 0)
with col2:
    sort_by = st.selectbox("Sort by", ["24h Change", "Volume", "Market Cap Rank"])

filtered = [c for c in coins if c["change_24h"] >= min_change]

if sort_by == "24h Change":
    filtered.sort(key=lambda x: x["change_24h"], reverse=True)
elif sort_by == "Volume":
    filtered.sort(key=lambda x: x["volume"], reverse=True)
else:
    filtered.sort(key=lambda x: x["rank"])

if not filtered:
    st.info("No coins match the current filter.")
    st.stop()

st.markdown("---")

VERDICT_STYLE = {
    "BUY":   ("🟢", "#22c55e", "Early Buy Signal"),
    "WATCH": ("🟡", "#f59e0b", "Watch Closely"),
    "AVOID": ("🔴", "#ef4444", "Avoid"),
}

for coin in filtered:
    change = coin["change_24h"]
    if change >= 5:
        momentum_badge = "🟢 Strong Momentum"
    elif change >= 0:
        momentum_badge = "🟡 Mild Uptrend"
    else:
        momentum_badge = "🔴 Declining"

    with st.container():
        c1, c2, c3, c4, c5 = st.columns([2, 1.5, 1.5, 1.5, 1])
        with c1:
            rank_label = f"#{coin['rank']}" if coin["rank"] < 9999 else "Unranked"
            st.markdown(f"**{coin['name']}** `{coin['symbol']}` &nbsp; <span style='color:#888;font-size:0.8em'>{rank_label}</span>", unsafe_allow_html=True)
            if coin["description"]:
                st.caption(coin["description"][:160] + "..." if len(coin["description"]) > 160 else coin["description"])
        with c2:
            price = coin["price"]
            price_fmt = f"${price:,.4f}" if price < 1 else f"${price:,.2f}"
            st.metric("Price", price_fmt)
        with c3:
            st.metric("24h Change", f"{change:+.2f}%", delta_color="normal")
        with c4:
            vol = coin["volume"]
            vol_fmt = f"${vol/1e9:.2f}B" if vol >= 1e9 else f"${vol/1e6:.1f}M" if vol >= 1e6 else f"${vol:,.0f}"
            st.metric("Volume", vol_fmt)
        with c5:
            st.markdown(f"<div style='padding-top:20px'>{momentum_badge}</div>", unsafe_allow_html=True)

        if coin["sparkline"]:
            st.image(coin["sparkline"], width=200)

        # AI Analysis
        key = f"analysis_{coin['id']}"
        if groq_key:
            if st.button(f"🤖 Analyze {coin['symbol']}", key=f"btn_{coin['id']}"):
                with st.spinner(f"Analyzing {coin['name']}..."):
                    st.session_state[key] = analyze_coin(groq_key, coin)

        if key in st.session_state:
            result = st.session_state[key]
            verdict = result.get("verdict", "WATCH")
            emoji, color, label = VERDICT_STYLE.get(verdict, ("🟡", "#f59e0b", verdict))

            st.markdown(
                f"<div style='background:#1e1e2e;border-left:4px solid {color};padding:12px 16px;border-radius:6px;margin-top:8px'>"
                f"<strong style='color:{color};font-size:1.1em'>{emoji} {label}</strong><br><br>"
                f"<strong>Analysis:</strong> {result.get('reasoning','')}<br><br>"
                f"<strong>Red Flag:</strong> {result.get('red_flag','None')}<br><br>"
                + (
                    "<strong>Suggestions:</strong><ul>"
                    + "".join(f"<li>{s}</li>" for s in result.get("suggestions", []))
                    + "</ul>"
                    if result.get("suggestions") else ""
                )
                + f"<strong>Tip:</strong> {result.get('coaching_tip','')}"
                f"</div>",
                unsafe_allow_html=True,
            )
        elif not groq_key:
            st.caption("Add your Groq API key in the Checklist sidebar to enable AI analysis.")

        st.markdown("---")
