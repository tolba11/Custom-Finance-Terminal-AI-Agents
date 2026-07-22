"""Pyramid Copilot — page-aware AI assistant panel on every view,
modeled on OpenBB Workspace's Copilot (chat that uses the current
dashboard as context)."""
import streamlit as st

from lib.config import get_anthropic_key
from lib.deep_finance import chat_anthropic

MODEL = "claude-sonnet-5"


def copilot(page: str, context: str = ""):
    """Render the Copilot popover. `context` is live page data the
    model can cite (ticker, quotes, stats)."""
    with st.popover("COPILOT"):
        st.markdown(
            f'<div style="font-family:Consolas,monospace;font-size:'
            f'0.62rem;letter-spacing:0.1em;color:#8a93a6;">CONTEXT: '
            f'{page.upper()}</div>', unsafe_allow_html=True)
        if not get_anthropic_key():
            st.info("Add ANTHROPIC_API_KEY in Secrets to enable Copilot.")
            return
        hist = st.session_state.setdefault("cp_hist", [])
        for m in hist[-8:]:
            if m["role"] == "user":
                st.markdown(
                    f'<div style="border-left:2px solid #8a93a6;'
                    f'padding:1px 8px;margin:6px 0;color:#8a93a6;'
                    f'font-size:0.82rem;">{m["content"]}</div>',
                    unsafe_allow_html=True)
            else:
                st.markdown(m["content"])
        q = st.text_input("Ask Copilot", key="cp_q",
                          placeholder=f"Ask about {page}…",
                          label_visibility="collapsed")
        c1, c2 = st.columns([1.4, 1])
        with c1:
            go = st.button("Ask", key="cp_go", use_container_width=True)
        with c2:
            if st.button("Clear", key="cp_clear",
                         use_container_width=True):
                st.session_state["cp_hist"] = []
                st.rerun()
        if go and q.strip():
            hist.append({"role": "user", "content": q.strip()})
            sys_ctx = (
                "You are Pyramid Copilot, the AI assistant inside the "
                f"Pyramid Terminal finance app. The user is on the {page} "
                "view. Live data currently on their screen:\n"
                f"{(context or 'none provided')[:6000]}\n"
                "Answer concisely and quantitatively; cite the on-screen "
                "numbers when relevant.")
            msgs = [{"role": m["role"], "content": m["content"]}
                    for m in hist[-8:]]
            with st.spinner("Thinking…"):
                text, err = chat_anthropic(MODEL, msgs, context=sys_ctx)
            hist.append({"role": "assistant",
                         "content": text or f"Copilot error: {err}"})
            st.rerun()
