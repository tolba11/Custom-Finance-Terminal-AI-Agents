"""SEC EDGAR helpers — free, keyless, fair-use headers required."""
import requests
import streamlit as st

HEADERS = {"User-Agent": "PyramidTerminal personal research "
                         "yassintolba2003@gmail.com"}

FORM_TYPES = ["All", "10-K", "10-Q", "8-K", "DEF 14A", "S-1", "20-F", "6-K"]


@st.cache_data(ttl=86400, show_spinner=False)
def _cik_map() -> dict:
    try:
        r = requests.get("https://www.sec.gov/files/company_tickers.json",
                         headers=HEADERS, timeout=20)
        return {v["ticker"].upper(): (str(v["cik_str"]).zfill(10),
                                      v.get("title", ""))
                for v in r.json().values()}
    except Exception:
        return {}


@st.cache_data(ttl=3600, show_spinner=False, max_entries=32)
def get_filings(ticker: str):
    """Returns (company_title, [filing dicts], error)."""
    base = ticker.upper().split(".")[0].replace("-", "")
    m = _cik_map()
    entry = m.get(ticker.upper()) or m.get(base)
    if not entry:
        return "", [], ("Not found in SEC registry — EDGAR covers "
                        "US-listed filers only.")
    cik, title = entry
    try:
        r = requests.get(f"https://data.sec.gov/submissions/CIK{cik}.json",
                         headers=HEADERS, timeout=20)
        recent = r.json().get("filings", {}).get("recent", {})
        out = []
        forms = recent.get("form", [])
        for i in range(len(forms)):
            acc = recent["accessionNumber"][i].replace("-", "")
            doc = recent["primaryDocument"][i]
            out.append({
                "form": forms[i],
                "date": recent["filingDate"][i],
                "desc": (recent.get("primaryDocDescription", [""] *
                         len(forms))[i] or forms[i]),
                "url": (f"https://www.sec.gov/Archives/edgar/data/"
                        f"{int(cik)}/{acc}/{doc}"),
                "index": (f"https://www.sec.gov/cgi-bin/browse-edgar?"
                          f"action=getcompany&CIK={cik}&type="
                          f"{forms[i]}&dateb=&owner=include&count=40"),
            })
        return title, out, ""
    except Exception as e:
        return title, [], f"{type(e).__name__}: {e}"


def fulltext_search_url(query: str) -> str:
    """Link to SEC EDGAR full-text search for any phrase."""
    from urllib.parse import quote
    return "https://efts.sec.gov/LATEST/search-index?q=" + quote(query)


def edgar_search_ui(query: str) -> str:
    """Human-facing EDGAR full-text search page."""
    from urllib.parse import quote
    return "https://www.sec.gov/cgi-bin/browse-edgar" \
        + "?action=getcompany&company=" + quote(query) \
        + "&type=10-K&dateb=&owner=include&count=40"
