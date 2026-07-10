"""Risk score 0-100: volatility + drawdown + concentration."""
import math

import pandas as pd

RISK_LABELS = [(25, "Conservative"), (50, "Moderate"),
               (75, "Aggressive"), (101, "Very aggressive")]


def risk_label(score: float) -> str:
    for cut, label in RISK_LABELS:
        if score < cut:
            return label
    return "Very aggressive"


def annualized_vol(closes: pd.Series) -> float:
    rets = closes.pct_change().dropna()
    if rets.empty:
        return 0.0
    return float(rets.std() * math.sqrt(252))


def max_drawdown(closes: pd.Series) -> float:
    if closes.empty:
        return 0.0
    peak = closes.cummax()
    dd = (closes / peak - 1).min()
    return abs(float(dd))


def concentration_score(weights: list) -> float:
    """Herfindahl-style concentration from a list of weights (0-1)."""
    if not weights:
        return 0.5
    hhi = sum(w * w for w in weights)
    # top-10 holdings of a broad fund ~0.01-0.03; a 3-stock portfolio ~0.33
    return min(1.0, hhi / 0.30)


def compute_risk_score(closes: pd.Series, weights: list = None) -> dict:
    """0-100 risk score. weights optional (holding/portfolio weights)."""
    vol = annualized_vol(closes)
    dd = max_drawdown(closes)
    conc = concentration_score(weights or [])

    # normalize: 40% vol (0-60% ann.), 40% drawdown (0-60%), 20% concentration
    vol_n = min(1.0, vol / 0.60)
    dd_n = min(1.0, dd / 0.60)
    score = 100 * (0.40 * vol_n + 0.40 * dd_n + 0.20 * conc)
    score = max(0, min(100, score))
    return {
        "score": round(score),
        "label": risk_label(score),
        "volatility": vol,
        "max_drawdown": dd,
        "concentration": conc,
    }
