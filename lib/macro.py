"""FRED macro indicator helpers."""
import pandas as pd
import streamlit as st

from lib.config import get_fred_key

INDICATORS = {
    "GDP": ("GDP", "Nominal GDP ($B)", "level"),
    "Unemployment": ("UNRATE", "Unemployment rate (%)", "level"),
    "CPI YoY": ("CPIAUCSL", "CPI, all items", "yoy"),
    "Core CPI YoY": ("CPILFESL", "CPI ex food & energy", "yoy"),
    "Fed Funds": ("FEDFUNDS", "Effective fed funds rate (%)", "level"),
    "10Y-2Y Spread": ("T10Y2Y", "10Y minus 2Y Treasury (%)", "level"),
    "Retail Sales": ("RSAFS", "Retail sales ($M)", "yoy"),
    "Industrial Production": ("INDPRO", "Industrial production index", "yoy"),
}


def _fred():
    key = get_fred_key()
    if not key:
        return None
    try:
        from fredapi import Fred
        return Fred(api_key=key)
    except Exception:
        return None


@st.cache_data(ttl=3600, show_spinner=False, max_entries=64)
def get_series(series_id: str, years: int = 10) -> pd.Series:
    fred = _fred()
    if fred is None:
        return pd.Series(dtype=float)
    try:
        start = pd.Timestamp.now() - pd.DateOffset(years=years)
        s = fred.get_series(series_id, observation_start=start)
        return s.dropna()
    except Exception:
        return pd.Series(dtype=float)


def yoy(series: pd.Series) -> pd.Series:
    """Year-over-year % change for a monthly series."""
    if series.empty:
        return series
    return (series.pct_change(12) * 100).dropna()


@st.cache_data(ttl=3600, show_spinner=False)
def get_indicators() -> dict:
    """{label: {'series': pd.Series, 'latest': float, 'desc': str}}"""
    out = {}
    for label, (sid, desc, mode) in INDICATORS.items():
        s = get_series(sid)
        if mode == "yoy":
            s = yoy(s)
        if not s.empty:
            out[label] = {"series": s, "latest": float(s.iloc[-1]),
                          "desc": desc}
    return out
