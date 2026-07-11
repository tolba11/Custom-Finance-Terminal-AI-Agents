"""PE/VC data sources: deal headlines, TradedVC archive, VC Corner archive.
All fetchers are defensive and cached at 15 minutes."""
import json
import re
import xml.etree.ElementTree as ET
from datetime import datetime, timezone

import requests
import streamlit as st

UA = {"User-Agent": "Mozilla/5.0 (TolbaTerminal personal dashboard)"}


# ---------- Deals: PE deal headlines via Google News RSS ----------

@st.cache_data(ttl=900, show_spinner=False, max_entries=4)
def fetch_pe_deal_headlines(limit: int = 25) -> list:
    url = ("https://news.google.com/rss/search?q="
           "%22private%20equity%22%20(deal%20OR%20buyout%20OR%20acquires"
           "%20OR%20fund)&hl=en-US&gl=US&ceid=US:en")
    out = []
    try:
        r = requests.get(url, headers=UA, timeout=12)
        root = ET.fromstring(r.content)
        for it in root.iter("item"):
            title = it.findtext("title", "")
            link = it.findtext("link", "")
            pub = it.findtext("pubDate", "")
            src = it.find("{https://news.google.com/rss}source")
            source = (src.text if src is not None else
                      (it.findtext("source") or ""))
            ts = None
            try:
                ts = datetime.strptime(pub, "%a, %d %b %Y %H:%M:%S %Z"
                                       ).replace(tzinfo=timezone.utc)
            except (ValueError, TypeError):
                pass
            if title:
                out.append({"title": title, "link": link,
                            "source": source, "published": ts})
            if len(out) >= limit:
                break
    except Exception:
        pass
    return out


# ---------- VC Traded: beehiiv archive ----------

def _tradedvc_from_next_data(html: str) -> list:
    m = re.search(r'<script id="__NEXT_DATA__"[^>]*>(.*?)</script>',
                  html, re.DOTALL)
    if not m:
        return []
    out = []
    try:
        data = json.loads(m.group(1))

        def walk(node):
            if isinstance(node, dict):
                if node.get("slug") and (node.get("web_title")
                                         or node.get("title")):
                    out.append({
                        "title": node.get("web_title") or node.get("title"),
                        "summary": node.get("web_subtitle")
                        or node.get("subtitle") or "",
                        "link": "https://vc.traded.co/p/" + node["slug"],
                        "date": (node.get("publish_date")
                                 or node.get("displayed_date") or ""),
                    })
                for v in node.values():
                    walk(v)
            elif isinstance(node, list):
                for v in node:
                    walk(v)
        walk(data)
    except Exception:
        return []
    seen, uniq = set(), []
    for p in out:
        if p["link"] not in seen:
            seen.add(p["link"])
            uniq.append(p)
    return uniq


def _tradedvc_from_anchors(html: str) -> list:
    out, seen = [], set()
    for m in re.finditer(
            r'href="(https://vc\.traded\.co/p/[^"]+|/p/[^"]+)"[^>]*>'
            r'\s*([^<][^<]{15,400}?)\s*<', html):
        link, text = m.group(1), re.sub(r"\s+", " ", m.group(2)).strip()
        if link.startswith("/p/"):
            link = "https://vc.traded.co" + link
        if link in seen or len(text) < 20:
            continue
        seen.add(link)
        out.append({"title": text, "summary": "", "link": link, "date": ""})
    return out


@st.cache_data(ttl=900, show_spinner=False, max_entries=2)
def fetch_tradedvc(pages: int = 4) -> list:
    posts, seen = [], set()
    for page in range(1, pages + 1):
        try:
            r = requests.get(f"https://vc.traded.co/archive?page={page}",
                             headers=UA, timeout=12)
            if r.status_code != 200:
                continue
            batch = (_tradedvc_from_next_data(r.text)
                     or _tradedvc_from_anchors(r.text))
            for p in batch:
                if p["link"] not in seen:
                    seen.add(p["link"])
                    posts.append(p)
        except Exception:
            continue
    return posts


# ---------- VC Corner: Substack archive API ----------

@st.cache_data(ttl=900, show_spinner=False, max_entries=2)
def fetch_vccorner(max_posts: int = 300) -> list:
    posts = []
    offset = 0
    while offset < max_posts:
        try:
            r = requests.get(
                "https://www.thevccorner.com/api/v1/archive",
                params={"sort": "new", "offset": offset, "limit": 50},
                headers=UA, timeout=12)
            batch = r.json()
            if not isinstance(batch, list) or not batch:
                break
            for p in batch:
                posts.append({
                    "title": p.get("title", ""),
                    "subtitle": p.get("subtitle", ""),
                    "link": p.get("canonical_url", ""),
                    "date": (p.get("post_date") or "")[:10],
                    "paid": p.get("audience") == "only_paid",
                })
            if len(batch) < 50:
                break
            offset += 50
        except Exception:
            break
    return posts
