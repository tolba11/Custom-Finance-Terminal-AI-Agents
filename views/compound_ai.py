"""Compound AI — third-party financial modeling copilot (launch panel)."""
import streamlit as st

from lib.config import apply_base_style, render_footer, render_sidebar

COMPOUND_URL = "https://getcompound.ai/login"

apply_base_style(st)
render_sidebar(st)
st.title("Compound AI")
st.markdown(
    '<div class="tt-subtitle">THIRD-PARTY SERVICE — COMPOUND '
    '(GETCOMPOUND.AI)</div>', unsafe_allow_html=True)

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
                '<span class="tt-func-name">Workspace</span><br>'
                '<span class="tt-func-desc">Compound does not permit '
                'embedding inside other applications, so it opens in its '
                'own browser tab. Your browser keeps you signed in between '
                'visits.</span></div>', unsafe_allow_html=True)
    st.link_button("Log in to Compound", COMPOUND_URL,
                   type="primary", use_container_width=True)

render_footer(st)
