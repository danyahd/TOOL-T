import streamlit as st
import pandas as pd
import plotly.express as px
from core.database import init_db, get_all_trades

st.set_page_config(page_title="Weekly Review", page_icon="📈", layout="wide")

init_db()

st.title("📈 Weekly Review")
st.caption("Patterns don't lie. Your data will coach you better than any influencer.")

trades = get_all_trades()

if not trades:
    st.info("No trades yet. Log some trades to see your patterns.")
    st.stop()

df = pd.DataFrame(trades)
df["created_at"] = pd.to_datetime(df["created_at"])
closed = df[df["result"].notna()].copy()

if closed.empty:
    st.warning("No closed trades yet. Close trades in the Journal first.")
    st.stop()

# --- Top stats ---
total = len(closed)
wins = (closed["result"] == "win").sum()
losses = (closed["result"] == "loss").sum()
win_rate = wins / total * 100 if total else 0
avg_risk = closed["risk_percent"].mean()
sl_discipline = closed["stop_loss"].mean() * 100

col1, col2, col3, col4 = st.columns(4)
col1.metric("Win Rate", f"{win_rate:.0f}%", f"{wins}W / {losses}L")
col2.metric("Avg Risk / Trade", f"{avg_risk:.1f}%", help="Target: ≤2%")
col3.metric("Stop Loss Rate", f"{sl_discipline:.0f}%", help="% of trades with a stop loss set")
col4.metric("Total Closed Trades", total)

st.divider()

col_left, col_right = st.columns(2)

with col_left:
    st.subheader("By Setup Type")
    setup_stats = (
        closed.groupby("setup_type")
        .agg(trades=("id", "count"), wins=("result", lambda x: (x == "win").sum()), avg_pl=("profit_loss", "mean"))
        .reset_index()
    )
    setup_stats["Win Rate %"] = (setup_stats["wins"] / setup_stats["trades"] * 100).round(1)
    setup_stats["Avg P&L %"] = setup_stats["avg_pl"].round(2)
    st.dataframe(
        setup_stats[["setup_type", "trades", "Win Rate %", "Avg P&L %"]].rename(
            columns={"setup_type": "Setup", "trades": "Trades"}
        ),
        use_container_width=True,
        hide_index=True,
    )

with col_right:
    st.subheader("By Timeframe")
    tf_stats = (
        closed.groupby("timeframe")
        .agg(
            trades=("id", "count"),
            win_rate=("result", lambda x: round((x == "win").sum() / len(x) * 100, 1)),
            avg_risk=("risk_percent", "mean"),
        )
        .reset_index()
        .rename(columns={"timeframe": "TF", "trades": "Trades", "win_rate": "Win Rate %", "avg_risk": "Avg Risk %"})
    )
    st.dataframe(tf_stats, use_container_width=True, hide_index=True)

# --- Cumulative P&L chart ---
if closed["profit_loss"].notna().any():
    st.subheader("Cumulative P&L")
    sorted_closed = closed.sort_values("created_at").copy()
    sorted_closed["Cumulative P&L %"] = sorted_closed["profit_loss"].cumsum()
    fig = px.line(
        sorted_closed,
        x="created_at",
        y="Cumulative P&L %",
        markers=True,
        color_discrete_sequence=["#22c55e"],
    )
    fig.update_layout(xaxis_title="Date", plot_bgcolor="rgba(0,0,0,0)", margin=dict(l=0, r=0))
    st.plotly_chart(fig, use_container_width=True)

st.divider()

# --- Auto-generated insights ---
st.subheader("Insights")
insights = []

breakout_trades = closed[closed["setup_type"] == "Breakout"]
if len(breakout_trades) >= 2:
    bwr = (breakout_trades["result"] == "win").mean() * 100
    if bwr < 50:
        insights.append(f"⚠️ Your breakout trades win only {bwr:.0f}% of the time. Consider avoiding them.")

if sl_discipline < 100:
    missing_sl = closed[closed["stop_loss"] == 0]
    sl_losses = (missing_sl["result"] == "loss").sum()
    insights.append(f"🚨 {100 - sl_discipline:.0f}% of trades had no stop loss. {sl_losses} of those were losses.")

over_risk = closed[closed["risk_percent"] > 2]
if len(over_risk) > 0:
    insights.append(f"⚠️ {len(over_risk)} trades broke your 2% risk rule.")

if "emotion_score" in closed.columns and closed["emotion_score"].notna().any():
    high_conf = closed[closed["emotion_score"] >= 8]
    if len(high_conf) >= 2:
        hc_wr = (high_conf["result"] == "win").mean() * 100
        insights.append(f"📊 High-confidence trades (emotion 8+) have a {hc_wr:.0f}% win rate.")

if insights:
    for line in insights:
        st.markdown(line)
else:
    st.success("No rule violations detected. Keep it up.")

st.divider()

# --- Rules reminder ---
st.subheader("Your Rules")
for rule in [
    "No meme coins",
    "No influencer trades",
    "Max 2% risk per trade",
    "No leverage",
    "No revenge trading",
]:
    st.markdown(f"❌ {rule}")
