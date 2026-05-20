import streamlit as st
import pandas as pd
from core.database import init_db, get_all_trades, update_trade_result

st.set_page_config(page_title="Trade Journal", page_icon="📓", layout="wide")

init_db()

st.title("📓 Trade Journal")

trades = get_all_trades()

if not trades:
    st.info("No trades yet. Use the Trade Checklist to log your first trade.")
    st.stop()

df = pd.DataFrame(trades)
df["created_at"] = pd.to_datetime(df["created_at"])
df["Date"] = df["created_at"].dt.strftime("%Y-%m-%d %H:%M")
df["stop_loss"] = df["stop_loss"].map({1: "Yes", 0: "No"})

# --- Filters ---
col1, col2, col3 = st.columns(3)
with col1:
    coins = df["coin"].unique().tolist()
    coin_filter = st.multiselect("Coin", coins, default=coins)
with col2:
    show_open = st.checkbox("Open trades only")
with col3:
    result_opts = df["result"].dropna().unique().tolist()
    result_filter = st.multiselect("Result", result_opts)

filtered = df[df["coin"].isin(coin_filter)]
if show_open:
    filtered = filtered[filtered["result"].isna()]
if result_filter:
    filtered = filtered[filtered["result"].isin(result_filter) | filtered["result"].isna()]

display = ["Date", "coin", "timeframe", "setup_type", "risk_percent", "stop_loss",
           "trade_score", "result", "profit_loss", "entry_reason"]
display = [c for c in display if c in filtered.columns]

st.dataframe(
    filtered[display].rename(columns={
        "coin": "Coin", "timeframe": "TF", "setup_type": "Setup",
        "risk_percent": "Risk %", "stop_loss": "SL", "trade_score": "Score",
        "result": "Result", "profit_loss": "P&L %", "entry_reason": "Reason",
    }),
    use_container_width=True,
    hide_index=True,
)

st.divider()
st.subheader("Close a Trade")

open_trades = df[df["result"].isna()]

if open_trades.empty:
    st.info("No open trades to close.")
else:
    options = {
        f"#{row['id']} — {row['coin']} {row['timeframe']} ({row['Date']})": row["id"]
        for _, row in open_trades.iterrows()
    }
    selected_label = st.selectbox("Select trade", list(options.keys()))
    selected_id = options[selected_label]

    col1, col2, col3 = st.columns(3)
    with col1:
        exit_price = st.number_input("Exit price", min_value=0.0, format="%.4f")
    with col2:
        result = st.selectbox("Result", ["win", "loss", "breakeven"])
    with col3:
        pl = st.number_input("P&L %", min_value=-100.0, max_value=1000.0, value=0.0, step=0.1)

    if st.button("Close Trade", type="primary"):
        update_trade_result(selected_id, exit_price, result, pl)
        st.success("Trade closed!")
        st.rerun()
