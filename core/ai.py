from groq import Groq

MODEL = "llama-3.3-70b-versatile"

SYSTEM_PROMPT = """You are a strict trading discipline coach. Your job is NOT to predict where the market goes — nobody can do that reliably.

Your job is to evaluate whether a trade setup is logical, disciplined, and follows sound risk management. You look for emotional reasoning, rule-breaking, and weak setups. You are honest and direct — you do not sugarcoat bad setups.

Important: you are reviewing the trader's REASONING and DISCIPLINE, not predicting price."""


def analyze_trade(api_key: str, trade: dict, score: int, warnings: list[str]) -> dict:
    """
    Returns a dict with keys: verdict, reasoning, red_flag, coaching_tip, raw
    verdict is one of: TRADE / WAIT / SKIP
    """
    coin = trade.get("coin", "Unknown")
    timeframe = trade.get("timeframe", "Unknown")
    setup = trade.get("setup_type", "Unknown")
    risk = trade.get("risk_percent", 0)
    stop_loss = "Yes" if trade.get("stop_loss") else "No"
    trend = "Yes" if trade.get("trend_aligned") else "No"
    reason = trade.get("entry_reason", "").strip() or "(no reason given)"
    emotion = trade.get("emotion_score", 5)

    rule_warnings = "\n".join(f"- {w}" for w in warnings) if warnings else "- None"

    prompt = f"""Evaluate this trade setup and give me a plain, honest assessment.

TRADE DETAILS:
- Coin: {coin}
- Timeframe: {timeframe}
- Setup type: {setup}
- Trend aligned: {trend}
- Risk per trade: {risk}%
- Stop loss set: {stop_loss}
- Confidence level: {emotion}/10
- Entry reason (in the trader's own words): "{reason}"
- Rule-based score: {score}/10
- Rule violations flagged:
{rule_warnings}

Respond in EXACTLY this format, no extra text:

VERDICT: [TRADE or WAIT or SKIP]
REASONING: [2-3 honest sentences about whether this setup makes sense]
RED FLAG: [The single biggest concern, or "None" if solid]
SUGGESTIONS:
- [Specific suggestion 1 — e.g. "Wait for a close above X before entering"]
- [Specific suggestion 2 — e.g. "Reduce risk to 1% given the current uncertainty"]
- [Specific suggestion 3 — e.g. "Set stop loss below the last swing low at X"]
COACHING TIP: [One short discipline or mindset reminder]"""

    client = Groq(api_key=api_key)
    response = client.chat.completions.create(
        model=MODEL,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": prompt},
        ],
        temperature=0.4,
        max_tokens=300,
    )

    raw = response.choices[0].message.content.strip()
    return _parse_response(raw)


def analyze_coin(api_key: str, coin: dict) -> dict:
    """
    Returns a dict with keys: verdict, reasoning, red_flag, suggestions, coaching_tip, raw
    verdict is one of: BUY / WATCH / AVOID
    """
    change = coin.get("change_24h", 0)
    vol = coin.get("volume", 0)
    vol_fmt = f"${vol/1e9:.2f}B" if vol >= 1e9 else f"${vol/1e6:.1f}M"
    mcap = coin.get("market_cap", 0)
    mcap_fmt = f"${mcap/1e9:.2f}B" if mcap >= 1e9 else f"${mcap/1e6:.1f}M"
    rank = coin.get("rank", 9999)
    rank_label = f"#{rank}" if rank < 9999 else "Unranked (very new)"
    description = coin.get("description", "No description available.")

    prompt = f"""Analyze this trending cryptocurrency and give an honest early investment assessment.

COIN: {coin.get('name')} ({coin.get('symbol')})
Market cap rank: {rank_label}
Price 24h change: {change:+.2f}%
24h Volume: {vol_fmt}
Market cap: {mcap_fmt}
Project description: {description}

You are a crypto analyst assessing whether this coin is worth early investment attention.
Be direct. High volume + rising price on a low-rank coin can mean early momentum.
But also watch for pump-and-dump patterns, lack of fundamentals, or hype with no substance.

Respond in EXACTLY this format, no extra text:

VERDICT: [BUY or WATCH or AVOID]
REASONING: [2-3 honest sentences about the coin's potential and risk]
RED FLAG: [The single biggest risk or concern, or "None" if solid]
SUGGESTIONS:
- [Specific suggestion 1]
- [Specific suggestion 2]
- [Specific suggestion 3]
COACHING TIP: [One short tip about investing in early-stage coins]"""

    client = Groq(api_key=api_key)
    response = client.chat.completions.create(
        model=MODEL,
        messages=[
            {"role": "system", "content": "You are a crypto analyst who gives honest, risk-aware assessments of early-stage cryptocurrency investments. You never hype. You always mention risks."},
            {"role": "user", "content": prompt},
        ],
        temperature=0.4,
        max_tokens=350,
    )

    raw = response.choices[0].message.content.strip()
    result = _parse_response(raw)
    # remap TRADE→BUY, SKIP→AVOID for coin context
    remap = {"TRADE": "BUY", "WAIT": "WATCH", "SKIP": "AVOID"}
    result["verdict"] = remap.get(result["verdict"], result["verdict"])
    return result


def _parse_response(raw: str) -> dict:
    result = {
        "verdict": "WAIT",
        "reasoning": "",
        "red_flag": "",
        "suggestions": [],
        "coaching_tip": "",
        "raw": raw,
    }
    in_suggestions = False
    for line in raw.splitlines():
        stripped = line.strip()
        if stripped.startswith("VERDICT:"):
            in_suggestions = False
            v = stripped.replace("VERDICT:", "").strip().upper()
            result["verdict"] = "SKIP" if "SKIP" in v else "TRADE" if "TRADE" in v else "WAIT"
        elif stripped.startswith("REASONING:"):
            in_suggestions = False
            result["reasoning"] = stripped.replace("REASONING:", "").strip()
        elif stripped.startswith("RED FLAG:"):
            in_suggestions = False
            result["red_flag"] = stripped.replace("RED FLAG:", "").strip()
        elif stripped.startswith("SUGGESTIONS:"):
            in_suggestions = True
        elif stripped.startswith("COACHING TIP:"):
            in_suggestions = False
            result["coaching_tip"] = stripped.replace("COACHING TIP:", "").strip()
        elif in_suggestions and stripped.startswith("-"):
            text = stripped.lstrip("-").strip()
            if text:
                result["suggestions"].append(text)
    return result
