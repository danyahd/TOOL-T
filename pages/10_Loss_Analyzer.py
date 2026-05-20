import streamlit as st
import pandas as pd
import plotly.express as px
from core.database import get_all_trades
from core.ai import analyze_losses

st.set_page_config(page_title="Loss Analyzer", page_icon="🔎", layout="wide")
st.title("🔎 Loss Pattern Analyzer")
st.caption("Turns your trading history into lessons. The more trades you log, the more accurate the analysis.")

groq_key = st.session_state.get("groq_api_key", "")
if not groq_key:
    try:
        groq_key = st.secrets.get("GROQ_API_KEY", "")
    except Exception:
        pass

trades = get_all_trades()
completed = [t for t in trades if t.get("result") in ("Win", "Loss", "Breakeven")]

if not completed:
    st.info("No completed trades found. Log trades in the Checklist and mark their results in the Journal to use this feature.")
    st.stop()

df = pd.DataFrame(completed)
df["profit_loss"] = pd.to_numeric(df["profit_loss"], errors="coerce").fillna(0)
df["emotion_score"] = pd.to_numeric(df["emotion_score"], errors="coerce").fillna(5)
df["trade_score"] = pd.to_numeric(df["trade_score"], errors="coerce").fillna(5)

losses = df[df["result"] == "Loss"]
wins = df[df["result"] == "Win"]
total = len(df)
loss_count = len(losses)
win_count = len(wins)
win_rate = (win_count / total * 100) if total else 0

# ── Overview ─────────────────────────────────────────────────────────────────
st.subheader("Overview")
c1, c2, c3, c4 = st.columns(4)
c1.metric("Total Trades", total)
c2.metric("Win Rate", f"{win_rate:.1f}%", delta_color="normal")
c3.metric("Total Losses", loss_count, delta_color="inverse")
total_pnl = df["profit_loss"].sum()
c4.metric("Total P&L", f"${total_pnl:+.2f}", delta_color="normal")

st.markdown("---")

if loss_count == 0:
    st.success("No losses recorded yet — keep it up!")
    st.stop()

# ── Loss breakdown charts ─────────────────────────────────────────────────────
st.subheader("Where Are Your Losses Coming From?")
col1, col2 = st.columns(2)

with col1:
    st.markdown("**Losses by Coin**")
    coin_losses = losses.groupby("coin").size().reset_index(name="losses")
    fig = px.bar(coin_losses.sort_values("losses", ascending=True),
                 x="losses", y="coin", orientation="h",
                 color="losses", color_continuous_scale="Reds")
    fig.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                      coloraxis_showscale=False, margin=dict(t=0,b=0,l=0,r=0), height=250)
    st.plotly_chart(fig, use_container_width=True)

with col2:
    st.markdown("**Losses by Timeframe**")
    tf_losses = losses.groupby("timeframe").size().reset_index(name="losses")
    fig2 = px.bar(tf_losses.sort_values("losses", ascending=True),
                  x="losses", y="timeframe", orientation="h",
                  color="losses", color_continuous_scale="Reds")
    fig2.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                       coloraxis_showscale=False, margin=dict(t=0,b=0,l=0,r=0), height=250)
    st.plotly_chart(fig2, use_container_width=True)

col3, col4 = st.columns(2)
with col3:
    st.markdown("**Emotion Score on Losses vs Wins**")
    fig3 = px.box(df[df["result"].isin(["Win","Loss"])], x="result", y="emotion_score",
                  color="result", color_discrete_map={"Win": "#22c55e", "Loss": "#ef4444"})
    fig3.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                       showlegend=False, margin=dict(t=0,b=0,l=0,r=0), height=250)
    st.plotly_chart(fig3, use_container_width=True)
    st.caption("High emotion score (8-10) on losses = emotional trading.")

with col4:
    st.markdown("**Trade Score on Losses vs Wins**")
    fig4 = px.box(df[df["result"].isin(["Win","Loss"])], x="result", y="trade_score",
                  color="result", color_discrete_map={"Win": "#22c55e", "Loss": "#ef4444"})
    fig4.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                       showlegend=False, margin=dict(t=0,b=0,l=0,r=0), height=250)
    st.plotly_chart(fig4, use_container_width=True)
    st.caption("Low trade score on wins = luck. Low score on losses = poor setups.")

st.markdown("---")

# ── AI Pattern Analysis ───────────────────────────────────────────────────────
st.subheader("🤖 AI Pattern Analysis")
st.caption("The AI reads your full trading history and tells you exactly what habits are costing you money.")

if groq_key:
    if st.button("Analyze My Loss Patterns", type="primary", use_container_width=True):
        setup_losses = losses.groupby("setup_type").size().to_dict()
        avg_emotion_loss = losses["emotion_score"].mean()
        avg_emotion_win = wins["emotion_score"].mean() if win_count else "N/A"
        avg_score_loss = losses["trade_score"].mean()
        avg_score_win = wins["trade_score"].mean() if win_count else "N/A"
        top_loss_coin = losses.groupby("coin").size().idxmax() if loss_count else "N/A"

        summary = f"""
Total trades: {total} | Wins: {win_count} | Losses: {loss_count} | Win rate: {win_rate:.1f}%
Total P&L: ${total_pnl:.2f}

Losses by setup type: {setup_losses}
Losses by coin: {losses.groupby('coin').size().to_dict()}
Losses by timeframe: {losses.groupby('timeframe').size().to_dict()}

Average emotion score on LOSSES: {avg_emotion_loss:.1f}/10
Average emotion score on WINS: {avg_emotion_win if isinstance(avg_emotion_win, str) else f'{avg_emotion_win:.1f}/10'}

Average trade score on LOSSES: {avg_score_loss:.1f}/10
Average trade score on WINS: {avg_score_win if isinstance(avg_score_win, str) else f'{avg_score_win:.1f}/10'}

Most loss-prone coin: {top_loss_coin}
"""
        with st.spinner("Analyzing your trading patterns..."):
            try:
                analysis = analyze_losses(groq_key, summary)
                st.session_state["loss_analysis"] = analysis
            except Exception as e:
                msg = str(e)
                if "auth" in msg.lower() or "401" in msg:
                    st.error("Invalid Groq API key.")
                else:
                    st.error(f"Analysis failed: {msg}")

    if "loss_analysis" in st.session_state:
        st.markdown(
            f"<div style='background:#1e1e2e;border-left:4px solid #f59e0b;padding:16px;border-radius:6px;line-height:1.8'>"
            f"{st.session_state['loss_analysis'].replace(chr(10), '<br>')}</div>",
            unsafe_allow_html=True,
        )
else:
    st.caption("Add your Groq API key in the Checklist sidebar to enable AI analysis.")

st.markdown("---")
st.subheader("📋 Loss Trade Log")
loss_display = losses[["created_at","coin","timeframe","setup_type","trade_score","emotion_score","profit_loss","entry_reason"]].copy()
loss_display.columns = ["Date","Coin","Timeframe","Setup","Score","Emotion","P&L","Entry Reason"]
st.dataframe(loss_display, use_container_width=True, hide_index=True)
