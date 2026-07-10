"""Technical & fundamental scores (0-100). Descriptive only — never
exposed as buy/sell signals in the UI."""
import pandas as pd


def _rsi(closes: pd.Series, window: int = 14) -> float:
    delta = closes.diff()
    gain = delta.clip(lower=0).rolling(window).mean()
    loss = (-delta.clip(upper=0)).rolling(window).mean()
    rs = gain / loss.replace(0, 1e-9)
    rsi = 100 - 100 / (1 + rs)
    return float(rsi.iloc[-1]) if not rsi.empty else 50.0


def technical_score(df: pd.DataFrame) -> dict:
    """Score trend, momentum, and position vs moving averages.
    Returns {'score': int, 'drivers': [str], 'facts': {...}}."""
    out = {"score": 50, "drivers": [], "facts": {}}
    if df is None or df.empty or len(df) < 30 or "Close" not in df:
        out["drivers"].append("Insufficient history for a full read")
        return out
    closes = df["Close"]
    price = float(closes.iloc[-1])
    pts, total = 0, 0
    drivers = []

    ma50 = closes.rolling(50).mean().iloc[-1] if len(closes) >= 50 else None
    ma200 = closes.rolling(200).mean().iloc[-1] if len(closes) >= 200 else None

    if ma200 is not None and not pd.isna(ma200):
        total += 30
        if price > ma200:
            pts += 30
            drivers.append("Price above 200-day moving average")
        else:
            drivers.append("Price below 200-day moving average")
        out["facts"]["above_200dma"] = price > ma200
    if ma50 is not None and not pd.isna(ma50):
        total += 20
        if price > ma50:
            pts += 20
            drivers.append("Price above 50-day moving average")
        else:
            drivers.append("Price below 50-day moving average")

    rsi = _rsi(closes)
    out["facts"]["rsi"] = rsi
    total += 25
    if 45 <= rsi <= 70:
        pts += 25
        drivers.append(f"Firm momentum (RSI {rsi:.0f})")
    elif rsi > 70:
        pts += 12
        drivers.append(f"Elevated momentum (RSI {rsi:.0f})")
    elif rsi >= 30:
        pts += 10
        drivers.append(f"Soft momentum (RSI {rsi:.0f})")
    else:
        drivers.append(f"Depressed momentum (RSI {rsi:.0f})")

    hi, lo = float(closes.max()), float(closes.min())
    pos = (price - lo) / (hi - lo) if hi > lo else 0.5
    out["facts"]["range_pos"] = pos
    total += 25
    pts += int(pos * 25)
    drivers.append(f"At {pos:.0%} of the period's price range")

    out["score"] = int(round(pts / total * 100)) if total else 50
    out["drivers"] = drivers
    return out


def _tier(value, cuts, labels):
    for cut, label in zip(cuts, labels):
        if value < cut:
            return label
    return labels[-1]


def fundamental_score(info: dict) -> dict:
    """Score margins, returns, leverage, growth from a yfinance info dict."""
    out = {"score": 50, "drivers": [], "facts": {}}
    pts, total = 0, 0
    drivers = []

    roe = info.get("returnOnEquity")
    if roe is not None:
        total += 25
        out["facts"]["roe"] = roe
        if roe > 0.20:
            pts += 25
        elif roe > 0.10:
            pts += 17
        elif roe > 0:
            pts += 8
        drivers.append(f"ROE {roe:.0%}")

    margins = info.get("profitMargins")
    if margins is not None:
        total += 25
        out["facts"]["margin"] = margins
        if margins > 0.20:
            pts += 25
        elif margins > 0.10:
            pts += 17
        elif margins > 0:
            pts += 8
        drivers.append(f"Net margin {margins:.0%}")

    dte = info.get("debtToEquity")
    if dte is not None:
        total += 25
        out["facts"]["dte"] = dte
        if dte < 50:
            pts += 25
        elif dte < 100:
            pts += 17
        elif dte < 200:
            pts += 8
        drivers.append(f"Debt/Equity {dte:.0f}%")

    growth = info.get("revenueGrowth")
    if growth is not None:
        total += 25
        out["facts"]["rev_growth"] = growth
        if growth > 0.15:
            pts += 25
        elif growth > 0.05:
            pts += 17
        elif growth > 0:
            pts += 8
        drivers.append(f"Revenue growth {growth:+.0%}")

    out["score"] = int(round(pts / total * 100)) if total else 50
    out["drivers"] = drivers or ["Limited fundamental data available"]
    return out


def at_a_glance(info: dict, tech: dict) -> list:
    """The 7 neutral-language chips: (label, value) tuples."""
    chips = []
    if "above_200dma" in tech.get("facts", {}):
        chips.append(("Trend", "Above 200DMA" if tech["facts"]["above_200dma"]
                      else "Below 200DMA"))
    rsi = tech.get("facts", {}).get("rsi")
    if rsi is not None:
        bucket = ("Elevated" if rsi > 70 else
                  "Firm" if rsi >= 55 else
                  "Neutral" if rsi >= 45 else
                  "Soft" if rsi >= 30 else "Depressed")
        chips.append(("Momentum", f"{bucket} (RSI {rsi:.0f})"))
    pos = tech.get("facts", {}).get("range_pos")
    if pos is not None:
        chips.append(("52-week range", f"{pos:.0%} of range"))
    roe = info.get("returnOnEquity")
    if roe is not None:
        tier = "High" if roe > 0.20 else "Moderate" if roe > 0.10 else "Low"
        chips.append(("Profitability", f"{tier} (ROE {roe:.0%})"))
    dte = info.get("debtToEquity")
    if dte is not None:
        tier = ("Low" if dte < 50 else "Moderate" if dte < 100 else
                "Elevated" if dte < 200 else "High")
        chips.append(("Leverage", f"{tier} (D/E {dte:.0f}%)"))
    beta = info.get("beta")
    if beta is not None:
        tier = ("Higher than market" if beta > 1.15 else
                "Near market" if beta > 0.85 else "Lower than market")
        chips.append(("Volatility", f"{tier} (β {beta:.2f})"))
    pe = info.get("trailingPE")
    if pe is not None:
        tier = ("Low multiple" if pe < 15 else
                "Moderate multiple" if pe < 30 else "High multiple")
        chips.append(("Valuation", f"{tier} (P/E {pe:.1f})"))
    return chips
