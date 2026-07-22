"""Home — OpenBB-Workspace-style widget dashboard."""
import streamlit as st

from lib.config import apply_base_style, render_footer, render_sidebar
from lib.logos import logo_img_html
from lib.market_data import (INDEX_TICKERS, SECTOR_ETFS, get_quotes_bulk)
from lib.markets_strip import render_markets_strip
from lib.news import market_news, time_ago
from lib.registry import PAGES, url_path
from lib.watchlist import load_watchlist, save_watchlist

apply_base_style(st)
render_sidebar(st)

st.title("Pyramid Terminal")
st.markdown('<div class="tt-subtitle">WORKSPACE · LIVE DATA · '
            'AUTO-REFRESH 15 MIN</div>', unsafe_allow_html=True)

GREEN, RED = "#16c784", "#ea3943"


def _card_open(title):
    st.markdown(
        f'<div style="font-family:Consolas,monospace;font-size:0.68rem;'
        f'letter-spacing:0.1em;color:#8a93a6;border-bottom:2px solid '
        f'#252c3b;padding-bottom:4px;margin-bottom:6px;">{title}</div>',
        unsafe_allow_html=True)


def _row(logo_html, label, sub, val, pct):
    color = GREEN if (pct or 0) >= 0 else RED
    st.markdown(
        f'<div style="display:grid;grid-template-columns:24px minmax(0,1fr)'
        f' 6em 4.5em;gap:8px;align-items:center;padding:4px 0;'
        f'border-bottom:1px solid #1a2029;">{logo_html}'
        f'<span style="min-width:0;"><b style="font-size:0.82rem;">{label}'
        f'</b> <span style="color:#5c6575;font-size:11px;white-space:'
        f'nowrap;">{sub}</span></span>'
        f'<span style="text-align:right;font-family:Consolas,monospace;'
        f'font-size:0.82rem;">{val}</span>'
        f'<span style="text-align:right;font-family:Consolas,monospace;'
        f'font-size:0.78rem;color:{color};">{pct:+.2f}%</span></div>'
        if pct is not None else
        f'<div style="padding:4px 0;color:#5c6575;">{label} —</div>',
        unsafe_allow_html=True)


def _safe(fn):
    try:
        fn()
    except Exception as e:
        st.error("Widget hit a temporary data problem.")
        st.caption(f"Detail: {type(e).__name__}: {e}")


# ============ ROW 1: watchlist | indices | sectors ============
c_wl, c_ix, c_sec = st.columns([1.35, 1, 1])

with c_wl:
    def _watchlist():
        _card_open("WATCHLIST")
        wl = load_watchlist()
        quotes = get_quotes_bulk(tuple(wl))
        for tk in wl:
            q = quotes.get(tk, {})
            price, pct = q.get("price"), q.get("change_pct")
            _row(logo_img_html(tk, 20), tk, "",
                 f"{price:,.2f}" if price else "—", pct)
        with st.expander("Edit watchlist"):
            new = st.text_input("Add symbol", key="wl_add",
                                placeholder="e.g. NFLX or 7203.T")
            c1, c2 = st.columns(2)
            with c1:
                if st.button("Add", key="wl_add_btn") and new.strip():
                    save_watchlist(wl + [new])
                    st.rerun()
            rm = st.multiselect("Remove", wl, key="wl_rm")
            with c2:
                if st.button("Remove", key="wl_rm_btn") and rm:
                    save_watchlist([t for t in wl if t not in rm])
                    st.rerun()
    _safe(_watchlist)

with c_ix:
    def _indices():
        _card_open("INDICES & ASSETS")
        quotes = get_quotes_bulk(tuple(INDEX_TICKERS.keys()))
        for tk, name in INDEX_TICKERS.items():
            q = quotes.get(tk, {})
            price, pct = q.get("price"), q.get("change_pct")
            _row('<span></span>', name, "",
                 f"{price:,.2f}" if price else "—", pct)
    _safe(_indices)

with c_sec:
    def _sectors():
        _card_open("SECTORS TODAY")
        quotes = get_quotes_bulk(tuple(SECTOR_ETFS.keys()))
        pairs = []
        for tk, name in SECTOR_ETFS.items():
            q = quotes.get(tk, {})
            if q.get("change_pct") is not None:
                pairs.append((name, tk, q["change_pct"]))
        for name, tk, pct in sorted(pairs, key=lambda x: -x[2]):
            bar_w = min(abs(pct) * 30, 100)
            color = GREEN if pct >= 0 else RED
            st.markdown(
                f'<div style="display:grid;grid-template-columns:minmax(0,'
                f'1fr) 90px 4.5em;gap:8px;align-items:center;padding:3px 0;'
                f'border-bottom:1px solid #1a2029;">'
                f'<span style="font-size:0.78rem;white-space:nowrap;'
                f'overflow:hidden;text-overflow:ellipsis;">{name}</span>'
                f'<span style="background:#1a2029;height:8px;">'
                f'<span style="display:block;width:{bar_w}%;height:8px;'
                f'background:{color};"></span></span>'
                f'<span style="text-align:right;font-family:Consolas,'
                f'monospace;font-size:0.78rem;color:{color};">{pct:+.2f}%'
                f'</span></div>', unsafe_allow_html=True)
    _safe(_sectors)

st.markdown("<div style='height:14px'></div>", unsafe_allow_html=True)

# ============ ROW 2: markets strip ============
def _strip():
    _card_open("COMMODITIES · FX · RATES")
    render_markets_strip()
_safe(_strip)

st.markdown("<div style='height:14px'></div>", unsafe_allow_html=True)

# ============ ROW 3: news | functions ============
c_news, c_fn = st.columns([1.35, 2])

with c_news:
    def _news():
        _card_open("LATEST HEADLINES")
        for a in (market_news(limit=10) or [])[:10]:
            title = a.get("title") or ""
            link = a.get("link") or a.get("url") or "#"
            pub = a.get("publisher") or a.get("source") or ""
            ago = time_ago(a.get("published")) if a.get("published") else ""
            st.markdown(
                f'<div style="padding:5px 0;border-bottom:1px solid '
                f'#1a2029;"><a href="{link}" target="_blank" '
                f'style="color:#dee3ea;text-decoration:none;font-size:'
                f'0.85rem;">{title}</a><br>'
                f'<span style="color:#5c6575;font-family:Consolas,'
                f'monospace;font-size:0.65rem;letter-spacing:0.05em;">'
                f'{pub.upper()} {("· " + ago) if ago else ""}</span></div>',
                unsafe_allow_html=True)
    _safe(_news)

with c_fn:
    def _funcs():
        _card_open("FUNCTIONS")
        funcs = [(f, t, d) for f, t, d in PAGES if t != "Home"]
        st.caption(f"{len(funcs)} functions available")
        cols = st.columns(3)
        for i, (f, title, desc) in enumerate(funcs):
            with cols[i % 3]:
                st.markdown(
                    f'<a href="{url_path(f)}" target="_self" '
                    f'style="text-decoration:none;">'
                    f'<div class="tt-func"><span class="tt-func-name">'
                    f'{title}</span><br><span class="tt-func-desc">{desc}'
                    f'</span></div></a>', unsafe_allow_html=True)
    _safe(_funcs)

render_footer(st)
