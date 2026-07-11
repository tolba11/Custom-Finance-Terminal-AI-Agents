"""ETF Analyzer — chart, returns, risk gauge, sectors, holdings, peers."""
import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from lib.charts import CHART_VIEWS, render_gauge, render_price_chart
from lib.config import apply_base_style, render_footer, render_sidebar
from lib.etf_peers import find_peers
from lib.logos import logo_img_html
from lib.market_data import (PERIOD_MAP, get_etf_details, get_history,
                             get_quote, get_stock_fundamentals)
from lib.risk import compute_risk_score
from lib.symbol_search import symbol_search

apply_base_style(st)
render_sidebar(st)
st.title("ETF Analyzer")

c1, c2 = st.columns([1, 3])
with c1:
    ticker = symbol_search("ETF ticker or fund name", "etf", "SPY")
with c2:
    period = st.segmented_control("Period", list(PERIOD_MAP.keys()),
                                  default="1Y", key="etf_period") or "1Y"

if not ticker:
    st.stop()

details = get_etf_details(ticker)
info = details["info"]
quote = get_quote(ticker)
df = get_history(ticker, period)

if df.empty and not info:
    st.warning(f"No data found for **{ticker}**.")
    render_footer(st)
    st.stop()

name = info.get("longName") or info.get("shortName") or ticker
st.markdown(
    f'<div style="display:flex;align-items:center;gap:14px;">'
    f'{logo_img_html(ticker, 56)}<div><h2 style="margin:0;">{name} '
    f'<span style="color:#71717a;font-size:0.7em;">{ticker}</span></h2>'
    f'</div></div>', unsafe_allow_html=True)

m1, m2, m3, m4 = st.columns(4)
price, pct = quote.get("price"), quote.get("change_pct")
m1.metric("Price", f"${price:,.2f}" if price else "—",
          f"{pct:+.2f}%" if pct is not None else None)
er = info.get("netExpenseRatio") or info.get("annualReportExpenseRatio")
m2.metric("Expense ratio", f"{er:.2f}%" if er is not None else "—")
aum = info.get("totalAssets")
m3.metric("AUM", f"${aum/1e9:,.1f}B" if aum else "—")
y = info.get("yield") or info.get("dividendYield")
m4.metric("Yield", f"{y:.2%}" if y and y < 1 else
          (f"{y:.2f}%" if y else "—"))

view = st.segmented_control("View", CHART_VIEWS, default="Performance",
                            key="etf_view") or "Performance"
baseline = quote.get("prev_close") if period == "1D" else None
st.plotly_chart(render_price_chart(df, view=view, baseline_price=baseline),
                use_container_width=True)

# ---- Returns table + risk gauge ----
st.divider()
rc, gc = st.columns([1, 1])
with rc:
    st.subheader("Returns")
    rows = []
    ytd = get_history(ticker, "YTD")
    if not ytd.empty:
        rows.append(("YTD", (ytd["Close"].iloc[-1] / ytd["Close"].iloc[0]
                             - 1) * 100))
    for label, yrs in (("3Y avg", 3), ("5Y avg", 5)):
        h = get_history(ticker, f"{yrs}Y")
        if not h.empty and len(h) > 10:
            total = h["Close"].iloc[-1] / h["Close"].iloc[0]
            rows.append((label, (total ** (1 / yrs) - 1) * 100))
    b3 = info.get("beta3Year") or info.get("beta")
    tbl = pd.DataFrame(
        [(lbl, f"{v:+.2f}%") for lbl, v in rows]
        + ([("3Y beta", f"{b3:.2f}")] if b3 else []),
        columns=["Metric", "Value"])
    st.dataframe(tbl, hide_index=True, use_container_width=True)

with gc:
    st.subheader("Risk profile")
    h3 = get_history(ticker, "3Y")
    weights = None
    holdings = details.get("holdings")
    if holdings is not None and "Holding Percent" in holdings.columns:
        weights = list(holdings["Holding Percent"].dropna())
    risk = compute_risk_score(h3["Close"] if not h3.empty else pd.Series(),
                              weights)
    st.plotly_chart(render_gauge(risk["score"], f"Risk: {risk['label']}",
                                 "Volatility, drawdown, concentration",
                                 bands="risk"),
                    use_container_width=True)
    st.caption(f"3Y annualized volatility {risk['volatility']:.1%} · "
               f"max drawdown {risk['max_drawdown']:.1%}")

# ---- Sector breakdown ----
sectors = details.get("sectors")
if sectors:
    st.divider()
    st.subheader("Sector breakdown")
    s = pd.Series(sectors).sort_values() * 100
    s.index = [i.replace("_", " ").title() for i in s.index]
    fig = go.Figure(go.Bar(x=s.values, y=s.index, orientation="h",
                           marker_color="#38bdf8",
                           text=[f"{v:.1f}%" for v in s.values],
                           textposition="outside"))
    fig.update_layout(template="plotly_white", height=380,
                      margin=dict(l=10, r=60, t=10, b=10),
                      xaxis_ticksuffix="%", paper_bgcolor="rgba(0,0,0,0)")
    st.plotly_chart(fig, use_container_width=True)

# ---- Top holdings ----
if holdings is not None and not holdings.empty:
    st.divider()
    st.subheader("Top holdings")
    hcols = st.columns(2)
    hdf = holdings.reset_index()
    for i, (_, d) in enumerate(hdf.iterrows()):
        sym = str(d.get("Symbol") or d.get("index") or "")
        hname = str(d.get("Name") or d.get("Holding Name") or "")[:30]
        if hname.upper().startswith(sym.upper()):
            hname = hname[len(sym):].strip()
        w = d.get("Holding Percent")
        with hcols[i % 2]:
            st.markdown(
                f'<div style="display:flex;align-items:center;gap:8px;'
                f'padding:5px 0;border-bottom:1px solid #e4e4e7;">'
                f'{logo_img_html(sym, 26)}<b>{sym}</b>'
                f'<span style="color:#71717a;font-size:13px;">{hname}</span>'
                f'<span style="margin-left:auto;">'
                f'{w:.2%}</span></div>' if w is not None else
                f'<div style="padding:5px 0;">{sym} {hname}</div>',
                unsafe_allow_html=True)

# ---- Peer comparison ----
peers = find_peers(ticker)
if peers:
    st.divider()
    st.subheader("Peer cost comparison")
    rows = []
    for p in peers:
        pi = get_stock_fundamentals(p)
        per = pi.get("netExpenseRatio")
        if per is None:
            per = pi.get("annualReportExpenseRatio")
        rows.append({
            "Ticker": p,
            "Name": (pi.get("shortName") or "")[:36],
            "Expense ratio (%)": per,
            "AUM ($B)": round(pi.get("totalAssets", 0) / 1e9, 1)
            if pi.get("totalAssets") else None,
        })
    tbl = pd.DataFrame(rows).sort_values("Expense ratio (%)",
                                         na_position="last")
    st.dataframe(tbl, hide_index=True, use_container_width=True)

    my_er = er
    cheapest = tbl.dropna(subset=["Expense ratio (%)"]).iloc[0] \
        if not tbl.dropna(subset=["Expense ratio (%)"]).empty else None
    if (my_er is not None and cheapest is not None
            and cheapest["Ticker"] != ticker
            and cheapest["Expense ratio (%)"] < my_er):
        bps = (my_er - cheapest["Expense ratio (%)"]) * 100
        dollars = (my_er - cheapest["Expense ratio (%)"]) / 100 * 100000
        st.info(f" **{cheapest['Ticker']}** tracks a similar exposure at "
                f"{cheapest['Expense ratio (%)']:.2f}% — about "
                f"**{bps:.0f} bps lower**, or roughly **${dollars:,.0f}/yr "
                f"on a $100K position**.")

render_footer(st)