import streamlit as st
import requests
import plotly.graph_objects as go
from datetime import datetime

st.set_page_config(page_title="Fear & Greed", page_icon="🧠", layout="wide")
st.title("🧠 Fear & Greed Index")
st.caption("The single most important sentiment indicator for crypto. Extreme greed = dangerous time to buy. Extreme fear = potential opportunity.")


@st.cache_data(ttl=3600)
def fetch_fng(limit=30):
    try:
        r = requests.get(f"https://api.alternative.me/fng/?limit={limit}", timeout=10)
        r.raise_for_status()
        return r.json()["data"]
    except Exception:
        return []


data = fetch_fng(30)
if not data:
    st.error("Could not load Fear & Greed data.")
    st.stop()

current = data[0]
value = int(current["value"])
label = current["value_classification"]

# Color based on value
if value <= 25:
    color, emoji, advice = "#ef4444", "😱", "Extreme Fear — market is panicking. Historically a buying opportunity, but only if you've done your research."
elif value <= 45:
    color, emoji, advice = "#f97316", "😟", "Fear — sentiment is negative. Prices may be undervalued. Don't rush — wait for signs of reversal."
elif value <= 55:
    color, emoji, advice = "#f59e0b", "😐", "Neutral — no strong signal either way. Focus on your strategy, not the market mood."
elif value <= 75:
    color, emoji, advice = "#84cc16", "😊", "Greed — market is optimistic. Be cautious — don't chase pumps."
else:
    color, emoji, advice = "#22c55e", "🤑", "Extreme Greed — everyone is buying. This is historically when crashes happen. Be very careful."

# Gauge chart
fig = go.Figure(go.Indicator(
    mode="gauge+number",
    value=value,
    title={"text": f"{emoji} {label}", "font": {"size": 20, "color": color}},
    gauge={
        "axis": {"range": [0, 100], "tickwidth": 1, "tickcolor": "#888"},
        "bar": {"color": color},
        "bgcolor": "#1e1e2e",
        "steps": [
            {"range": [0, 25],  "color": "#3b1010"},
            {"range": [25, 45], "color": "#3b2010"},
            {"range": [45, 55], "color": "#2e2e10"},
            {"range": [55, 75], "color": "#1e3010"},
            {"range": [75, 100],"color": "#103010"},
        ],
        "threshold": {"line": {"color": "white", "width": 3}, "thickness": 0.8, "value": value},
    },
    number={"font": {"size": 48, "color": color}},
))
fig.update_layout(
    height=300,
    paper_bgcolor="rgba(0,0,0,0)",
    font={"color": "#ccc"},
    margin=dict(t=40, b=0, l=40, r=40),
)

col1, col2 = st.columns([1, 1])
with col1:
    st.plotly_chart(fig, use_container_width=True)
with col2:
    st.markdown("### What does this mean for you?")
    st.markdown(f"<div style='background:#1e1e2e;border-left:4px solid {color};padding:14px;border-radius:6px;font-size:1.05em'>{advice}</div>", unsafe_allow_html=True)
    st.markdown("---")
    st.markdown("**The golden rule:** *Be fearful when others are greedy, and greedy when others are fearful.* — Warren Buffett")
    st.caption("The index is updated daily. It combines volatility, market momentum, social media, and Bitcoin dominance.")

# Historical chart
st.markdown("---")
st.subheader("Last 30 Days")

dates = [datetime.fromtimestamp(int(d["timestamp"])) for d in reversed(data)]
values = [int(d["value"]) for d in reversed(data)]
labels = [d["value_classification"] for d in reversed(data)]
colors = []
for v in values:
    if v <= 25:   colors.append("#ef4444")
    elif v <= 45: colors.append("#f97316")
    elif v <= 55: colors.append("#f59e0b")
    elif v <= 75: colors.append("#84cc16")
    else:         colors.append("#22c55e")

fig2 = go.Figure()
fig2.add_trace(go.Bar(
    x=dates, y=values,
    marker_color=colors,
    text=labels,
    textposition="outside",
    textfont=dict(size=9, color="#888"),
    hovertemplate="%{x|%b %d}<br>%{y} — %{text}<extra></extra>",
))
fig2.add_hline(y=25, line_dash="dot", line_color="#ef4444", annotation_text="Extreme Fear", annotation_font_color="#ef4444")
fig2.add_hline(y=75, line_dash="dot", line_color="#22c55e", annotation_text="Extreme Greed", annotation_font_color="#22c55e")
fig2.update_layout(
    height=300,
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)",
    xaxis=dict(showgrid=False, color="#888"),
    yaxis=dict(range=[0, 110], showgrid=True, gridcolor="#333", color="#888"),
    margin=dict(t=10, b=0, l=0, r=0),
    showlegend=False,
)
st.plotly_chart(fig2, use_container_width=True)

st.markdown("---")
st.subheader("📚 How to use this index")
c1, c2, c3 = st.columns(3)
with c1:
    st.markdown("**🚫 Don't do this**")
    st.error("Buy when the index is at 80+ (extreme greed) because everyone else is buying and you fear missing out (FOMO)")
with c2:
    st.markdown("**✅ Do this instead**")
    st.success("Wait for fear (below 40) to consider entering. Use your checklist. Never skip risk management.")
with c3:
    st.markdown("**🧘 The mindset**")
    st.info("Most beginners lose because they follow the crowd. This index shows you what the crowd is feeling — so you can think independently.")
