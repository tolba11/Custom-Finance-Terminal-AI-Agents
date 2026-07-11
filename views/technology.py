"""Technology — TechCrunch section reader."""
import streamlit as st

from lib.config import apply_base_style, render_footer, render_sidebar
from lib.news import time_ago
from lib.techcrunch import SECTIONS, fetch_techcrunch

apply_base_style(st)
render_sidebar(st)
st.title("Technology")
st.markdown('<div class="tt-subtitle">TECHCRUNCH — SECTION FEEDS · '
            'REFRESHES EVERY 15 MIN</div>', unsafe_allow_html=True)

st.markdown('<div class="tt-func" style="margin-bottom:0.8rem;">'
            '<span class="tt-func-name">TechCrunch</span><br>'
            '<span class="tt-func-desc">Latest reporting across startups, '
            'venture, security, AI, Apple, and apps. Headlines and '
            'summaries link to the full articles on techcrunch.com.</span>'
            '</div>', unsafe_allow_html=True)

section = st.segmented_control("Section", list(SECTIONS.keys()),
                               default="Latest",
                               key="tc_section") or "Latest"

try:
    articles, err = fetch_techcrunch(section)
except Exception as e:
    articles, err = [], f"{type(e).__name__}: {e}"

if err and not articles:
    st.error(f"TechCrunch feed error — {err}")
    st.caption("It retries automatically on the next 15-minute refresh.")
    st.link_button("Open TechCrunch", "https://techcrunch.com/")
elif articles:
    q = st.text_input("Filter articles", placeholder="e.g. Anthropic, "
                      "fundraise, breach", key="tc_q").strip().lower()
    shown = [a for a in articles
             if not q or q in a["title"].lower()
             or q in a["summary"].lower()]
    st.caption(f"{len(shown)} articles — {section}")
    for a in shown:
        meta = " · ".join(x for x in (
            a["author"],
            time_ago(a["published"]) if a["published"] else "") if x)
        st.markdown(
            f'<div style="padding:9px 0;border-bottom:1px solid #f4f4f5;">'
            f'<a href="{a["link"]}" target="_blank" style="color:#18181b;'
            f'text-decoration:none;font-weight:600;font-size:0.95rem;">'
            f'{a["title"]}</a>'
            f'<div style="font-family:Consolas,monospace;font-size:0.7rem;'
            f'letter-spacing:0.05em;color:#a1a1aa;padding-top:2px;">'
            f'{meta.upper()}</div>'
            f'<div style="color:#71717a;font-size:0.83rem;padding-top:2px;">'
            f'{a["summary"][:260]}</div></div>', unsafe_allow_html=True)

render_footer(st)
