"""Alpha Vantage helpers. The free tier allows ~25 requests/day, so every
call here is cached for hours-to-days and gated on the key."""
import requests
import streamlit as st

from lib.config import get_alpha_vantage_key

BASE = "https://www.alphavantage.co/query"


def key_missing() -> bool:
    return not get_alpha_vantage_key()


def _av(params: dict):
    """Returns (json, error). Detects AV throttle notes."""
    key = get_alpha_vantage_key()
    if not key:
        return None, "no key"
    p = dict(params)
    p["apikey"] = key
    try:
        r = requests.get(BASE, params=p, timeout=20)
        data = r.json()
        for k in ("Note", "Information", "Error Message"):
            if isinstance(data, dict) and data.get(k):
                return None, str(data[k])[:200]
        return data, ""
    except Exception as e:
        return None, f"{type(e).__name__}: {e}"


@st.cache_data(ttl=86400, show_spinner=False, max_entries=32)
def av_overview(symbol: str):
    return _av({"function": "OVERVIEW", "symbol": symbol})


@st.cache_data(ttl=86400, show_spinner=False, max_entries=32)
def av_earnings(symbol: str):
    return _av({"function": "EARNINGS", "symbol": symbol})


@st.cache_data(ttl=604800, show_spinner=False, max_entries=48)
def av_transcript(symbol: str, quarter: str):
    """quarter format: 2025Q1"""
    return _av({"function": "EARNINGS_CALL_TRANSCRIPT",
                "symbol": symbol, "quarter": quarter})


@st.cache_data(ttl=21600, show_spinner=False, max_entries=32)
def av_news_sentiment(symbol: str):
    return _av({"function": "NEWS_SENTIMENT", "tickers": symbol,
                "limit": 12, "sort": "LATEST"})


@st.cache_data(ttl=86400, show_spinner=False, max_entries=8)
def av_commodity(function: str):
    """WTI, BRENT, COPPER — monthly series."""
    return _av({"function": function, "interval": "monthly"})
