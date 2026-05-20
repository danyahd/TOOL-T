def score_trade(trade: dict) -> tuple[int, list[str], list[str]]:
    """Returns (score 0-10, good_points, warnings)."""
    score = 0
    good: list[str] = []
    warnings: list[str] = []

    # Stop loss (critical — no stop = major deduction)
    if trade.get("stop_loss"):
        score += 2
        good.append("Stop loss is set")
    else:
        warnings.append("No stop loss — this alone can wipe an account")

    # Risk %
    risk = trade.get("risk_percent", 0)
    if risk <= 1:
        score += 3
        good.append(f"Risk is very conservative ({risk}%)")
    elif risk <= 2:
        score += 2
        good.append(f"Risk within your 2% rule ({risk}%)")
    elif risk <= 3:
        score += 1
        warnings.append(f"Risk is above your 2% rule ({risk}%) — bending your own rules")
    else:
        warnings.append(f"Risk is {risk}% — this breaks your rules")

    # Setup quality
    setup = trade.get("setup_type", "")
    if setup in ("Pullback", "Support bounce"):
        score += 2
        good.append(f"{setup} is a disciplined, patient setup")
    elif setup == "Trend continuation":
        score += 1
        good.append("Trend continuation is acceptable")
    elif setup == "Breakout":
        warnings.append("Breakout entries are often late and emotional — are you chasing?")

    # Trend alignment
    if trade.get("trend_aligned"):
        score += 1
        good.append("Entry is aligned with the trend")
    else:
        warnings.append("Counter-trend entry — higher risk, make sure you have a strong reason")

    # Entry reason quality
    reason = (trade.get("entry_reason") or "").strip()
    if len(reason) >= 15:
        score += 1
        good.append("You wrote a clear entry reason")
    else:
        warnings.append("Entry reason is too vague — write at least one full sentence")

    # Timeframe quality
    if trade.get("timeframe") in ("4h", "Daily"):
        score += 1
        good.append(f"Higher timeframe ({trade['timeframe']}) = cleaner signals")

    return max(0, min(10, score)), good, warnings


def risk_label(score: int) -> tuple[str, str]:
    if score >= 8:
        return "Low", "🟢"
    elif score >= 6:
        return "Medium", "🟡"
    elif score >= 4:
        return "High", "🟠"
    return "Very High", "🔴"
