import streamlit as st
import plotly.graph_objects as go

st.set_page_config(page_title="Calculator", page_icon="🧮", layout="wide")

st.title("🧮 Risk / Reward Calculator")
st.caption("Fill this out for every trade. If the numbers don't make sense, don't take the trade.")

st.divider()

col1, col2 = st.columns(2)

with col1:
    st.subheader("Your Account")
    account_balance = st.number_input("Account balance ($)", min_value=1.0, value=1000.0, step=10.0)
    risk_percent = st.slider("Risk per trade (%)", min_value=0.1, max_value=5.0, value=2.0, step=0.1,
                             help="Your rule is max 2%. Don't change this just because a trade looks good.")

with col2:
    st.subheader("Trade Levels")
    entry_price = st.number_input("Entry price ($)", min_value=0.0, value=0.0, format="%.4f")
    stop_loss = st.number_input("Stop loss price ($)", min_value=0.0, value=0.0, format="%.4f")
    target_price = st.number_input("Target price ($)", min_value=0.0, value=0.0, format="%.4f")

st.divider()

# ── Validation ────────────────────────────────────────────────────────────────
inputs_valid = entry_price > 0 and stop_loss > 0 and target_price > 0

if not inputs_valid:
    st.info("Enter your entry price, stop loss, and target price above to see the calculations.")
    st.stop()

is_long = entry_price > stop_loss

if is_long and target_price <= entry_price:
    st.error("Target price must be above entry price for a long trade.")
    st.stop()

if not is_long and target_price >= entry_price:
    st.error("Target price must be below entry price for a short trade.")
    st.stop()

if is_long and stop_loss >= entry_price:
    st.error("Stop loss must be below entry price for a long trade.")
    st.stop()

# ── Calculations ──────────────────────────────────────────────────────────────
risk_per_unit = abs(entry_price - stop_loss)
reward_per_unit = abs(target_price - entry_price)
rr_ratio = reward_per_unit / risk_per_unit if risk_per_unit > 0 else 0

max_loss_usd = account_balance * (risk_percent / 100)
position_size_usd = max_loss_usd / (risk_per_unit / entry_price) if entry_price > 0 else 0
coins_to_buy = position_size_usd / entry_price if entry_price > 0 else 0
potential_profit_usd = coins_to_buy * reward_per_unit

# ── Results ───────────────────────────────────────────────────────────────────
rr_color = "#22c55e" if rr_ratio >= 2 else "#f59e0b" if rr_ratio >= 1 else "#ef4444"
rr_verdict = "Good" if rr_ratio >= 2 else "Acceptable" if rr_ratio >= 1.5 else "Poor — skip this trade" if rr_ratio >= 1 else "Bad — never take this"

col_rr, col_metrics = st.columns([1, 2])

with col_rr:
    st.markdown("### Risk / Reward Ratio")
    st.markdown(
        f"<p style='font-size:72px;font-weight:bold;color:{rr_color};margin:0'>{rr_ratio:.1f}R</p>",
        unsafe_allow_html=True,
    )
    st.markdown(f"**Verdict:** <span style='color:{rr_color}'>{rr_verdict}</span>", unsafe_allow_html=True)
    st.caption("Minimum to aim for: 2R (risk $1 to make $2)")

with col_metrics:
    st.markdown("### Trade Breakdown")
    m1, m2 = st.columns(2)
    m1.metric("Max Loss", f"-${max_loss_usd:,.2f}", f"{risk_percent}% of account")
    m2.metric("Potential Profit", f"+${potential_profit_usd:,.2f}", f"{potential_profit_usd/account_balance*100:.1f}% of account")
    m1.metric("Position Size", f"${position_size_usd:,.2f}", "amount to put in")
    m2.metric("Coins to Buy", f"{coins_to_buy:.6f}", f"@ ${entry_price:,.4f}")

st.divider()

# ── Visual trade diagram ──────────────────────────────────────────────────────
st.subheader("Trade Diagram")

levels = sorted([stop_loss, entry_price, target_price])
padding = (max(levels) - min(levels)) * 0.3
y_min = min(levels) - padding
y_max = max(levels) + padding

fig = go.Figure()

# Zone fills
fig.add_hrect(y0=entry_price, y1=target_price,
              fillcolor="rgba(34,197,94,0.12)", line_width=0, annotation_text="Profit Zone")
fig.add_hrect(y0=stop_loss, y1=entry_price,
              fillcolor="rgba(239,68,68,0.12)", line_width=0, annotation_text="Risk Zone")

# Level lines
for price, color, label, dash in [
    (target_price, "#22c55e", f"Target  ${target_price:,.4f}", "solid"),
    (entry_price, "#a855f7", f"Entry  ${entry_price:,.4f}", "solid"),
    (stop_loss, "#ef4444", f"Stop Loss  ${stop_loss:,.4f}", "dash"),
]:
    fig.add_hline(y=price, line_color=color, line_dash=dash, line_width=2,
                  annotation_text=label, annotation_position="right",
                  annotation_font_color=color)

fig.update_layout(
    height=320,
    plot_bgcolor="rgba(0,0,0,0)",
    paper_bgcolor="rgba(0,0,0,0)",
    yaxis=dict(range=[y_min, y_max], tickprefix="$", gridcolor="rgba(128,128,128,0.15)"),
    xaxis=dict(visible=False),
    margin=dict(l=0, r=120, t=10, b=10),
    showlegend=False,
)

st.plotly_chart(fig, use_container_width=True)

# ── Beginner tip ──────────────────────────────────────────────────────────────
st.divider()

if rr_ratio < 1:
    st.error("🚨 You are risking more than you can make. This trade makes no mathematical sense. Skip it.")
elif rr_ratio < 2:
    st.warning("⚠️ R:R is below 2:1. Even with a 50% win rate you will slowly lose money at this ratio. Consider a better target or tighter stop.")
else:
    st.success(f"✅ R:R of {rr_ratio:.1f}:1 means you only need to win {100/(1+rr_ratio):.0f}% of trades to be profitable.")

with st.expander("📖 What does R:R mean?"):
    st.markdown("""
**Risk/Reward Ratio (R:R)** tells you how much you stand to make compared to how much you risk.

- **2R** = You risk $1 to potentially make $2
- **3R** = You risk $1 to potentially make $3

**Why it matters:**

With a 2:1 R:R, you only need to win **34% of your trades** to break even.
With a 1:1 R:R, you need to win **50%** just to break even — and that's before fees.

**Rule of thumb:** Never take a trade with less than 2:1 R:R. Ever.
""")
