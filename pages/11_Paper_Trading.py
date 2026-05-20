import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
from core.database import save_paper_trade, get_paper_trades, reset_paper_trades
from core.market_data import get_prices, COINS

st.set_page_config(page_title="Paper Trading", page_icon="📝", layout="wide")
st.title("📝 Paper Trading Simulator")
st.caption("Practice buying and selling with **fake money** — no real risk. Learn how trading works before using real funds.")

STARTING_CASH = 10_000.0


@st.cache_data(ttl=60)
def get_crypto_prices():
    raw = get_prices()
    return {sym: raw.get(cid, {}).get("usd", 0) for sym, cid in COINS.items()}


@st.cache_data(ttl=60)
def get_stock_price(ticker: str) -> float:
    try:
        return yf.Ticker(ticker).fast_info.last_price or 0
    except Exception:
        return 0


def compute_portfolio(trades: list) -> dict:
    cash = STARTING_CASH
    holdings = {}
    for t in trades:
        sym = t["symbol"]
        qty = t["quantity"]
        total = t["total"]
        if t["action"] == "BUY":
            cash -= total
            holdings[sym] = holdings.get(sym, {"qty": 0, "avg_price": 0, "type": t["asset_type"]})
            prev_qty = holdings[sym]["qty"]
            prev_avg = holdings[sym]["avg_price"]
            new_qty = prev_qty + qty
            holdings[sym]["avg_price"] = ((prev_avg * prev_qty) + total) / new_qty if new_qty else 0
            holdings[sym]["qty"] = new_qty
        elif t["action"] == "SELL":
            cash += total
            if sym in holdings:
                holdings[sym]["qty"] -= qty
                if holdings[sym]["qty"] <= 0:
                    del holdings[sym]
    return {"cash": cash, "holdings": holdings}


# Load data
trades = get_paper_trades()
portfolio = compute_portfolio(trades)
cash = portfolio["cash"]
holdings = portfolio["holdings"]

# Get current prices for all holdings
crypto_prices = get_crypto_prices()

def current_price(sym, asset_type):
    if asset_type == "Crypto":
        return crypto_prices.get(sym, 0)
    return get_stock_price(sym)

holdings_value = sum(
    h["qty"] * current_price(sym, h["type"])
    for sym, h in holdings.items()
)
total_value = cash + holdings_value
pnl = total_value - STARTING_CASH
pnl_pct = (pnl / STARTING_CASH) * 100

# ── Portfolio summary ─────────────────────────────────────────────────────────
c1, c2, c3, c4 = st.columns(4)
c1.metric("Portfolio Value", f"${total_value:,.2f}", f"{pnl_pct:+.2f}%", delta_color="normal")
c2.metric("Cash Available", f"${cash:,.2f}")
c3.metric("Holdings Value", f"${holdings_value:,.2f}")
c4.metric("Total P&L", f"${pnl:+.2f}", delta_color="normal")

st.markdown("---")

# ── Trade form ────────────────────────────────────────────────────────────────
st.subheader("Place a Trade")
col1, col2 = st.columns(2)

with col1:
    asset_type = st.radio("Asset type", ["Crypto", "Stock"], horizontal=True)
    if asset_type == "Crypto":
        symbol = st.selectbox("Symbol", list(COINS.keys()))
        price = crypto_prices.get(symbol, 0)
    else:
        symbol = st.text_input("Stock ticker (e.g. AAPL, NVDA)", "AAPL").upper().strip()
        price = get_stock_price(symbol) if symbol else 0

    if price:
        st.caption(f"Current price: **${price:,.4f}**" if price < 1 else f"Current price: **${price:,.2f}**")
    else:
        st.caption("Price unavailable")

with col2:
    action = st.radio("Action", ["BUY", "SELL"], horizontal=True)
    amount_type = st.radio("Enter by", ["Dollar amount ($)", "Quantity"], horizontal=True)

    if amount_type == "Dollar amount ($)":
        dollar_amt = st.number_input("Amount (USD)", min_value=1.0, value=100.0, step=10.0)
        quantity = dollar_amt / price if price else 0
    else:
        quantity = st.number_input("Quantity", min_value=0.0001, value=1.0, step=0.1, format="%.4f")
        dollar_amt = quantity * price

    total_cost = quantity * price if price else 0
    st.caption(f"Total: **${total_cost:,.2f}**")

    can_trade = True
    if action == "BUY" and total_cost > cash:
        st.error(f"Not enough cash. You have ${cash:,.2f}")
        can_trade = False
    elif action == "SELL":
        held = holdings.get(symbol, {}).get("qty", 0)
        if quantity > held:
            st.error(f"You only hold {held:.4f} {symbol}")
            can_trade = False

    if st.button(f"{'Buy' if action == 'BUY' else 'Sell'} {symbol}", type="primary", disabled=not (can_trade and price > 0)):
        save_paper_trade(symbol, asset_type, action, quantity, price)
        st.success(f"{'Bought' if action == 'BUY' else 'Sold'} {quantity:.4f} {symbol} at ${price:,.2f}")
        st.cache_data.clear()
        st.rerun()

st.markdown("---")

# ── Holdings ──────────────────────────────────────────────────────────────────
if holdings:
    st.subheader("Current Holdings")
    rows = []
    for sym, h in holdings.items():
        cur = current_price(sym, h["type"])
        val = h["qty"] * cur
        cost = h["qty"] * h["avg_price"]
        pnl_h = val - cost
        pnl_pct_h = (pnl_h / cost * 100) if cost else 0
        rows.append({
            "Symbol": sym,
            "Type": h["type"],
            "Quantity": f"{h['qty']:.4f}",
            "Avg Buy Price": f"${h['avg_price']:,.4f}" if h['avg_price'] < 1 else f"${h['avg_price']:,.2f}",
            "Current Price": f"${cur:,.4f}" if cur < 1 else f"${cur:,.2f}",
            "Value": f"${val:,.2f}",
            "P&L": f"${pnl_h:+.2f} ({pnl_pct_h:+.1f}%)",
        })
    st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)
    st.markdown("---")

# ── Trade history ─────────────────────────────────────────────────────────────
if trades:
    st.subheader("Trade History")
    hist_df = pd.DataFrame(trades)[["created_at","symbol","asset_type","action","quantity","price","total"]]
    hist_df.columns = ["Date","Symbol","Type","Action","Quantity","Price","Total"]
    st.dataframe(hist_df, use_container_width=True, hide_index=True)

    st.markdown("---")
    if st.button("🔄 Reset Paper Portfolio", type="secondary"):
        reset_paper_trades()
        st.cache_data.clear()
        st.success("Portfolio reset to $10,000")
        st.rerun()
else:
    st.info("No trades yet. Place your first paper trade above to start practicing!")

st.markdown("---")
st.markdown("""
**📚 How to use Paper Trading to learn:**
- Start with the same amount you plan to invest for real
- Follow your checklist rules — don't skip them just because it's fake money
- Track why each trade went right or wrong in the Journal
- Only move to real money when you're consistently profitable here
""")
