"""Download logos for top US tickers into assets/logos/<TICKER>.<ext>.

Source order per ticker:
  1. simple-icons SVG via jsdelivr CDN (recolored white for dark mode)
  2. vectorlogo.zone SVG
  3. apple-touch-icon from the company's domain
  4. Google faviconV2 at size=256
  5. DuckDuckGo icons

Run:  python scripts/fetch_logos.py
"""
import os
import re
import sys

import requests

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from lib.logos import TICKER_DOMAINS  # noqa: E402

OUT_DIR = os.path.join(os.path.dirname(os.path.dirname(
    os.path.abspath(__file__))), "assets", "logos")
HEADERS = {"User-Agent": "Mozilla/5.0 (logo fetcher; personal dashboard)"}
TIMEOUT = 12

# simple-icons slugs differ from domains; map the common ones
SIMPLE_ICON_SLUGS = {
    "AAPL": "apple", "MSFT": None, "GOOGL": "google", "GOOG": "google",
    "AMZN": None, "NVDA": "nvidia", "META": "meta", "TSLA": "tesla",
    "ORCL": "oracle", "ADBE": "adobe", "NFLX": "netflix", "AMD": "amd",
    "CSCO": "cisco", "INTC": "intel", "IBM": "ibm", "QCOM": "qualcomm",
    "UBER": "uber", "PYPL": "paypal", "ABNB": "airbnb", "SHOP": "shopify",
    "SNOW": "snowflake", "COIN": "coinbase", "CRM": "salesforce",
    "NKE": "nike", "SBUX": "starbucks", "MCD": "mcdonalds",
    "V": "visa", "MA": "mastercard", "KO": "cocacola", "PEP": "pepsi",
    "F": "ford", "GM": "generalmotors", "TM": "toyota", "SONY": "sony",
    "BABA": "alibabadotcom", "TSM": "tsmc", "ASML": None,
    "INTU": "intuit", "NOW": None, "PLTR": "palantir",
}


def _save(ticker: str, content: bytes, ext: str) -> bool:
    if not content or len(content) < 200:
        return False
    path = os.path.join(OUT_DIR, f"{ticker}{ext}")
    with open(path, "wb") as f:
        f.write(content)
    return True


def _get(url: str):
    try:
        r = requests.get(url, headers=HEADERS, timeout=TIMEOUT)
        if r.status_code == 200 and r.content:
            return r
    except requests.RequestException:
        pass
    return None


def try_simple_icons(ticker: str) -> bool:
    slug = SIMPLE_ICON_SLUGS.get(ticker)
    if not slug:
        return False
    r = _get(f"https://cdn.jsdelivr.net/npm/simple-icons@latest/icons/{slug}.svg")
    if r is None or b"<svg" not in r.content[:200]:
        return False
    svg = r.content.decode("utf-8", errors="ignore")
    # recolor for dark mode
    if 'fill="' in svg:
        svg = re.sub(r'fill="[^"]*"', 'fill="#ffffff"', svg, count=1)
    else:
        svg = svg.replace("<svg ", '<svg fill="#ffffff" ', 1)
    return _save(ticker, svg.encode(), ".svg")


def try_vectorlogo(ticker: str, domain: str) -> bool:
    name = domain.split(".")[0]
    r = _get(f"https://www.vectorlogo.zone/logos/{name}/{name}-icon.svg")
    if r is not None and b"<svg" in r.content[:300]:
        return _save(ticker, r.content, ".svg")
    return False


def try_apple_touch(ticker: str, domain: str) -> bool:
    for path in ("apple-touch-icon.png", "apple-touch-icon-precomposed.png"):
        r = _get(f"https://{domain}/{path}")
        if r is not None and r.headers.get("content-type", "").startswith("image"):
            return _save(ticker, r.content, ".png")
    return False


def try_google_favicon(ticker: str, domain: str) -> bool:
    r = _get("https://t3.gstatic.com/faviconV2?client=SOCIAL&type=FAVICON"
             f"&fallback_opts=TYPE,SIZE,URL&url=https://{domain}&size=256")
    if r is not None and r.headers.get("content-type", "").startswith("image"):
        return _save(ticker, r.content, ".png")
    return False


def try_duckduckgo(ticker: str, domain: str) -> bool:
    r = _get(f"https://icons.duckduckgo.com/ip3/{domain}.ico")
    if r is not None:
        return _save(ticker, r.content, ".ico")
    return False


def main():
    os.makedirs(OUT_DIR, exist_ok=True)
    ok, fail = 0, []
    for ticker, domain in TICKER_DOMAINS.items():
        safe = ticker.replace("/", "-")
        if any(os.path.exists(os.path.join(OUT_DIR, f"{safe}{e}"))
               for e in (".svg", ".png", ".ico")):
            ok += 1
            continue
        got = (try_simple_icons(safe)
               or try_vectorlogo(safe, domain)
               or try_apple_touch(safe, domain)
               or try_google_favicon(safe, domain)
               or try_duckduckgo(safe, domain))
        if got:
            ok += 1
            print(f"  ✓ {ticker}")
        else:
            fail.append(ticker)
            print(f"  ✗ {ticker}")
    print(f"\nDone: {ok}/{len(TICKER_DOMAINS)} logos saved to {OUT_DIR}")
    if fail:
        print("Missing:", ", ".join(fail))


if __name__ == "__main__":
    main()
