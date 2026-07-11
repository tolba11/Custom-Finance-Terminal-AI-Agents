"""Perceptis AI — third-party executive presentation maker (launch panel)."""
import streamlit as st

from lib.config import apply_base_style, render_footer, render_sidebar

PERCEPTIS_URL = "https://app.perceptis.ai/"

apply_base_style(st)
render_sidebar(st)
st.title("Perceptis AI")
st.markdown(
    '<div class="tt-subtitle">THIRD-PARTY SERVICE — PERCEPTIS '
    '(PERCEPTIS.AI)</div>', unsafe_allow_html=True)

c1, c2 = st.columns([2, 1])
with c1:
    st.markdown(
        '<div class="tt-func" style="margin-bottom:0.8rem;">'
        '<span class="tt-func-name">Executive presentation AI</span><br>'
        '<span class="tt-func-desc">Perceptis turns a prompt into a '
        'structured, board-ready deck — consulting-grade storylines with '
        'cited claims, delivered as fully editable PowerPoint files.</span>'
        '</div>', unsafe_allow_html=True)
    caps = [
        ("Slidekick", "Pitch decks, strategy memos, and financial reports "
                      "generated from a prompt"),
        ("Cited output", "Automatic source citations on factual statements"),
        ("Your templates", "Generates directly into your organization's "
                           "PowerPoint master — fonts, colors, structure"),
        ("Chatalyst", "Chat with your own documents to extract insights "
                      "and fact-check claims"),
        ("Security", "SOC 2 compliant; vendor states it does not train on "
                     "customer data"),
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
                '<span class="tt-func-desc">Perceptis opens in its own '
                'browser tab. Your browser keeps you signed in between '
                'visits.</span></div>', unsafe_allow_html=True)
    st.link_button("Log in to Perceptis", PERCEPTIS_URL,
                   type="primary", use_container_width=True)

render_footer(st)
