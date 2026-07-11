"""Deep Finance — multi-model research chat (Claude + Perplexity)."""
import streamlit as st

from lib import deep_finance as dfn
from lib.config import apply_base_style, render_sidebar

apply_base_style(st)
render_sidebar(st)
st.title("Deep Finance")
st.markdown('<div class="tt-subtitle">MULTI-MODEL RESEARCH CHAT — '
            'CLAUDE FABLE 5 · OPUS 4.8 · SONNET 5 · PERPLEXITY SONAR</div>',
            unsafe_allow_html=True)

c1, c2, c3 = st.columns([3, 1.4, 0.8])
with c1:
    model_name = st.segmented_control(
        "Model", list(dfn.MODELS.keys()),
        default="Claude Sonnet 5", key="df_model") or "Claude Sonnet 5"
model = dfn.MODELS[model_name]
with c2:
    ground = st.toggle("Web grounding", value=False, key="df_ground",
                       help="For Claude models: pull live Perplexity "
                            "Search results into the prompt.",
                       disabled=(model["provider"] != "anthropic"
                                 or not dfn.perplexity_ready()))
with c3:
    st.markdown("<div style='height:1.7rem'></div>", unsafe_allow_html=True)
    if st.button("New chat", use_container_width=True, key="df_new"):
        st.session_state["df_history"] = []
        st.rerun()

st.caption(f"{model_name} — {model['hint']}. Runs on your own API keys; "
           "each message costs credits.")

if model["provider"] == "anthropic" and not dfn.anthropic_ready():
    st.info("Add your ANTHROPIC_API_KEY in the app Secrets to chat with "
            "Claude models.")
    st.stop()
if model["provider"] == "perplexity" and not dfn.perplexity_ready():
    st.info('Add your Perplexity key in the app Secrets to chat with '
            'Sonar models:\n\n`PERPLEXITY_API_KEY = "pplx-..."`')
    st.stop()

history = st.session_state.setdefault("df_history", [])

for turn in history:
    with st.chat_message(turn["role"]):
        st.markdown(turn["content"])
        if turn.get("citations"):
            st.markdown(
                '<div style="font-family:Consolas,monospace;font-size:'
                '0.7rem;letter-spacing:0.06em;color:#71717a;'
                'padding-top:6px;">SOURCES</div>', unsafe_allow_html=True)
            for i, c in enumerate(turn["citations"][:8], 1):
                st.markdown(f'<a href="{c}" target="_blank" '
                            f'style="font-size:0.78rem;color:#c2410c;">'
                            f'[{i}] {c[:90]}</a>', unsafe_allow_html=True)

prompt = st.chat_input(f"Ask {model_name} anything markets…")
if prompt:
    history.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)
    msgs = [{"role": t["role"], "content": t["content"]} for t in history]
    with st.chat_message("assistant"):
        with st.spinner(f"{model_name} thinking…"):
            if model["provider"] == "anthropic":
                context = dfn.web_ground(prompt) if ground else ""
                text, err = dfn.chat_anthropic(model["id"], msgs, context)
                cites = []
                if context and text:
                    text += ("\n\n*Grounded with live Perplexity Search "
                             "results.*")
            else:
                text, cites, err = dfn.chat_perplexity(model["id"], msgs)
        if err:
            st.error(f"{model_name} error — {err}")
            history.pop()
        else:
            st.markdown(text)
            if cites:
                st.markdown(
                    '<div style="font-family:Consolas,monospace;font-size:'
                    '0.7rem;letter-spacing:0.06em;color:#71717a;'
                    'padding-top:6px;">SOURCES</div>',
                    unsafe_allow_html=True)
                for i, c in enumerate(cites[:8], 1):
                    st.markdown(f'<a href="{c}" target="_blank" '
                                f'style="font-size:0.78rem;color:#c2410c;">'
                                f'[{i}] {c[:90]}</a>', unsafe_allow_html=True)
            history.append({"role": "assistant", "content": text,
                            "citations": cites})
