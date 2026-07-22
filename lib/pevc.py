"""PE/VC data sources: deal headlines, TradedVC archive, VC Corner archive.
All fetchers are defensive and cached at 15 minutes."""
import json
import re
import xml.etree.ElementTree as ET
from datetime import datetime, timezone

import requests
import streamlit as st

UA = {"User-Agent": "Mozilla/5.0 (PyramidTerminal personal dashboard)"}


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

BROWSER_HEADERS = {
    "User-Agent": ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                   "AppleWebKit/537.36 (KHTML, like Gecko) "
                   "Chrome/126.0.0.0 Safari/537.36"),
    "Accept": ("text/html,application/xhtml+xml,application/xml;q=0.9,"
               "image/avif,image/webp,*/*;q=0.8"),
    "Accept-Language": "en-US,en;q=0.9",
    "Referer": "https://vc.traded.co/",
}

_DATE_RE = re.compile(
    r"^((?:\d+\s+(?:minute|hour|day)s?\s+ago)|"
    r"(?:[A-Z][a-z]{2}\s+\d{1,2},\s+\d{4}))")


def _strip_tags(fragment: str) -> str:
    return re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", fragment)).strip()


def _tradedvc_from_anchors(html: str) -> list:
    """Beehiiv archive cards: each post has 1-3 anchors to the same /p/
    slug (title anchor, date+title+summary anchor, author anchor). Strip
    tags, group by slug, reconstruct title/date/summary."""
    groups = {}
    for m in re.finditer(
            r'<a[^>]+href="((?:https://vc\.traded\.co)?/p/[^"?#]+)"'
            r'[^>]*>(.*?)</a>', html, re.DOTALL):
        link = m.group(1)
        if link.startswith("/"):
            link = "https://vc.traded.co" + link
        text = _strip_tags(m.group(2))
        if len(text) >= 15:
            groups.setdefault(link, []).append(text)
    out = []
    for link, texts in groups.items():
        texts = sorted(set(texts), key=len)
        date, summary = "", ""
        if len(texts) > 1:
            title = texts[0]
            longer = texts[-1]
            dm = _DATE_RE.match(longer)
            if dm:
                date = dm.group(1)
                longer = longer[len(date):].strip()
            if longer.startswith(title):
                summary = longer[len(title):].strip()
            else:
                summary = longer
        else:
            longer = texts[0]
            dm = _DATE_RE.match(longer)
            if dm:
                date = dm.group(1)
                longer = longer[len(date):].strip()
            title = longer[:220]
        out.append({"title": title, "summary": summary[:300],
                    "link": link, "date": date})
    return out


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
                        "summary": (node.get("web_subtitle")
                                    or node.get("subtitle") or "")[:300],
                        "link": "https://vc.traded.co/p/" + node["slug"],
                        "date": (node.get("publish_date")
                                 or node.get("displayed_date") or "")[:10],
                    })
                for v in node.values():
                    walk(v)
            elif isinstance(node, list):
                for v in node:
                    walk(v)
        walk(data)
    except Exception:
        return []
    return out


@st.cache_data(ttl=900, show_spinner=False, max_entries=2)
def fetch_tradedvc(pages: int = 10):
    """Full TradedVC archive. Returns (posts, diagnostics)."""
    import time as _time
    t0 = _time.time()
    posts, seen, diag = [], set(), []
    sess = requests.Session()
    sess.headers.update(BROWSER_HEADERS)
    for page in range(1, pages + 1):
        if _time.time() - t0 > 40:
            diag.append("time-budget hit")
            break
        try:
            r = sess.get(f"https://vc.traded.co/archive?page={page}",
                         timeout=10)
            if r.status_code != 200:
                diag.append(f"p{page}:HTTP{r.status_code}")
                if r.status_code in (403, 429):
                    break
                continue
            batch = (_tradedvc_from_next_data(r.text)
                     or _tradedvc_from_anchors(r.text))
            if not batch:
                diag.append(f"p{page}:0 parsed")
            new = 0
            for p in batch:
                if p["link"] not in seen:
                    seen.add(p["link"])
                    posts.append(p)
                    new += 1
            if new == 0 and page > 1:
                break  # past the end of the archive
        except Exception as e:
            diag.append(f"p{page}:{type(e).__name__}")
    return posts, "; ".join(diag[:6])


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
