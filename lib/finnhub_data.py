"""Finnhub API helpers: earnings & IPO calendars, analyst recommendation
trends, insider transactions. Free-tier endpoints only."""
from datetime import date, timedelta

import requests
import streamlit as st

from lib.config import get_finnhub_key

BASE = "https://finnhub.io/api/v1"


def key_missing() -> bool:
    return not get_finnhub_key()


def _get(path: str, params: dict = None):
    key = get_finnhub_key()
    if not key:
        return None
    p = dict(params or {})
    p["token"] = key
    try:
        r = requests.get(f"{BASE}{path}", params=p, timeout=15)
        if r.status_code == 200:
            return r.json()
    except requests.RequestException:
        pass
    return None


@st.cache_data(ttl=1800, show_spinner=False, max_entries=4)
def earnings_calendar(days_ahead: int = 14) -> list:
    start = date.today()
    end = start + timedelta(days=days_ahead)
    data = _get("/calendar/earnings",
                {"from": start.isoformat(), "to": end.isoformat()})
    items = (data or {}).get("earningsCalendar") or []
    items.sort(key=lambda x: (x.get("date") or "", x.get("symbol") or ""))
    return items


@st.cache_data(ttl=3600, show_spinner=False)
def ipo_calendar(days_ahead: int = 30) -> list:
    start = date.today()
    end = start + timedelta(days=days_ahead)
    data = _get("/calendar/ipo",
                {"from": start.isoformat(), "to": end.isoformat()})
    return (data or {}).get("ipoCalendar") or []


@st.cache_data(ttl=3600, show_spinner=False, max_entries=64)
def recommendation_trends(symbol: str) -> list:
    """Monthly analyst consensus counts (third-party data), newest first."""
    data = _get("/stock/recommendation", {"symbol": symbol.upper()})
    return data or []


@st.cache_data(ttl=3600, show_spinner=False, max_entries=64)
def insider_transactions(symbol: str, limit: int = 25) -> list:
    data = _get("/stock/insider-transactions", {"symbol": symbol.upper()})
    items = (data or {}).get("data") or []
    items.sort(key=lambda x: x.get("transactionDate") or "", reverse=True)
    return items[:limit]
