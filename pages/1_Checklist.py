import streamlit as st
from core.database import init_db, save_trade
from core.scoring import score_trade, risk_label
from core.ai import analyze_trade

st.set_page_config(page_title="Trade Checklist", page_icon="✅", layout="wide")

init_db()

# --- API key setup (sidebar) ---
with st.sidebar:
    st.subheader("AI Settings")
    api_key = st.text_input(
        "Groq API Key",
        type="password",
        placeholder="gsk_...",
        help="Free at console.groq.com → API Keys",
        value=st.session_state.get("groq_api_key", "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"),
    )
    if api_key:
        st.session_state["groq_api_key"] = api_key
        st.success("API key saved for this session.")
    else:
        st.info("Add your free Groq API key to enable AI analysis.\nGet one at console.groq.com")

st.title("✅ Trade Checklist")
st.caption("Fill this out before every single trade. No exceptions.")

col1, col2 = st.columns(2)

with col1:
    coin = st.selectbox("Coin", ["BTC", "ETH", "BNB", "SOL", "XRP", "AVAX", "LINK", "ADA", "MATIC", "ARB", "OP"])
    timeframe = st.selectbox("Timeframe", ["1h", "4h", "Daily"])
    setup_type = st.selectbox(
        "Setup Type",
        ["Pullback", "Support bounce", "Trend continuation", "Breakout"],
    )
    trend_aligned = st.checkbox("My entry aligns with the overall trend", value=True)

with col2:
    risk_percent = st.slider("Risk %", min_value=0.1, max_value=5.0, value=2.0, step=0.1)
    stop_loss = st.radio("Stop loss set?", ["Yes", "No"], horizontal=True) == "Yes"
    entry_price = st.number_input("Entry price (optional)", min_value=0.0, value=0.0, format="%.4f")
    emotion_score = st.slider(
        "Confidence level (1 = uncertain, 10 = very confident)",
        min_value=1, max_value=10, value=7
    )

entry_reason = st.text_area(
    "Why are you entering this trade?",
    placeholder="e.g. BTC pulled back to the 4h EMA after a strong uptrend, volume dropped on the pullback — looking for continuation.",
    height=90,
)

# ── Beginner Warnings ─────────────────────────────────────────────────────────
beginner_tips = []

if setup_type == "Breakout":
    beginner_tips.append((
        "warning",
        "Breakout trading — the most common beginner trap",
        "Most breakouts fail and reverse. By the time price breaks a level, the traders who planned it are already in profit and looking to sell. You end up buying their exit. Breakouts that work usually retest the broken level first — wait for that retest instead of chasing the initial break."
    ))

if not stop_loss:
    beginner_tips.append((
        "error",
        "No stop loss — this is how accounts get wiped",
        "A stop loss is not optional. Without one, a single bad trade can lose 20%, 50%, or everything if the market moves hard against you. Every professional trader uses stop losses — not because they expect to lose, but because they know they could be wrong."
    ))

if risk_percent > 2:
    beginner_tips.append((
        "warning",
        f"Risk is {risk_percent}% — above your own rule",
        f"At {risk_percent}% risk, just 10 losing trades in a row wipes {min(100, risk_percent * 10):.0f}% of your account. At 2%, those same 10 losses only cost 20% and you can recover. High risk feels fine when you're winning. It feels catastrophic when you're not."
    ))

if timeframe == "1h":
    beginner_tips.append((
        "info",
        "1h timeframe — more noise, harder to read",
        "The 1h chart is full of fake signals and random noise. As a beginner, the 4h or Daily chart gives you cleaner setups with less stress. You don't need to trade every hour — one good setup per week on the 4h beats five bad ones on the 1h."
    ))

if not trend_aligned:
    beginner_tips.append((
        "warning",
        "Counter-trend trade — swimming against the current",
        "Trading against the trend is an advanced technique. The trend exists because there are more buyers (or sellers) than the other side. Fighting that requires a very specific reason. As a beginner, the rule is simple: only trade in the direction of the trend."
    ))

if emotion_score >= 9:
    beginner_tips.append((
        "warning",
        "Very high confidence — watch for overconfidence bias",
        "The trades that feel the most certain are often the most dangerous. High confidence can make you skip your checklist, increase your risk, or ignore warning signs. The market does not care how confident you are. Run the process regardless of how good it feels."
    ))

reason_stripped = entry_reason.strip()
if reason_stripped and len(reason_stripped) < 20:
    beginner_tips.append((
        "warning",
        "Entry reason too vague",
        "\"Looks good\" or \"going up\" is not a reason. A real entry reason explains: what pattern you see, what timeframe, what confirms the setup, and where you're wrong (your stop). If you can't write one sentence explaining all of that, you don't have a setup — you have a feeling."
    ))

if beginner_tips:
    st.subheader("Beginner Tips")
    for tip_type, title, explanation in beginner_tips:
        with st.expander(f"{'⚠️' if tip_type == 'warning' else '🚨' if tip_type == 'error' else 'ℹ️'}  {title}"):
            st.markdown(explanation)

st.divider()

trade = {
    "coin": coin,
    "timeframe": timeframe,
    "setup_type": setup_type,
    "trend_aligned": trend_aligned,
    "risk_percent": risk_percent,
    "stop_loss": stop_loss,
    "entry_reason": entry_reason,
    "entry_price": entry_price if entry_price > 0 else None,
    "emotion_score": emotion_score,
}

score, good_points, warnings = score_trade(trade)
level, level_icon = risk_label(score)

# --- Rule-based score ---
col_score, col_feedback = st.columns([1, 2])

with col_score:
    st.markdown("### Trade Score")
    color = "#22c55e" if score >= 8 else "#f59e0b" if score >= 6 else "#ef4444"
    st.markdown(
        f"<p style='font-size:80px;font-weight:bold;color:{color};margin:0'>{score}"
        f"<span style='font-size:32px;color:#888'>/10</span></p>",
        unsafe_allow_html=True,
    )
    st.markdown(f"**Risk Level:** {level_icon} {level}")

with col_feedback:
    if good_points:
        st.markdown("**Good**")
        for g in good_points:
            st.markdown(f"- ✅ {g}")
    if warnings:
        st.markdown("**Concerns**")
        for w in warnings:
            st.warning(w)

st.divider()

if score < 4:
    st.error("🚨 Trade score too low. Sit this one out.")
elif score < 6:
    st.warning("⚠️ Significant concerns. Review carefully before entering.")
else:
    st.success("Trade looks acceptable. Enter with discipline.")

# --- AI Analysis ---
st.subheader("🤖 AI Coach Analysis")

groq_key = st.session_state.get("groq_api_key", "")

if not groq_key:
    st.info("Add your Groq API key in the sidebar to get AI analysis.")
else:
    if st.button("Analyze with AI", type="primary", use_container_width=True):
        with st.spinner("AI is reviewing your setup..."):
            try:
                result = analyze_trade(groq_key, trade, score, warnings)

                verdict = result["verdict"]
                if verdict == "TRADE":
                    st.success("### Verdict: TRADE ✅")
                elif verdict == "WAIT":
                    st.warning("### Verdict: WAIT ⏳")
                else:
                    st.error("### Verdict: SKIP ❌")

                col_a, col_b = st.columns(2)

                with col_a:
                    st.markdown("**Reasoning**")
                    st.markdown(result["reasoning"])

                    if result["red_flag"] and result["red_flag"].lower() != "none":
                        st.markdown("**Red Flag**")
                        st.error(result["red_flag"])

                with col_b:
                    if result["suggestions"]:
                        st.markdown("**Suggestions**")
                        for s in result["suggestions"]:
                            st.markdown(f"- 💡 {s}")

                    if result["coaching_tip"]:
                        st.markdown("**Coaching Tip**")
                        st.info(result["coaching_tip"])

                st.caption("AI reviews your reasoning and discipline — not the market. Final call is always yours.")

            except Exception as e:
                st.error(f"AI error: {e}")
                st.caption("Check your API key or internet connection.")

st.divider()

col_save, col_skip = st.columns(2)

with col_save:
    if st.button("Save to Journal", use_container_width=True):
        tid = save_trade({**trade, "trade_score": score})
        st.success(f"Saved. Trade ID: #{tid}")

with col_skip:
    if st.button("Skip This Trade", use_container_width=True):
        st.info("Good call. The best traders sit out bad setups.")
