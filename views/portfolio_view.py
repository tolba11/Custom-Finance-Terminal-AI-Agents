"""Portfolio — holdings entry, value, allocation, risk, AI review."""
import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from lib import claude_analyst
from lib.charts import render_gauge
from lib.config import apply_base_style, render_footer, render_sidebar
from lib.market_data import get_history, get_quotes_bulk, \
    get_stock_fundamentals
from lib.portfolio import load_portfolio, save_portfolio
from lib.risk import compute_risk_score

apply_base_style(st)
render_sidebar(st)
st.title("Portfolio")

holdings = load_portfolio()

# ---- Editor ----
with st.expander("Edit holdings", expanded=not holdings):
    df_edit = st.data_editor(
        pd.DataFrame(holdings or [{"ticker": "", "shares": 0.0,
                                   "cost_basis": 0.0}]),
        num_rows="dynamic", use_container_width=True,
        column_config={
            "ticker": st.column_config.TextColumn("Ticker", required=True),
            "shares": st.column_config.NumberColumn("Shares", min_value=0.0),
            "cost_basis": st.column_config.NumberColumn(
                "Cost basis ($/share)", min_value=0.0),
        })
    if st.button("Save portfolio"):
        clean = [
            {"ticker": str(r["ticker"]).strip().upper(),
             "shares": float(r["shares"] or 0),
             "cost_basis": float(r["cost_basis"] or 0)}
            for _, r in df_edit.iterrows()
            if str(r["ticker"]).strip() and float(r["shares"] or 0) > 0
        ]
        save_portfolio(clean)
        st.success(f"Saved {len(clean)} holdings.")
        st.rerun()

if not holdings:
    st.info("Add your first holding above to get started.")
    render_footer(st)
    st.stop()

# ---- Valuation ----
tickers = tuple(h["ticker"] for h in holdings)
quotes = get_quotes_bulk(tickers)

rows = []
for h in holdings:
    tk = h["ticker"]
    q = quotes.get(tk, {})
    price = q.get("price")
    value = price * h["shares"] if price else None
    cost = h["cost_basis"] * h["shares"]
    rows.append({
        "Ticker": tk, "Shares": h["shares"],
        "Cost basis": h["cost_basis"], "Price": price,
        "Value": value, "Cost": cost,
        "Return ($)": value - cost if value is not None else None,
        "Return (%)": (value / cost - 1) * 100
        if value is not None and cost else None,
    })
df = pd.DataFrame(rows)
total_value = df["Value"].sum(skipna=True)
total_cost = df["Cost"].sum(skipna=True)

m1, m2, m3 = st.columns(3)
m1.metric("Current value", f"${total_value:,.0f}")
m2.metric("Total cost", f"${total_cost:,.0f}")
ret = (total_value / total_cost - 1) * 100 if total_cost else 0
m3.metric("Total return", f"${total_value - total_cost:,.0f}",
          f"{ret:+.1f}%")

st.dataframe(
    df.style.format({"Cost basis": "${:,.2f}", "Price": "${:,.2f}",
                     "Value": "${:,.0f}", "Cost": "${:,.0f}",
                     "Return ($)": "${:,.0f}", "Return (%)": "{:+.1f}%"},
                    na_rep="—"),
    hide_index=True, use_container_width=True)

# ---- Allocation + sector pies ----
st.divider()
c1, c2 = st.columns(2)
valid = df.dropna(subset=["Value"])
with c1:
    st.subheader("Allocation")
    fig = go.Figure(go.Pie(labels=valid["Ticker"], values=valid["Value"],
                           hole=0.45))
    fig.update_layout(template="plotly_white", height=360,
                      margin=dict(l=10, r=10, t=10, b=10),
                      paper_bgcolor="rgba(0,0,0,0)")
    st.plotly_chart(fig, use_container_width=True)
with c2:
    st.subheader("Sector breakdown")
    sectors = {}
    for _, r in valid.iterrows():
        info = get_stock_fundamentals(r["Ticker"])
        sec = info.get("sector") or ("ETF/Fund" if (info.get("quoteType")
                                                    == "ETF") else "Other")
        sectors[sec] = sectors.get(sec, 0) + r["Value"]
    if sectors:
        fig = go.Figure(go.Pie(labels=list(sectors.keys()),
                               values=list(sectors.values()), hole=0.45))
        fig.update_layout(template="plotly_white", height=360,
                          margin=dict(l=10, r=10, t=10, b=10),
                          paper_bgcolor="rgba(0,0,0,0)")
        st.plotly_chart(fig, use_container_width=True)

# ---- Portfolio risk ----
st.divider()
st.subheader("Risk profile")
weights = list(valid["Value"] / total_value) if total_value else []
port_hist = None
for _, r in valid.iterrows():
    h = get_history(r["Ticker"], "3Y")
    if h.empty:
        continue
    w = r["Value"] / total_value
    series = h["Close"].pct_change().fillna(0) * w
    port_hist = series if port_hist is None else port_hist.add(series,
                                                               fill_value=0)
if port_hist is not None:
    port_curve = (1 + port_hist).cumprod() * 100
    risk = compute_risk_score(port_curve, weights)
    g, t = st.columns([1, 1])
    with g:
        st.plotly_chart(render_gauge(risk["score"],
                                     f"Risk: {risk['label']}",
                                     "Volatility, drawdown, concentration",
                                     bands="risk"),
                        use_container_width=True)
    with t:
        st.markdown(f"- Annualized volatility: **{risk['volatility']:.1%}**")
        st.markdown(f"- Max drawdown (3Y): **{risk['max_drawdown']:.1%}**")
        st.markdown(f"- Concentration: **{risk['concentration']:.0%}** "
                    "(higher = fewer, larger positions)")

# ---- AI review ----
st.divider()
st.subheader("AI portfolio review")
if claude_analyst.key_missing():
    st.info("Add your ANTHROPIC_API_KEY in the app Secrets to enable AI analysis.")
elif st.button("Generate review"):
    facts = "; ".join(
        f"{r['Ticker']}: {r['Value']/total_value:.0%} of portfolio, "
        f"return {r['Return (%)']:.0f}%"
        for _, r in valid.iterrows() if r["Return (%)"] is not None)
    facts += f". Total value ${total_value:,.0f}."
    with st.spinner("Analyzing…"):
        st.markdown(claude_analyst.portfolio_analysis(facts))

render_footer(st)
