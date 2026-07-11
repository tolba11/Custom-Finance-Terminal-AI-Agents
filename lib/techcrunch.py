"""TechCrunch section feeds (WordPress RSS, paginated). Cached 15 min."""
import re
import xml.etree.ElementTree as ET
from datetime import datetime, timezone

import requests
import streamlit as st

UA = {"User-Agent": ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                     "AppleWebKit/537.36 (KHTML, like Gecko) "
                     "Chrome/126.0.0.0 Safari/537.36")}

# sub-tab -> (primary feed path, fallback feed path)
SECTIONS = {
    "Latest": ("feed", None),
    "Startups": ("category/startups/feed", None),
    "Venture": ("category/venture/feed", None),
    "Apple": ("tag/apple/feed", "category/apple/feed"),
    "Security": ("category/security/feed", None),
    "AI": ("category/artificial-intelligence/feed", "category/ai/feed"),
    "Apps": ("category/apps/feed", None),
}

_TAG = re.compile(r"<[^>]+>")


def _parse_feed(content: bytes) -> list:
    out = []
    root = ET.fromstring(content)
    ns = {"dc": "http://purl.org/dc/elements/1.1/"}
    for it in root.iter("item"):
        title = (it.findtext("title") or "").strip()
        link = (it.findtext("link") or "").strip()
        desc = _TAG.sub(" ", it.findtext("description") or "")
        desc = re.sub(r"\s+", " ", desc).strip()
        author = (it.findtext("dc:creator", namespaces=ns) or "").strip()
        ts = None
        try:
            ts = datetime.strptime(it.findtext("pubDate", ""),
                                   "%a, %d %b %Y %H:%M:%S %z")
        except (ValueError, TypeError):
            pass
        if title and link:
            out.append({"title": title, "link": link, "summary": desc,
                        "author": author, "published": ts})
    return out


@st.cache_data(ttl=900, show_spinner=False, max_entries=16)
def fetch_techcrunch(section: str, pages: int = 3):
    """Articles for one TechCrunch section. Returns (articles, error)."""
    paths = [p for p in SECTIONS.get(section, (None, None)) if p]
    if not paths:
        return [], f"unknown section {section}"
    articles, seen, err = [], set(), ""
    for path in paths:
        for page in range(1, pages + 1):
            url = f"https://techcrunch.com/{path}/"
            if page > 1:
                url += f"?paged={page}"
            try:
                r = requests.get(url, headers=UA, timeout=12)
                if r.status_code != 200:
                    err = f"HTTP {r.status_code} on {path} p{page}"
                    break
                batch = _parse_feed(r.content)
                if not batch:
                    break
                for a in batch:
                    if a["link"] not in seen:
                        seen.add(a["link"])
                        articles.append(a)
            except Exception as e:
                err = f"{type(e).__name__} on {path} p{page}"
                break
        if articles:
            break  # primary path worked; skip fallback
    articles.sort(key=lambda a: a["published"] or
                  datetime.min.replace(tzinfo=timezone.utc), reverse=True)
    return articles, ("" if articles else err)
