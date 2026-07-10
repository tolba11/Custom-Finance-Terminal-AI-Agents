"""News via yfinance with Yahoo RSS fallback."""
import time
import xml.etree.ElementTree as ET
from datetime import datetime, timezone

import requests
import streamlit as st
import yfinance as yf


def _normalize_yf_item(item: dict) -> dict:
    """yfinance news items changed shape across versions; normalize both."""
    content = item.get("content", item)
    title = content.get("title") or item.get("title") or ""
    summary = (content.get("summary") or content.get("description")
               or item.get("summary") or "")
    publisher = ""
    prov = content.get("provider") or {}
    if isinstance(prov, dict):
        publisher = prov.get("displayName", "")
    publisher = publisher or item.get("publisher", "")
    link = ""
    urlobj = content.get("canonicalUrl") or content.get("clickThroughUrl") or {}
    if isinstance(urlobj, dict):
        link = urlobj.get("url", "")
    link = link or item.get("link", "")
    ts = None
    pub = content.get("pubDate") or item.get("providerPublishTime")
    if isinstance(pub, (int, float)):
        ts = datetime.fromtimestamp(pub, tz=timezone.utc)
    elif isinstance(pub, str):
        try:
            ts = datetime.fromisoformat(pub.replace("Z", "+00:00"))
        except ValueError:
            ts = None
    return {"title": title, "summary": summary, "publisher": publisher,
            "link": link, "published": ts}


def _rss_fallback(ticker: str = None, limit: int = 15) -> list:
    sym = ticker or "^GSPC"
    url = ("https://feeds.finance.yahoo.com/rss/2.0/headline"
           f"?s={sym}&region=US&lang=en-US")
    try:
        r = requests.get(url, timeout=10,
                         headers={"User-Agent": "Mozilla/5.0"})
        root = ET.fromstring(r.content)
        items = []
        for it in root.iter("item"):
            title = it.findtext("title", "")
            link = it.findtext("link", "")
            desc = it.findtext("description", "")
            pub = it.findtext("pubDate", "")
            ts = None
            try:
                ts = datetime.strptime(pub, "%a, %d %b %Y %H:%M:%S %z")
            except (ValueError, TypeError):
                pass
            items.append({"title": title, "summary": desc,
                          "publisher": "Yahoo Finance", "link": link,
                          "published": ts})
            if len(items) >= limit:
                break
        return items
    except Exception:
        return []


@st.cache_data(ttl=300, show_spinner=False)
def ticker_news(ticker: str, limit: int = 10) -> list:
    """News for one ticker."""
    items = []
    try:
        raw = yf.Ticker(ticker).news or []
        items = [_normalize_yf_item(i) for i in raw]
        items = [i for i in items if i["title"]]
    except Exception:
        items = []
    if not items:
        items = _rss_fallback(ticker, limit)
    return items[:limit]


@st.cache_data(ttl=300, show_spinner=False)
def market_news(limit: int = 15) -> list:
    """Aggregated market headlines from broad tickers, deduped, newest first."""
    seen, items = set(), []
    for sym in ("^GSPC", "^NDX", "^DJI"):
        for it in ticker_news(sym, limit=10):
            key = it["title"].strip().lower()
            if key and key not in seen:
                seen.add(key)
                items.append(it)
    items.sort(key=lambda i: i["published"] or datetime.min.replace(
        tzinfo=timezone.utc), reverse=True)
    return items[:limit]


def time_ago(ts) -> str:
    if not ts:
        return ""
    delta = time.time() - ts.timestamp()
    if delta < 3600:
        return f"{int(delta // 60)}m ago"
    if delta < 86400:
        return f"{int(delta // 3600)}h ago"
    return f"{int(delta // 86400)}d ago"
