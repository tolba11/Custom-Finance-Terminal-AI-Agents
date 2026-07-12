"""Portfolio analytics: performance vs benchmark, risk stats, correlation.
The same analytics families institutional portfolio APIs provide, computed
from the Terminal's own price history."""
import math

import pandas as pd
import streamlit as st

from lib.market_data import get_history

BENCH = "SPY"


@st.cache_data(ttl=900, show_spinner=False, max_entries=8)
def build_portfolio_series(holdings_key: tuple, period: str = "1Y"):
    """holdings_key: tuple of (ticker, shares). Returns dict with
    portfolio value series, benchmark series, per-ticker daily returns."""
    closes = {}
    for tk, _ in holdings_key:
        h = get_history(tk, period)
        if h is not None and not h.empty and "Close" in h:
            s = h["Close"]
            s.index = pd.to_datetime(s.index).tz_localize(None).normalize()
            closes[tk] = s[~s.index.duplicated(keep="last")]
    if not closes:
        return None
    prices = pd.DataFrame(closes).ffill().dropna(how="all")
    shares = pd.Series({tk: sh for tk, sh in holdings_key})
    value = (prices * shares.reindex(prices.columns)).sum(axis=1)
    value = value[value > 0]

    b = get_history(BENCH, period)
    bench = None
    if b is not None and not b.empty:
        bs = b["Close"]
        bs.index = pd.to_datetime(bs.index).tz_localize(None).normalize()
        bench = bs[~bs.index.duplicated(keep="last")]
        bench = bench.reindex(value.index).ffill()

    return {"value": value, "bench": bench,
            "returns": prices.pct_change().dropna(how="all")}


def perf_stats(value: pd.Series, bench: pd.Series = None) -> dict:
    """Annualized performance/risk statistics for a value series."""
    out = {}
    if value is None or len(value) < 20:
        return out
    rets = value.pct_change().dropna()
    n = len(rets)
    years = n / 252
    total = value.iloc[-1] / value.iloc[0] - 1
    out["Cumulative return"] = f"{total:+.1%}"
    if years > 0.2:
        out["CAGR"] = f"{(1 + total) ** (1 / max(years, 1e-9)) - 1:+.1%}"
    vol = rets.std() * math.sqrt(252)
    out["Volatility (ann.)"] = f"{vol:.1%}"
    if vol > 0:
        out["Sharpe (rf=0)"] = f"{(rets.mean() * 252) / vol:.2f}"
    peak = value.cummax()
    out["Max drawdown"] = f"{(value / peak - 1).min():.1%}"
    out["Best day"] = f"{rets.max():+.1%}"
    out["Worst day"] = f"{rets.min():+.1%}"
    if bench is not None and len(bench.dropna()) > 20:
        brets = bench.pct_change().dropna()
        joined = pd.concat([rets, brets], axis=1, keys=["p", "b"]).dropna()
        if len(joined) > 20 and joined["b"].var() > 0:
            beta = joined["p"].cov(joined["b"]) / joined["b"].var()
            out["Beta vs SPY"] = f"{beta:.2f}"
            alpha = (joined["p"].mean()
                     - beta * joined["b"].mean()) * 252
            out["Alpha vs SPY (ann.)"] = f"{alpha:+.1%}"
            btotal = bench.dropna().iloc[-1] / bench.dropna().iloc[0] - 1
            out["Excess vs SPY"] = f"{total - btotal:+.1%}"
    return out
