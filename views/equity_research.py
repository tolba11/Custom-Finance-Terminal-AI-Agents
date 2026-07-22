"""Equity Research — multi-agent analyst desk (TradingAgents-style)."""
import streamlit as st

from lib.agents import STAGES, run_pipeline
from lib.config import apply_base_style, get_anthropic_key, render_footer, \
    render_sidebar
from lib.symbol_search import symbol_search

apply_base_style(st)
render_sidebar(st)
st.title("Equity Research")
st.markdown('<div class="tt-subtitle">MULTI-AGENT ANALYST DESK — '
            'ANALYSTS, DEBATE, RISK, VERDICT</div>', unsafe_allow_html=True)

if not get_anthropic_key():
    st.info("Add your ANTHROPIC_API_KEY in the app Secrets to enable the "
            "research desk.")
    render_footer(st)
    st.stop()

STAGE_LABELS = {k: (label, group) for k, label, group in STAGES}
VERDICT_COLORS = {"BUY": "#16c784", "HOLD": "#b45309", "SELL": "#ea3943"}

# ---- controls ----
c1, c2, c3, c4 = st.columns([2, 2, 2, 1])
with c1:
    ticker = symbol_search("What equity would you like to analyze?",
                           "er", "MSFT")
with c2:
    depth = st.segmented_control("Research depth",
                                 ["Shallow", "Medium", "Deep"],
                                 default="Shallow",
                                 key="er_depth") or "Shallow"
with c3:
    mode = st.segmented_control("Model", ["Standard", "Opus 4.8"],
                                default="Standard",
                                key="er_mode") or "Standard"
with c4:
    st.markdown("<div style='height:1.8rem'></div>", unsafe_allow_html=True)
    run = st.button("Run analysis", type="primary",
                    use_container_width=True)

est = {"Shallow": "~60-90s", "Medium": "~2 min", "Deep": "~3-5 min"}[depth]
cost = ("roughly $0.05-0.15/run" if mode == "Standard"
        else "roughly $1-3/run — Opus is the premium model")
st.caption(f"Runs eleven-plus model calls on your Anthropic key "
           f"({est}, {cost}).")

left, right = st.columns([1, 2.6], gap="medium")


def render_progress(container, statuses, duration=None):
    with container:
        st.markdown("**Progress**")
        if duration is not None:
            st.caption(f"Analyzing {ticker} | Duration: "
                       f"{int(duration//60):02d}:{int(duration%60):02d}")
        group = None
        for key, label, grp in STAGES:
            if grp != group:
                group = grp
                st.markdown(
                    f'<div style="font-family:Consolas,monospace;'
                    f'text-transform:uppercase;font-size:0.72rem;'
                    f'letter-spacing:0.08em;color:#8a93a6;'
                    f'margin:10px 0 2px 0;">{grp}</div>',
                    unsafe_allow_html=True)
            s = statuses.get(key, "pending")
            color = {"pending": "#5c6575", "running": "#f97316",
                     "done": "#16c784"}[s]
            text = {"pending": "pending", "running": "generating",
                    "done": "completed"}[s]
            st.markdown(
                f'<div style="display:flex;justify-content:space-between;'
                f'padding:3px 0;border-bottom:1px solid #1a2029;'
                f'font-size:0.85rem;"><span>{label}</span>'
                f'<span style="color:{color};font-family:Consolas,monospace;'
                f'font-size:0.75rem;">{text}</span></div>',
                unsafe_allow_html=True)


if run and ticker:
    statuses = {}
    prog_box = left.container()
    status_area = right.empty()
    with status_area.container():
        st.markdown("**Desk running**")
        live = st.status(f"Analyzing {ticker}", expanded=False)

    def on_stage(key, state):
        statuses[key] = state
        prog_box.empty()
        render_progress(prog_box.container(), statuses)
        label = STAGE_LABELS[key][0]
        live.update(label=f"{label} — "
                    f"{'working' if state == 'running' else 'completed'}")

    try:
        with st.spinner(""):
            result = run_pipeline(ticker, depth=depth, mode=mode,
                                  on_stage=on_stage)
        st.session_state["er_result"] = result
        live.update(label="Analysis complete", state="complete")
        st.rerun()
    except Exception as e:
        live.update(label="Run failed", state="error")
        st.error(f"The desk hit an error: {e}")
        st.caption("Common causes: Anthropic credit balance empty, or a "
                   "data source briefly rate-limited. Try again.")

result = st.session_state.get("er_result")
if result and not run:
    statuses = {k: "done" for k, _, _ in STAGES}
    render_progress(left.container(), statuses,
                    duration=result["duration"])
    with left.container():
        st.markdown("<div style='height:12px'></div>",
                    unsafe_allow_html=True)
        st.caption(f"Depth: {result['depth']} · Model: {result['mode']}")

    with right:
        v = result["verdict"]
        color = VERDICT_COLORS.get(v, "#b45309")
        st.markdown(
            f'<div style="border:1px solid #252c3b;border-left:4px solid '
            f'{color};padding:0.9rem 1.2rem;background:#161b26;">'
            f'<span style="font-family:Consolas,monospace;font-size:0.72rem;'
            f'letter-spacing:0.1em;color:#8a93a6;">FINAL RECOMMENDATION '
            f'— {result["ticker"]}</span><br>'
            f'<span style="font-family:Consolas,monospace;font-weight:700;'
            f'font-size:2.2rem;color:{color};">{v}</span></div>',
            unsafe_allow_html=True)
        st.caption("Automated multi-agent model output for research — not "
                   "advice from a licensed advisor.")
        st.markdown("### Final Trade Decision")
        st.markdown(result["reports"].get("verdict_body", ""))

        st.divider()
        st.markdown("### Agent Reports")
        for key, label, _ in STAGES[:-1]:
            with st.expander(label.upper()):
                st.markdown(result["reports"].get(key, "No report."))
elif not result and not run:
    render_progress(left.container(), {})
    with right:
        st.markdown(
            '<div class="tt-func"><span class="tt-func-name">How it works'
            '</span><br><span class="tt-func-desc">Four analysts (market, '
            'sentiment/flow, news, fundamentals) research the name from '
            'live data. Bull and bear advocates debate it, an evaluator '
            'judges the arguments, the trading desk drafts a plan, three '
            'risk analysts stress it, and the portfolio manager issues the '
            'final verdict. Every report is preserved below the verdict.'
            '</span></div>', unsafe_allow_html=True)

render_footer(st)
