import streamlit as st

st.set_page_config(page_title="Glossary", page_icon="📚", layout="wide")

st.title("📚 Glossary")
st.caption("Every term used in this app — explained in plain language. No jargon.")

search = st.text_input("Search a term...", placeholder="e.g. RSI, stop loss, pullback")

GLOSSARY = {
    "Chart Basics": {
        "Candlestick": {
            "short": "A bar on the chart showing open, high, low, and close price for a time period.",
            "detail": """
Each candle tells you 4 things about that time period:
- **Open** — where price started
- **Close** — where price ended
- **High** — the highest point reached
- **Low** — the lowest point reached

**Green candle** = price closed higher than it opened (buyers won that period).
**Red candle** = price closed lower than it opened (sellers won that period).

The thin lines above/below the body are called **wicks** — they show how far price moved before reversing.
""",
            "example": "A green 4h candle means in that 4-hour period, buyers pushed price up.",
        },
        "Support": {
            "short": "A price level where price has bounced up from before — buyers tend to step in here.",
            "detail": """
Support is a price zone where demand is strong enough to stop price from falling further.

Think of it as a floor. When price drops to that level, buyers see it as cheap and start buying — pushing price back up.

**Why it matters:** Buying near support gives you a tight stop loss (just below the level) and a good risk/reward ratio. If support breaks, price often falls fast.

**Important:** Support is not a magic line. It breaks sometimes. Always have a stop loss below it.
""",
            "example": "BTC keeps bouncing off $90,000. That's a support level.",
        },
        "Resistance": {
            "short": "A price level where price has been rejected before — sellers tend to appear here.",
            "detail": """
Resistance is the opposite of support — it's a ceiling where sellers come in and push price back down.

When price approaches resistance, traders who bought lower start selling to take profit. This selling pressure pushes price down.

**Why it matters for beginners:** Never buy right into resistance. You're essentially buying at a price where other people are selling. Bad timing.

**When resistance breaks:** If price pushes through resistance with strong volume, that level often becomes new support.
""",
            "example": "ETH keeps getting rejected at $3,500. That's resistance.",
        },
        "Trend": {
            "short": "The general direction price is moving — up, down, or sideways.",
            "detail": """
- **Uptrend** — price makes higher highs and higher lows. Buyers are in control.
- **Downtrend** — price makes lower highs and lower lows. Sellers are in control.
- **Sideways** — price moves between two levels with no clear direction.

**The golden rule:** Trade in the direction of the trend. Don't fight it.

If BTC is in an uptrend, only look for buy setups. Fighting an uptrend by shorting is like swimming against a strong current — exhausting and usually losing.
""",
            "example": "BTC has been making higher highs for 3 months — it's in an uptrend.",
        },
        "Timeframe": {
            "short": "How long each candle on the chart represents.",
            "detail": """
Common timeframes:
- **1h** — each candle = 1 hour. Lots of noise, many false signals. Harder for beginners.
- **4h** — each candle = 4 hours. Good balance of detail and clarity. Recommended for beginners.
- **Daily** — each candle = 1 day. Very clean signals. Best for understanding the big picture.

**Rule of thumb:** Always check the Daily chart first to understand the big picture, then use 4h to time your entry.

Higher timeframes = cleaner signals = less stress = better for beginners.
""",
            "example": "On the 4h chart, you can see BTC is clearly in an uptrend. On the 1h, it's hard to tell.",
        },
    },
    "Indicators": {
        "EMA 20 (Orange line)": {
            "short": "The average price of the last 20 candles, updated continuously. Shows short-term trend.",
            "detail": """
EMA stands for **Exponential Moving Average**. It smooths out price noise to show the trend direction.

**EMA 20** reacts quickly to price changes — it's the short-term trend line.

**How to use it:**
- Price above EMA 20 = short-term bullish
- Price below EMA 20 = short-term bearish
- Price bouncing off EMA 20 in an uptrend = potential buy setup (pullback to EMA)

The EMA 20 is often used as a dynamic support/resistance level in trending markets.
""",
            "example": "In an uptrend, BTC keeps pulling back to the EMA 20 and bouncing. Traders buy those touches.",
        },
        "EMA 50 (Blue line)": {
            "short": "The average price of the last 50 candles. Shows medium-term trend.",
            "detail": """
The EMA 50 moves slower than the EMA 20 — it filters out more noise.

**How to use it:**
- Price above EMA 50 = medium-term uptrend
- Price below EMA 50 = medium-term downtrend

**EMA alignment signal (most important):**
- Price > EMA 20 > EMA 50 = **Strong uptrend** — look for buys
- Price < EMA 20 < EMA 50 = **Strong downtrend** — avoid longs
- EMA 20 crossing above EMA 50 = potential trend change to bullish

As a beginner, only trade longs when price is above both EMAs.
""",
            "example": "BTC is above both EMA 20 and EMA 50. Both EMAs are sloping up. Strong uptrend confirmed.",
        },
        "RSI": {
            "short": "Measures if price has moved too far too fast — shows overbought or oversold conditions.",
            "detail": """
RSI (Relative Strength Index) ranges from 0 to 100:

- **Above 70** = Overbought — price has risen a lot, may be due for a pullback. Bad time to buy.
- **Below 30** = Oversold — price has fallen a lot, may be due for a bounce. Potential buy zone.
- **40–60** = Neutral — no extreme conditions. Good entry zone if setup is right.

**Important:** Overbought doesn't mean price will crash immediately. In strong uptrends, RSI can stay above 70 for weeks. Use it as a warning, not a signal alone.

**For beginners:** Don't buy when RSI is above 70. Wait for it to cool down to 40-60 range.
""",
            "example": "RSI hit 78 after BTC pumped 20% in 3 days. Buying here means buying into exhaustion.",
        },
    },
    "Risk Management": {
        "Stop Loss": {
            "short": "A price level where your trade automatically closes to limit your loss.",
            "detail": """
A stop loss is your exit if you're wrong. You set it before you enter the trade.

**Example:** You buy BTC at $100,000. You place a stop loss at $97,000. If price drops to $97,000, the trade closes automatically — you lose $3,000 instead of potentially much more.

**Why it's non-negotiable:**
Without a stop loss, one bad trade can wipe 30%, 50%, or even your entire account if you freeze and don't exit manually.

**Where to place it:** Below the most recent support level, or below the swing low that would invalidate your trade idea.

Never move your stop loss further away to avoid a loss — that's how small losses become account-destroying losses.
""",
            "example": "Stop loss placed just below the support level at $97,000. If it breaks, the trade idea is wrong.",
        },
        "Risk %": {
            "short": "What percentage of your account you're willing to lose on a single trade.",
            "detail": """
This is the most important number in trading.

**The rule: Max 2% per trade.**

Why? Simple math:
- At 2% risk: 10 losing trades in a row = 20% account loss (recoverable)
- At 5% risk: 10 losing trades in a row = 50% account loss (very hard to recover)
- At 10% risk: 10 losing trades in a row = 65% account loss (near impossible to recover)

Even the best traders in the world lose 40-50% of their trades. The difference is they manage risk so the losses are small and the wins are big.

**This app sets your default to 2%. Don't change it.**
""",
            "example": "$1,000 account × 2% = $20 max loss per trade. That's your stop loss size in dollars.",
        },
        "Risk/Reward Ratio (R:R)": {
            "short": "How much you can make compared to how much you risk. Minimum target: 2:1.",
            "detail": """
R:R tells you if a trade is mathematically worth taking.

**2:1 R:R** means: risk $1 to potentially make $2.

**Why 2:1 minimum:**
At 2:1 R:R, even if you only win 34% of your trades, you break even.
At 1:1 R:R, you need to win 50% just to break even — and that's before fees.

**How to calculate:**
- Distance from entry to target = reward
- Distance from entry to stop loss = risk
- R:R = reward ÷ risk

**Use the Calculator page** to calculate this for every trade before entering.
""",
            "example": "Entry $100, stop $97, target $106. Risk = $3, Reward = $6. R:R = 2:1. Worth taking.",
        },
        "Position Size": {
            "short": "How many coins to buy based on your account size and risk %.",
            "detail": """
Position size answers: "How much do I actually buy?"

**Formula:**
1. Max loss = Account × Risk % (e.g. $1,000 × 2% = $20)
2. Stop distance % = (Entry - Stop) / Entry
3. Position size = Max loss / Stop distance %

**Example:**
- Account: $1,000
- Risk: 2% = $20 max loss
- Entry: $100, Stop: $95 (5% stop distance)
- Position size = $20 / 5% = $400

You buy $400 worth of the coin. If it drops 5% to your stop, you lose $20 — exactly 2% of your account.

**Use the Calculator page** to do this automatically.
""",
            "example": "$1,000 account, 2% risk, 5% stop = $400 position size.",
        },
    },
    "Setup Types": {
        "Pullback": {
            "short": "Price briefly moves against the trend before continuing in the original direction.",
            "detail": """
A pullback is a temporary pause or dip in a trending market.

**In an uptrend:**
Price goes up → pulls back slightly → continues up

This is the safest entry for beginners because:
- You're trading with the trend (not against it)
- You're buying at a lower price than recent highs
- The pullback gives you a natural stop loss level

**How to spot it:** Price is in an uptrend, then pulls back to the EMA 20 or EMA 50, then shows a green candle reversing back up.

**This is the setup you should be looking for as a beginner.**
""",
            "example": "BTC is in an uptrend. It pulls back 5% to the EMA 20 on lower volume, then bounces. That's a pullback entry.",
        },
        "Support Bounce": {
            "short": "Price drops to a known support level and reverses back up.",
            "detail": """
A support bounce is when price falls to a level it has bounced from before, and bounces again.

**Why it works:** Other traders are also watching that support level. When price reaches it, many of them place buy orders there, creating demand that pushes price back up.

**How to trade it:**
1. Identify a clear support level (price has bounced here at least twice before)
2. Wait for price to reach that level
3. Look for a confirmation candle (green candle closing above support)
4. Enter with stop loss just below the support level

**This is one of the best setups for beginners** — clear entry, clear stop, good R:R.
""",
            "example": "ETH has bounced off $2,800 three times. When it drops there again and shows a green candle — that's your entry.",
        },
        "Trend Continuation": {
            "short": "Entering in the direction of an established trend after a brief pause.",
            "detail": """
A trend continuation setup is when you enter a trade in the same direction as the existing trend after price consolidates (moves sideways briefly).

**Pattern:**
Price trends up → moves sideways for a few candles → breaks out of the sideways range → continues up

**Why it's decent for beginners:**
- You're with the trend
- The consolidation gives you a clear entry point
- The stop goes below the consolidation range

**Risk:** If the consolidation breaks downward, you're stopped out. This happens — it's normal.
""",
            "example": "BTC trends up, then consolidates between $100k-$102k for a week. It breaks above $102k — trend continuation entry.",
        },
        "Breakout": {
            "short": "Entering when price breaks through a resistance level. High risk for beginners.",
            "detail": """
A breakout is when price moves above a resistance level it has been stuck under.

**Why beginners should avoid it:**
Most breakouts fail. Price breaks the level, triggers breakout buyers, then reverses back below — trapping those buyers in a losing trade. This is called a **fakeout**.

Professional traders often SELL into breakouts (to the eager buyers) and wait for a retest.

**If you still want to trade breakouts:**
- Wait for the breakout candle to CLOSE above resistance (not just touch it)
- Wait for price to come back and retest the broken level (it often does)
- Enter on the retest with stop below the level

This is significantly safer than buying the initial break.
""",
            "example": "BTC breaks above $105k resistance. Instead of buying immediately, wait for it to pull back to $105k and hold there — then enter.",
        },
    },
    "Psychology": {
        "FOMO (Fear of Missing Out)": {
            "short": "Entering a trade because price is moving fast and you're scared of missing the move.",
            "detail": """
FOMO is the feeling that price is running away from you and you need to get in NOW.

It causes you to:
- Enter without checking your setup
- Skip the checklist
- Buy at the worst possible time (top of a move)
- Risk more than your 2% rule

**What actually happens:** You buy after a big move. The move exhausts. Price pulls back. You're now in a losing trade that you entered for emotional reasons.

**The rule:** If you feel FOMO, do not trade. Sit on your hands. There will always be another setup. The market is not going to stop existing if you miss this move.
""",
            "example": "BTC pumps 15% in one day. You feel like you're missing out and buy the top. Price pulls back 10% the next day.",
        },
        "Revenge Trading": {
            "short": "Taking a trade immediately after a loss to try to make the money back.",
            "detail": """
After losing, your brain wants to "get even" with the market. This is one of the most destructive patterns in trading.

**What happens:**
You lose a trade → you feel frustrated → you take another trade immediately (often bigger risk) to recover the loss → you lose again → now you're down even more.

**Why it doesn't work:**
The market doesn't know you just lost. It doesn't owe you a recovery. Each trade is independent.

**The rule:** After a loss, close the laptop. Take a walk. Do not trade for at least 1 hour — better if it's the rest of the day. Review what went wrong before trading again.

This app tracks your emotion score specifically to help you spot this pattern in your journal.
""",
            "example": "You lose $50 on a BTC trade. Immediately take a bigger SOL trade to recover it. Lose $80 more.",
        },
        "Overconfidence Bias": {
            "short": "Believing you know what the market will do — and taking bigger risks because of it.",
            "detail": """
After a few winning trades, many beginners start to feel like they've figured out the market. This leads to:
- Increasing position sizes
- Skipping the checklist
- Ignoring warning signs
- Taking worse setups

**The reality:** Every trade carries risk regardless of how confident you feel. The best traders in the world are wrong 40-50% of the time. The difference is they manage risk the same way every time — confident or not.

**This app flags confidence scores of 9-10** because extremely high confidence is often a warning sign, not a green light.
""",
            "example": "You win 5 trades in a row and feel unstoppable. You double your position size on the next trade. It's a loser.",
        },
    },
}

# Filter by search
def matches(term: str, data: dict, query: str) -> bool:
    if not query:
        return True
    q = query.lower()
    return (q in term.lower() or
            q in data["short"].lower() or
            q in data["detail"].lower())

for category, terms in GLOSSARY.items():
    filtered = {t: d for t, d in terms.items() if matches(t, d, search)}
    if not filtered:
        continue

    st.subheader(category)
    for term, data in filtered.items():
        with st.expander(f"**{term}** — {data['short']}"):
            st.markdown(data["detail"])
            if data.get("example"):
                st.info(f"**Example:** {data['example']}")
    st.divider()
