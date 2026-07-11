"""PE/VC — deal headlines, TradedVC archive, The VC Corner archive."""
import streamlit as st

from lib.config import apply_base_style, render_footer, render_sidebar
from lib.news import time_ago
from lib.pevc import fetch_pe_deal_headlines, fetch_tradedvc, fetch_vccorner


def _safe(fn, *args):
    """Run a fetcher; never let one source crash the page."""
    try:
        return fn(*args), None
    except Exception as e:
        return None, f"{type(e).__name__}: {e}"

apply_base_style(st)
render_sidebar(st)
st.title("PE / VC")
st.markdown('<div class="tt-subtitle">PRIVATE MARKETS — DEALS, RAISES, '
            'AND OPERATOR RESEARCH · REFRESHES EVERY 15 MIN</div>',
            unsafe_allow_html=True)

tab_deals, tab_traded, tab_corner = st.tabs(
    ["Deals", "VC Traded", "VC Corner"])


def row(title, meta, link, summary="", badge=None):
    badge_html = ""
    if badge:
        badge_html = (f'<span style="font-family:Consolas,monospace;'
                      f'font-size:0.65rem;letter-spacing:0.06em;'
                      f'background:#c2410c;color:#fff;padding:1px 6px;'
                      f'margin-left:8px;vertical-align:middle;">{badge}'
                      f'</span>')
    summary_html = (f'<div style="color:#71717a;font-size:0.83rem;'
                    f'padding-top:2px;">{summary}</div>' if summary else "")
    st.markdown(
        f'<div style="padding:9px 0;border-bottom:1px solid #f4f4f5;">'
        f'<a href="{link}" target="_blank" style="color:#18181b;'
        f'text-decoration:none;font-weight:600;font-size:0.95rem;">'
        f'{title}</a>{badge_html}'
        f'<div style="font-family:Consolas,monospace;font-size:0.7rem;'
        f'letter-spacing:0.05em;color:#a1a1aa;padding-top:2px;">{meta}'
        f'</div>{summary_html}</div>', unsafe_allow_html=True)


with tab_deals:
    st.markdown('<div class="tt-func" style="margin:0.6rem 0;">'
                '<span class="tt-func-name">Private equity deal flow'
                '</span><br><span class="tt-func-desc">Live PE deal '
                'headlines aggregated from news wires. For Private Equity '
                'News (Dow Jones) coverage — a licensed, subscriber '
                'publication that cannot be syndicated here — use the '
                'direct link.</span></div>', unsafe_allow_html=True)
    st.link_button("Open PE News — Deals",
                   "https://www.penews.com/deals")
    st.divider()
    items, err = _safe(fetch_pe_deal_headlines)
    if err:
        st.error(f"Deals feed error — {err}")
        items = None
    if items:
        for it in items:
            meta = " · ".join(x for x in (
                it["source"], time_ago(it["published"])
                if it["published"] else "") if x)
            row(it["title"], meta.upper(), it["link"])
    else:
        st.warning("Headline feed unavailable right now — it retries on "
                   "the next 15-minute refresh.")

with tab_traded:
    st.markdown('<div class="tt-func" style="margin:0.6rem 0;">'
                '<span class="tt-func-name">TradedVC</span><br>'
                '<span class="tt-func-desc">Venture capital raises and '
                'dealflow digests — full archive, newest first. Source: '
                'vc.traded.co</span></div>', unsafe_allow_html=True)
    res, err = _safe(fetch_tradedvc)
    posts, diag = res if res else ([], err or "")
    if err:
        st.error(f"TradedVC error — {err}")
    if posts:
        st.caption(f"{len(posts)} archive issues — full archive, "
                   f"refreshed every 15 minutes")
        for p in posts:
            row(p["title"], (p["date"] or "TRADEDVC").upper()[:24],
                p["link"], p["summary"][:220])
    else:
        st.warning("Archive unavailable right now — it retries on the "
                   "next 15-minute refresh.")
        if diag:
            st.caption(f"Diagnostics: {diag}")
        st.link_button("Open TradedVC", "https://vc.traded.co/")

with tab_corner:
    st.markdown('<div class="tt-func" style="margin:0.6rem 0;">'
                '<span class="tt-func-name">The VC Corner</span><br>'
                '<span class="tt-func-desc">Operator-grade VC research, '
                'investor lists, and fundraising playbooks — the complete '
                'archive. Free posts open directly; subscriber posts are '
                'marked and open on The VC Corner for access.</span>'
                '</div>', unsafe_allow_html=True)
    posts, err = _safe(fetch_vccorner)
    if err:
        st.error(f"VC Corner error — {err}")
        posts = None
    if posts:
        q = st.text_input("Filter the archive",
                          placeholder="e.g. angel investors, pitch deck, "
                          "SaaS metrics", key="vcc_q").strip().lower()
        shown = [p for p in posts
                 if not q or q in p["title"].lower()
                 or q in p["subtitle"].lower()]
        free = sum(1 for p in shown if not p["paid"])
        st.caption(f"{len(shown)} posts ({free} free, "
                   f"{len(shown) - free} subscriber)")
        for p in shown:
            row(p["title"], p["date"], p["link"],
                p["subtitle"][:220],
                badge="SUBSCRIBER" if p["paid"] else None)
    else:
        st.warning("Archive unavailable right now — it retries on the "
                   "next 15-minute refresh.")
        st.link_button("Open The VC Corner", "https://www.thevccorner.com/")

render_footer(st)
