"""Portfolio — holdings, performance vs benchmark, exposures, risk, AI."""
import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from lib import claude_analyst
from lib.charts import GREEN, RED, render_gauge
from lib.config import apply_base_style, render_footer, render_sidebar
from lib.logos import logo_img_html
from lib.market_data import get_quotes_bulk, get_stock_fundamentals
from lib.portfolio import load_portfolio, save_portfolio
from lib.portfolio_analytics import build_portfolio_series, perf_stats
from lib.risk import compute_risk_score

apply_base_style(st)
render_sidebar(st)
st.title("Portfolio")
st.markdown('<div class="tt-subtitle">PERFORMANCE · EXPOSURES · RISK — '
            'BENCHMARKED TO SPY · REFRESHES EVERY 15 MIN</div>',
            unsafe_allow_html=True)

holdings = load_portfolio()

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
    price, chg = q.get("price"), q.get("change_pct")
    value = price * h["shares"] if price else None
    cost = h["cost_basis"] * h["shares"]
    rows.append({"tk": tk, "shares": h["shares"], "cb": h["cost_basis"],
                 "price": price, "chg": chg, "value": value, "cost": cost})
df = pd.DataFrame(rows)
valid = df.dropna(subset=["value"])
total_value = valid["value"].sum()
total_cost = df["cost"].sum()
day_pnl = sum((r["value"] or 0) * (r["chg"] or 0) / 100
              / (1 + (r["chg"] or 0) / 100) for _, r in valid.iterrows())

k1, k2, k3, k4 = st.columns(4)
k1.metric("Value", f"${total_value:,.0f}")
k2.metric("Cost", f"${total_cost:,.0f}")
ret = (total_value / total_cost - 1) * 100 if total_cost else 0
k3.metric("Total P&L", f"${total_value - total_cost:,.0f}",
          f"{ret:+.1f}%")
k4.metric("Day P&L", f"${day_pnl:,.0f}",
          f"{day_pnl / total_value * 100:+.2f}%" if total_value else None)

# ---- Performance vs benchmark ----
st.divider()
p_l, p_r = st.columns([3, 1.2])
with p_r:
    horizon = st.segmented_control("Horizon", ["1Y", "3Y"],
                                   default="1Y", key="pf_h") or "1Y"
with p_l:
    st.subheader(f"Performance vs SPY — {horizon}")
hkey = tuple((h["ticker"], h["shares"]) for h in holdings)
series = build_portfolio_series(hkey, horizon)
if series and series["value"] is not None and len(series["value"]) > 5:
    v, b = series["value"], series["bench"]
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=v.index, y=v / v.iloc[0] * 100,
                             name="Portfolio", mode="lines",
                             line=dict(color="#c2410c", width=2.2)))
    if b is not None and b.dropna().shape[0] > 5:
        bb = b.dropna()
        fig.add_trace(go.Scatter(x=bb.index, y=bb / bb.iloc[0] * 100,
                                 name="SPY", mode="lines",
                                 line=dict(color="#71717a", width=1.6,
                                           dash="dot")))
    fig.add_hline(y=100, line_color="#d4d4d8", line_width=1,
                  line_dash="dot")
    fig.update_layout(template="plotly_white", height=380,
                      margin=dict(l=10, r=10, t=10, b=10),
                      legend=dict(orientation="h"),
                      yaxis_title="Indexed to 100",
                      paper_bgcolor="rgba(0,0,0,0)")
    st.plotly_chart(fig, use_container_width=True)

    stats = perf_stats(v, b)
    scols = st.columns(5)
    for i, (label, val) in enumerate(stats.items()):
        with scols[i % 5]:
            st.markdown(
                f'<div style="border:1px solid #e4e4e7;border-left:3px '
                f'solid #c2410c;padding:0.4rem 0.6rem;margin-bottom:0.5rem;'
                f'background:#fff;"><span style="font-family:Consolas,'
                f'monospace;font-size:0.65rem;letter-spacing:0.07em;'
                f'color:#71717a;">{label.upper()}</span><br>'
                f'<span style="font-family:Consolas,monospace;'
                f'font-weight:600;font-size:1.05rem;">{val}</span></div>',
                unsafe_allow_html=True)
else:
    st.caption("Performance history builds once holdings have price data.")

# ---- Holdings grid ----
st.divider()
st.subheader("Holdings")
hdr = ('<div style="display:grid;grid-template-columns:26px 4em '
       'minmax(0,1fr) 5em 5.5em 5em 6.5em 6.5em 5.5em;gap:8px;'
       'padding:4px 0;font-family:Consolas,monospace;font-size:0.65rem;'
       'letter-spacing:0.07em;color:#71717a;border-bottom:2px solid '
       '#e4e4e7;"><span></span><span>TICKER</span><span>NAME</span>'
       '<span style="text-align:right;">WEIGHT</span>'
       '<span style="text-align:right;">PRICE</span>'
       '<span style="text-align:right;">DAY</span>'
       '<span style="text-align:right;">VALUE</span>'
       '<span style="text-align:right;">P&L</span>'
       '<span style="text-align:right;">P&L %</span></div>')
st.markdown(hdr, unsafe_allow_html=True)
for _, r in valid.sort_values("value", ascending=False).iterrows():
    info = get_stock_fundamentals(r["tk"])
    name = (info.get("shortName") or info.get("longName") or "")[:26]
    w = r["value"] / total_value if total_value else 0
    pnl = r["value"] - r["cost"]
    pnl_pct = (r["value"] / r["cost"] - 1) * 100 if r["cost"] else 0
    dcolor = GREEN if (r["chg"] or 0) >= 0 else RED
    pcolor = GREEN if pnl >= 0 else RED
    st.markdown(
        f'<div style="display:grid;grid-template-columns:26px 4em '
        f'minmax(0,1fr) 5em 5.5em 5em 6.5em 6.5em 5.5em;gap:8px;'
        f'align-items:center;padding:6px 0;border-bottom:1px solid '
        f'#f4f4f5;">{logo_img_html(r["tk"], 22)}'
        f'<b style="font-size:0.85rem;">{r["tk"]}</b>'
        f'<span style="color:#71717a;font-size:12px;white-space:nowrap;'
        f'overflow:hidden;text-overflow:ellipsis;">{name}</span>'
        f'<span style="text-align:right;font-family:Consolas,monospace;'
        f'font-size:0.85rem;">{w:.1%}</span>'
        f'<span style="text-align:right;font-family:Consolas,monospace;'
        f'font-size:0.85rem;">{r["price"]:,.2f}</span>'
        f'<span style="text-align:right;font-family:Consolas,monospace;'
        f'font-size:0.8rem;color:{dcolor};">'
        f'{(r["chg"] or 0):+.2f}%</span>'
        f'<span style="text-align:right;font-family:Consolas,monospace;'
        f'font-size:0.85rem;">${r["value"]:,.0f}</span>'
        f'<span style="text-align:right;font-family:Consolas,monospace;'
        f'font-size:0.85rem;color:{pcolor};">${pnl:,.0f}</span>'
        f'<span style="text-align:right;font-family:Consolas,monospace;'
        f'font-size:0.85rem;color:{pcolor};">{pnl_pct:+.1f}%</span></div>',
        unsafe_allow_html=True)

# ---- Exposures + correlation ----
st.divider()
e_l, e_r = st.columns(2)
with e_l:
    st.subheader("Sector exposure")
    sectors = {}
    for _, r in valid.iterrows():
        info = get_stock_fundamentals(r["tk"])
        sec = info.get("sector") or ("ETF/Fund" if (info.get("quoteType")
                                                    == "ETF") else "Other")
        sectors[sec] = sectors.get(sec, 0) + r["value"]
    if sectors:
        s = pd.Series(sectors).sort_values() / total_value * 100
        fig = go.Figure(go.Bar(x=s.values, y=s.index, orientation="h",
                               marker_color="#c2410c",
                               text=[f"{v:.1f}%" for v in s.values],
                               textposition="outside"))
        fig.update_layout(template="plotly_white",
                          height=max(220, 40 * len(s)),
                          margin=dict(l=10, r=60, t=10, b=10),
                          xaxis_ticksuffix="%",
                          paper_bgcolor="rgba(0,0,0,0)")
        st.plotly_chart(fig, use_container_width=True)
    top = valid.sort_values("value", ascending=False)["value"]
    conc = top.head(3).sum() / total_value if total_value else 0
    st.caption(f"Top-3 positions are {conc:.0%} of the portfolio.")
with e_r:
    st.subheader("Holdings correlation")
    if series and series["returns"] is not None and \
            series["returns"].shape[1] >= 2:
        corr = series["returns"].corr().round(2)
        fig = go.Figure(go.Heatmap(
            z=corr.values, x=corr.columns, y=corr.index,
            zmin=-1, zmax=1, colorscale=[[0, "#b91c1c"],
                                         [0.5, "#ffffff"],
                                         [1, "#047857"]],
            text=corr.values, texttemplate="%{text}"))
        fig.update_layout(template="plotly_white", height=360,
                          margin=dict(l=10, r=10, t=10, b=10),
                          paper_bgcolor="rgba(0,0,0,0)")
        st.plotly_chart(fig, use_container_width=True)
        st.caption("Daily-return correlation — lighter is more "
                   "diversifying.")
    else:
        st.caption("Add at least two holdings with price history to see "
                   "the correlation matrix.")

# ---- Risk gauge ----
st.divider()
st.subheader("Risk profile")
if series and series["value"] is not None and len(series["value"]) > 20:
    weights = list(valid["value"] / total_value)
    risk = compute_risk_score(series["value"], weights)
    g, t = st.columns([1, 1])
    with g:
        st.plotly_chart(render_gauge(risk["score"],
                                     f"Risk: {risk['label']}",
                                     "Volatility, drawdown, concentration",
                                     bands="risk"),
                        use_container_width=True)
    with t:
        st.markdown(f"- Annualized volatility: **{risk['volatility']:.1%}**")
        st.markdown(f"- Max drawdown: **{risk['max_drawdown']:.1%}**")
        st.markdown(f"- Concentration: **{risk['concentration']:.0%}** "
                    "(higher = fewer, larger positions)")

# ---- AI review ----
st.divider()
st.subheader("AI portfolio review")
if claude_analyst.key_missing():
    st.info("Add your ANTHROPIC_API_KEY in the app Secrets to enable AI "
            "analysis.")
elif st.button("Generate review"):
    facts = "; ".join(
        f"{r['tk']}: {r['value']/total_value:.0%} weight, "
        f"P&L {((r['value']/r['cost'])-1)*100 if r['cost'] else 0:+.0f}%"
        for _, r in valid.iterrows())
    facts += f". Total ${total_value:,.0f}."
    if series:
        facts += " Stats: " + "; ".join(
            f"{k} {v}" for k, v in perf_stats(series["value"],
                                              series["bench"]).items())
    with st.spinner("Analyzing…"):
        st.markdown(claude_analyst.portfolio_analysis(facts))

render_footer(st)
