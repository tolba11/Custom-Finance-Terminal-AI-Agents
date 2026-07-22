"""Shared ticker/company search-with-suggestions component."""
import requests
import streamlit as st

from lib.config import get_finnhub_key

_TYPES = {"EQUITY": "Stock", "ETF": "ETF", "INDEX": "Index",
          "MUTUALFUND": "Fund", "CRYPTOCURRENCY": "Crypto"}

_EU_SUFFIX = {"L", "DE", "F", "PA", "AS", "MI", "SW", "MC", "BR", "LS",
              "VI", "ST", "OL", "CO", "HE", "IR", "WA", "PR", "AT"}
_APAC_SUFFIX = {"T", "HK", "SS", "SZ", "AX", "KS", "KQ", "TW", "TWO",
                "NS", "BO", "SI", "KL", "BK", "JK", "NZ"}


def symbol_region(symbol: str) -> str:
    """Classify a Yahoo symbol by its exchange suffix."""
    if "." in symbol:
        suffix = symbol.rsplit(".", 1)[-1].upper()
        if suffix in _EU_SUFFIX:
            return "Europe"
        if suffix in _APAC_SUFFIX:
            return "APAC"
        return "Other"
    return "U.S."


@st.cache_data(ttl=900, show_spinner=False, max_entries=256)
def search_symbols(q: str) -> list:
    """Match tickers AND company names. Yahoo search first, Finnhub backup."""
    out = []
    try:
        r = requests.get(
            "https://query2.finance.yahoo.com/v1/finance/search",
            params={"q": q, "quotesCount": 12, "newsCount": 0},
            headers={"User-Agent": "Mozilla/5.0"}, timeout=8)
        for it in r.json().get("quotes", []):
            qt = it.get("quoteType")
            if qt in _TYPES and it.get("symbol"):
                out.append({
                    "symbol": it["symbol"],
                    "name": it.get("shortname") or it.get("longname") or "",
                    "exch": it.get("exchDisp") or it.get("exchange") or "",
                    "type": _TYPES[qt],
                })
    except Exception:
        pass
    if not out and get_finnhub_key():
        try:
            r = requests.get("https://finnhub.io/api/v1/search",
                             params={"q": q, "token": get_finnhub_key()},
                             timeout=8)
            for it in r.json().get("result", [])[:8]:
                if it.get("symbol") and "." not in it["symbol"]:
                    out.append({"symbol": it["symbol"],
                                "name": (it.get("description") or "").title(),
                                "exch": "", "type": it.get("type", "")})
        except Exception:
            pass
    return out


def symbol_search(label: str, key: str, default: str,
                  region_filter: bool = False) -> str:
    """Search box + suggestion dropdown. Returns the selected symbol.
    The selection persists in session state across reruns/refreshes.
    With region_filter=True, matches can be narrowed to U.S. / Europe /
    APAC listings."""
    sel_key = f"{key}_symbol"
    if sel_key not in st.session_state:
        st.session_state[sel_key] = default

    q = st.text_input(
        label, key=f"{key}_q",
        placeholder="Ticker or company name — press Enter to search")

    region = "All"
    if region_filter:
        _r = st.segmented_control(
            "Region", ["All", "US", "EU", "APAC"],
            default="All", key=f"{key}_region") or "All"
        region = {"US": "U.S.", "EU": "Europe"}.get(_r, _r)

    if q and q.strip():
        matches = search_symbols(q.strip())
        if region != "All":
            matches = [m for m in matches
                       if symbol_region(m["symbol"]) == region]
            if not matches:
                st.caption(f"No {region} listings matched — clear the "
                           "region filter to see all matches.")
        if matches:
            syms = [m["symbol"] for m in matches]
            fmt = {m["symbol"]:
                   f'{m["symbol"]} — {m["name"]}'
                   + (f' ({m["exch"]}' if m["exch"] else "(")
                   + (f' · {m["type"]})' if m["type"] else ")")
                   for m in matches}
            choice = st.selectbox(
                "Matches", syms,
                format_func=lambda s: fmt.get(s, s),
                key=f"{key}_sel")
            if choice:
                st.session_state[sel_key] = choice
        else:
            st.session_state[sel_key] = q.strip().upper()
            st.caption("No matches found — treating your text as a ticker.")

    current = st.session_state[sel_key]
    st.markdown(
        f'<div style="font-family:Consolas,monospace;font-size:0.72rem;'
        f'letter-spacing:0.06em;color:#8a93a6;padding:2px 0 6px 0;">'
        f'SELECTED: <span style="color:#f97316;font-weight:600;">'
        f'{current}</span></div>', unsafe_allow_html=True)
    return current
