"""Macro — FRED indicators, yield curve, Claude pulse-check."""
import plotly.graph_objects as go
import streamlit as st

from lib import claude_analyst
from lib.config import apply_base_style, get_fred_key, render_footer, \
    render_sidebar
from lib.macro import get_indicators
from lib.rates import get_curve_history, get_yield_curve

apply_base_style(st)
render_sidebar(st)
st.title("Macro")

if not get_fred_key():
    st.info("Add your free **FRED_API_KEY** in the app Secrets to enable this page. "
            "Get one at fred.stlouisfed.org/docs/api — it takes a minute.")
    render_footer(st)
    st.stop()

indicators = get_indicators()
if not indicators:
    st.warning("Could not load FRED data. Check your key and connection.")
    render_footer(st)
    st.stop()

# ---- Metric tiles ----
cols = st.columns(4)
units = {"GDP": lambda v: f"${v/1000:,.1f}T", "Retail Sales": lambda v: f"{v:+.1f}%",
         "CPI YoY": lambda v: f"{v:.1f}%", "Core CPI YoY": lambda v: f"{v:.1f}%",
         "Unemployment": lambda v: f"{v:.1f}%", "Fed Funds": lambda v: f"{v:.2f}%",
         "10Y-2Y Spread": lambda v: f"{v:+.2f}%",
         "Industrial Production": lambda v: f"{v:+.1f}%"}
for i, (label, data) in enumerate(indicators.items()):
    fmt = units.get(label, lambda v: f"{v:,.2f}")
    cols[i % 4].metric(label, fmt(data["latest"]), help=data["desc"])

# ---- Indicator charts ----
st.divider()
pick = st.selectbox("Chart an indicator", list(indicators.keys()))
s = indicators[pick]["series"]
fig = go.Figure(go.Scatter(x=s.index, y=s.values, mode="lines",
                           line=dict(color="#38bdf8", width=2)))
fig.update_layout(template="plotly_white", height=380,
                  margin=dict(l=10, r=10, t=20, b=10),
                  paper_bgcolor="rgba(0,0,0,0)",
                  title=indicators[pick]["desc"])
st.plotly_chart(fig, use_container_width=True)

# ---- Yield curve ----
st.divider()
st.subheader("Treasury yield curve")
curve = get_yield_curve()
if not curve.empty:
    fig = go.Figure(go.Scatter(x=list(curve.index), y=curve.values,
                               mode="lines+markers",
                               line=dict(color="#a78bfa", width=2)))
    fig.update_layout(template="plotly_white", height=360,
                      margin=dict(l=10, r=10, t=20, b=10),
                      yaxis_ticksuffix="%", paper_bgcolor="rgba(0,0,0,0)")
    st.plotly_chart(fig, use_container_width=True)

hist = get_curve_history(("2Y", "10Y"))
if not hist.empty:
    fig = go.Figure()
    for col, color in zip(hist.columns, ("#f472b6", "#38bdf8")):
        fig.add_trace(go.Scatter(x=hist.index, y=hist[col], mode="lines",
                                 name=col, line=dict(color=color, width=1.5)))
    fig.update_layout(template="plotly_white", height=320,
                      margin=dict(l=10, r=10, t=30, b=10),
                      yaxis_ticksuffix="%", title="2Y vs 10Y over time",
                      paper_bgcolor="rgba(0,0,0,0)")
    st.plotly_chart(fig, use_container_width=True)

# ---- Claude pulse-check ----
st.divider()
st.subheader("AI macro pulse-check")
if claude_analyst.key_missing():
    st.info("Add your ANTHROPIC_API_KEY in the app Secrets to enable AI analysis.")
elif st.button("Generate pulse-check"):
    facts = "; ".join(f"{k}: {v['latest']:.2f}"
                      for k, v in indicators.items())
    if not curve.empty:
        facts += "; yield curve: " + ", ".join(
            f"{t}={v:.2f}%" for t, v in curve.items())
    with st.spinner("Analyzing…"):
        st.markdown(claude_analyst.macro_pulse(facts))

render_footer(st)
