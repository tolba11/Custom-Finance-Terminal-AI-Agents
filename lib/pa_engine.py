"""PA-style portfolio analytics engine.

Structure recycled from FactSet's enterprise-sdk (Apache-2):
Portfolio API v3 (model accounts = holdings + benchmark) feeding the
PA Engine v3 component model — components grouped by category
(Performance / Attribution / Weights / Risk), groupings (sector),
columns (measures), and column statistics — reimplemented here as
pure functions over Yahoo Finance data.
"""
import math

import pandas as pd
import streamlit as st

# PA "grouping": GICS-style sector -> SPDR sector ETF benchmark proxy
SECTOR_ETF = {
    "Technology": "XLK", "Financial Services": "XLF", "Healthcare": "XLV",
    "Energy": "XLE", "Industrials": "XLI", "Consumer Cyclical": "XLY",
    "Consumer Defensive": "XLP", "Utilities": "XLU", "Real Estate": "XLRE",
    "Basic Materials": "XLB", "Communication Services": "XLC",
}

_YF_SECTOR_KEYS = {
    "technology": "Technology", "financial_services": "Financial Services",
    "healthcare": "Healthcare", "consumer_cyclical": "Consumer Cyclical",
    "consumer_defensive": "Consumer Defensive",
    "communication_services": "Communication Services",
    "industrials": "Industrials", "energy": "Energy",
    "utilities": "Utilities", "real_estate": "Real Estate",
    "realestate": "Real Estate", "basic_materials": "Basic Materials",
}

# Fallback if SPY fund data is unavailable (approximate weights)
_SPY_FALLBACK = {
    "Technology": 0.33, "Financial Services": 0.13, "Healthcare": 0.11,
    "Consumer Cyclical": 0.11, "Communication Services": 0.09,
    "Industrials": 0.08, "Consumer Defensive": 0.06, "Energy": 0.03,
    "Utilities": 0.025, "Real Estate": 0.02, "Basic Materials": 0.02,
}


@st.cache_data(ttl=6 * 3600, show_spinner=False, max_entries=2)
def spy_sector_weights() -> dict:
    """Benchmark sector weights from SPY fund data (normalized)."""
    try:
        from lib.market_data import get_etf_details
        raw = get_etf_details("SPY").get("sectors") or {}
        w = {}
        for k, v in dict(raw).items():
            name = _YF_SECTOR_KEYS.get(str(k).lower().replace(" ", "_"))
            if name and v:
                w[name] = w.get(name, 0) + float(v)
        total = sum(w.values())
        if total > 0.5:
            return {k: v / total for k, v in w.items()}
    except Exception:
        pass
    return dict(_SPY_FALLBACK)


# ---- Performance components ----

def monthly_returns(value: pd.Series) -> pd.Series:
    """Calendar-month returns from a daily value series."""
    if value is None or len(value) < 25:
        return pd.Series(dtype=float)
    m = value.resample("ME").last()
    m.iloc[0] = value.iloc[0]  # anchor first month to inception
    return m.pct_change().dropna()


def extended_stats(value: pd.Series, bench: pd.Series = None) -> dict:
    """PA column-statistics set: absolute + benchmark-relative measures."""
    out = {}
    if value is None or len(value) < 20:
        return out
    rets = value.pct_change().dropna()
    total = value.iloc[-1] / value.iloc[0] - 1
    years = len(rets) / 252
    out["Cumulative return"] = f"{total:+.1%}"
    out["CAGR"] = f"{(1 + total) ** (1 / max(years, 1e-9)) - 1:+.1%}"
    vol = rets.std() * math.sqrt(252)
    out["Volatility (ann.)"] = f"{vol:.1%}"
    if vol > 0:
        out["Sharpe (rf=0)"] = f"{(rets.mean() * 252) / vol:.2f}"
    dstd = rets[rets < 0].std()
    if dstd and dstd > 0:
        out["Sortino"] = f"{(rets.mean() * 252) / (dstd * math.sqrt(252)):.2f}"
    peak = value.cummax()
    out["Max drawdown"] = f"{(value / peak - 1).min():.1%}"
    var95 = rets.quantile(0.05)
    out["VaR 95% (1-day)"] = f"{var95:.2%}"
    tail = rets[rets <= var95]
    if len(tail):
        out["CVaR 95% (1-day)"] = f"{tail.mean():.2%}"
    out["Best day"] = f"{rets.max():+.1%}"
    out["Worst day"] = f"{rets.min():+.1%}"

    if bench is not None and len(bench.dropna()) > 20:
        b = bench.dropna()
        brets = b.pct_change().dropna()
        j = pd.concat([rets, brets], axis=1, keys=["p", "b"]).dropna()
        if len(j) > 20 and j["b"].var() > 0:
            beta = j["p"].cov(j["b"]) / j["b"].var()
            out["Beta vs SPY"] = f"{beta:.2f}"
            alpha = (j["p"].mean() - beta * j["b"].mean()) * 252
            out["Alpha vs SPY (ann.)"] = f"{alpha:+.1%}"
            btotal = b.iloc[-1] / b.iloc[0] - 1
            out["Excess vs SPY"] = f"{total - btotal:+.1%}"
            active = j["p"] - j["b"]
            te = active.std() * math.sqrt(252)
            out["Tracking error"] = f"{te:.1%}"
            if te > 0:
                out["Information ratio"] = f"{active.mean() * 252 / te:.2f}"
            pm, bm = monthly_returns(value), monthly_returns(b)
            mj = pd.concat([pm, bm], axis=1, keys=["p", "b"]).dropna()
            up, dn = mj[mj["b"] > 0], mj[mj["b"] < 0]
            if len(up) and up["b"].mean():
                out["Up capture"] = f"{up['p'].mean() / up['b'].mean():.0%}"
            if len(dn) and dn["b"].mean():
                out["Down capture"] = f"{dn['p'].mean() / dn['b'].mean():.0%}"
    return out


def drawdown_series(value: pd.Series) -> pd.Series:
    if value is None or value.empty:
        return pd.Series(dtype=float)
    return (value / value.cummax() - 1) * 100


# ---- Attribution components ----

def contribution_to_return(returns: pd.DataFrame, weights: dict) -> pd.Series:
    """Per-position contribution: weight x horizon total return.
    Buy-and-hold approximation using current weights."""
    out = {}
    for tk in returns.columns:
        r = returns[tk].dropna()
        if len(r) and tk in weights:
            out[tk] = weights[tk] * ((1 + r).prod() - 1)
    return pd.Series(out).sort_values()


def brinson_attribution(port_sectors: dict, sector_rets: dict,
                        bench_weights: dict, bench_total: float,
                        port_sector_rets: dict) -> pd.DataFrame:
    """Brinson-Fachler single-period attribution by sector.
    allocation = (wp - wb)(Rb_s - Rb); selection = wp (Rp_s - Rb_s)."""
    rows = []
    for sec in sorted(set(port_sectors) | set(bench_weights)):
        wp = port_sectors.get(sec, 0.0)
        wb = bench_weights.get(sec, 0.0)
        rb = sector_rets.get(sec)
        rp = port_sector_rets.get(sec)
        alloc = (wp - wb) * (rb - bench_total) if rb is not None else None
        sel = wp * (rp - rb) if (rp is not None and rb is not None) else None
        rows.append({"Sector": sec, "Port wt": wp, "Bench wt": wb,
                     "Port ret": rp, "Bench ret": rb,
                     "Allocation": alloc, "Selection": sel,
                     "Total": (alloc or 0) + (sel or 0)
                     if (alloc is not None or sel is not None) else None})
    df = pd.DataFrame(rows)
    return df[(df["Port wt"] > 0.001) | (df["Bench wt"] > 0.001)]


# ---- Risk components ----

def risk_decomposition(returns: pd.DataFrame, weights: dict) -> pd.DataFrame:
    """Marginal / percent contribution to portfolio risk (MCTR, CTR)."""
    cols = [c for c in returns.columns if c in weights]
    r = returns[cols].dropna()
    if r.shape[0] < 20 or r.shape[1] < 1:
        return pd.DataFrame()
    w = pd.Series({c: weights[c] for c in cols})
    w = w / w.sum()
    cov = r.cov() * 252
    port_var = float(w @ cov @ w)
    if port_var <= 0:
        return pd.DataFrame()
    sigma = math.sqrt(port_var)
    mctr = (cov @ w) / sigma
    ctr = w * mctr
    return pd.DataFrame({
        "Weight": w, "Stand-alone vol": (r.std() * math.sqrt(252)),
        "MCTR": mctr, "CTR": ctr, "% of risk": ctr / sigma,
    }).sort_values("CTR", ascending=False)


# ---- Weights / style components ----

CAP_BUCKETS = [(200e9, "Mega (>$200B)"), (10e9, "Large ($10-200B)"),
               (2e9, "Mid ($2-10B)"), (0, "Small (<$2B)")]


def style_snapshot(infos: dict, weights: dict) -> list:
    """Weighted style measures vs SPY-holder profile fields."""
    def wavg(field):
        num = den = 0.0
        for tk, w in weights.items():
            v = (infos.get(tk) or {}).get(field)
            if v is not None and isinstance(v, (int, float)):
                num += w * float(v)
                den += w
        return num / den if den > 0.3 else None

    rows = []
    for label, field, fmt in [
            ("Weighted P/E (trailing)", "trailingPE", "{:.1f}"),
            ("Weighted P/B", "priceToBook", "{:.1f}"),
            ("Weighted dividend yield", "dividendYield", "{:.2%}"),
            ("Weighted beta", "beta", "{:.2f}"),
            ("Weighted ROE", "returnOnEquity", "{:.1%}"),
            ("Weighted net margin", "profitMargins", "{:.1%}"),
            ("Weighted revenue growth", "revenueGrowth", "{:+.1%}")]:
        v = wavg(field)
        if field == "dividendYield" and v is not None and v > 0.5:
            v = v / 100  # yfinance sometimes returns percent units
        rows.append((label, fmt.format(v) if v is not None else "—"))
    return rows


def cap_buckets(infos: dict, weights: dict) -> dict:
    out = {}
    for tk, w in weights.items():
        mc = (infos.get(tk) or {}).get("marketCap")
        label = "Unclassified"
        if mc:
            for floor, name in CAP_BUCKETS:
                if mc >= floor:
                    label = name
                    break
        out[label] = out.get(label, 0) + w
    return out


def geo_buckets(infos: dict, weights: dict) -> dict:
    out = {}
    for tk, w in weights.items():
        c = (infos.get(tk) or {}).get("country") or "Other/Fund"
        out[c] = out.get(c, 0) + w
    return out
