"""Compound AI — embedded third-party financial modeling copilot."""
import streamlit as st
import streamlit.components.v1 as components

from lib.config import apply_base_style, render_footer, render_sidebar

COMPOUND_URL = "https://getcompound.ai/login"

apply_base_style(st)
render_sidebar(st)
st.title("Compound AI")
st.markdown(
    '<div class="tt-subtitle">THIRD-PARTY SERVICE — COMPOUND '
    '(GETCOMPOUND.AI)</div>', unsafe_allow_html=True)

# ---- Capability panel (attributed to Compound) ----
c1, c2 = st.columns([2, 1])
with c1:
    st.markdown(
        '<div class="tt-func" style="margin-bottom:0.8rem;">'
        '<span class="tt-func-name">AI analyst for finance</span><br>'
        '<span class="tt-func-desc">Compound builds Excel models, drafts '
        'Word memos, creates PowerPoint decks, and analyzes data — with '
        'outputs the vendor describes as sourced and auditable.</span>'
        '</div>', unsafe_allow_html=True)
    caps = [
        ("Office automation", "Excel, Word, and PowerPoint tasks with AI"),
        ("Bulk analysis", "Work over thousands of files in a single chat"),
        ("Built-in data", "EDGAR, finance web search, and more"),
        ("Security", "SOC 2 Type II certified; vendor states it does not "
                     "train on customer data"),
    ]
    for name, desc in caps:
        st.markdown(
            f'<div style="display:flex;gap:12px;padding:6px 0;'
            f'border-bottom:1px solid #e4e4e7;">'
            f'<span style="font-family:Consolas,monospace;'
            f'text-transform:uppercase;font-size:0.75rem;'
            f'letter-spacing:0.06em;min-width:150px;color:#3f3f46;">'
            f'{name}</span>'
            f'<span style="color:#71717a;font-size:0.85rem;">{desc}</span>'
            f'</div>', unsafe_allow_html=True)
with c2:
    st.markdown('<div class="tt-func">'
                '<span class="tt-func-name">Session</span><br>'
                '<span class="tt-func-desc">Log in once in the embedded '
                'window below, or open Compound in its own tab for full '
                'screen work.</span></div>', unsafe_allow_html=True)
    st.link_button("Open Compound in new tab", COMPOUND_URL,
                   use_container_width=True)

st.divider()

# ---- Embedded workspace ----
mode = st.segmented_control("Workspace", ["Embedded", "Hidden"],
                            default="Embedded", key="compound_mode")
if mode == "Embedded":
    components.iframe(COMPOUND_URL, height=920, scrolling=True)
    st.caption(
        "If the panel stays blank or login loops, Compound (or its SSO "
        "provider) blocks running inside another page — use the new-tab "
        "button; your browser keeps you signed in there.")

render_footer(st)
