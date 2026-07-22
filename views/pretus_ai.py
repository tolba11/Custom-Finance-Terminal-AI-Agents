"""Pretus AI — third-party investment banking interview prep (launch)."""
import streamlit as st

from lib.config import apply_base_style, render_footer, render_sidebar

PRETUS_URL = ("https://heypretus.com/study-session/"
              "01a16bb1-2c9b-4119-b323-a18c71d3a049")

apply_base_style(st)
render_sidebar(st)
st.title("Pretus AI")
st.markdown('<div class="tt-subtitle">THIRD-PARTY SERVICE — PRETUS '
            '(HEYPRETUS.COM)</div>', unsafe_allow_html=True)

c1, c2 = st.columns([2, 1])
with c1:
    st.markdown(
        '<div class="tt-func" style="margin-bottom:0.8rem;">'
        '<span class="tt-func-name">AI-powered investment banking '
        'interview prep</span><br>'
        '<span class="tt-func-desc">Pretus is an AI practice platform for '
        'investment banking interviews — real questions from top firms '
        'with personalized feedback on your answers.</span></div>',
        unsafe_allow_html=True)
    caps = [
        ("Mock interviews", "AI-run practice sessions modeled on real "
                            "IB interview formats"),
        ("Question bank", "Real questions asked at top firms — technical "
                          "and behavioral"),
        ("Feedback", "Personalized feedback on each answer to sharpen "
                     "delivery"),
        ("Resources", "Comprehensive prep material alongside the "
                      "practice sessions"),
    ]
    for name, desc in caps:
        st.markdown(
            f'<div style="display:flex;gap:12px;padding:6px 0;'
            f'border-bottom:1px solid #252c3b;">'
            f'<span style="font-family:Consolas,monospace;'
            f'text-transform:uppercase;font-size:0.75rem;'
            f'letter-spacing:0.06em;min-width:150px;color:#b7c0d0;">'
            f'{name}</span>'
            f'<span style="color:#8a93a6;font-size:0.85rem;">{desc}</span>'
            f'</div>', unsafe_allow_html=True)
with c2:
    st.markdown('<div class="tt-func">'
                '<span class="tt-func-name">Study session</span><br>'
                '<span class="tt-func-desc">Opens your Pretus study '
                'session in its own browser tab. Your browser keeps you '
                'signed in between visits.</span></div>',
                unsafe_allow_html=True)
    st.link_button("Log in to Pretus", PRETUS_URL,
                   type="primary", use_container_width=True)

render_footer(st)
