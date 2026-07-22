"""Portfolio — PA-style component tabs: Overview, Performance,
Attribution, Exposures, Risk, AI. Analytics in lib/pa_engine.py
(architecture recycled from FactSet's enterprise-sdk PA Engine v3)."""
import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from lib import claude_analyst, pa_engine
from lib.charts import GREEN, RED, render_gauge
from lib.config import apply_base_style, render_footer, render_sidebar
from lib.logos import logo_img_html
from lib.market_data import (get_history_bulk, get_quotes_bulk,
                             get_stock_fundamentals)
from lib.portfolio import load_portfolio, save_portfolio
from lib.portfolio_analytics import build_portfolio_series
from lib.risk import compute_risk_score

apply_base_style(st)
render_sidebar(st)
from lib.copilot import copilot
copilot("Portfolio")
st.title("Portfolio")
st.markdown('<div class="tt-subtitle">PERFORMANCE · ATTRIBUTION · '
            'EXPOSURES · RISK — BENCHMARKED TO SPY · PA-ENGINE STYLE '
            'ANALYTICS</div>', unsafe_allow_html=True)

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

# ---- Shared data ----
tickers = tuple(h["ticker"] for h in holdings)
quotes = get_quotes_bulk(tickers)
rows = []
for h in holdings:
    tk = h["ticker"]
    q = quotes.get(tk, {})
    price, chg = q.get("price"), q.get("change_pct")
    value = price * h["shares"] if price else None
    rows.append({"tk": tk, "shares": h["shares"], "cb": h["cost_basis"],
                 "price": price, "chg": chg, "value": value,
                 "cost": h["cost_basis"] * h["shares"]})
df = pd.DataFrame(rows)
valid = df.dropna(subset=["value"])
total_value = valid["value"].sum()
total_cost = df["cost"].sum()
day_pnl = sum((r["value"] or 0) * (r["chg"] or 0) / 100
              / (1 + (r["chg"] or 0) / 100) for _, r in valid.iterrows())
weights = {r["tk"]: r["value"] / total_value
           for _, r in valid.iterrows()} if total_value else {}
infos = {tk: get_stock_fundamentals(tk) for tk in weights}


def sector_of(tk):
    info = infos.get(tk) or {}
    return info.get("sector") or ("ETF/Fund" if (info.get("quoteType")
                                                 == "ETF") else "Other")


k1, k2, k3, k4 = st.columns(4)
k1.metric("Value", f"${total_value:,.0f}")
k2.metric("Cost", f"${total_cost:,.0f}")
ret = (total_value / total_cost - 1) * 100 if total_cost else 0
k3.metric("Total P&L", f"${total_value - total_cost:,.0f}", f"{ret:+.1f}%")
k4.metric("Day P&L", f"${day_pnl:,.0f}",
          f"{day_pnl / total_value * 100:+.2f}%" if total_value else None)

h_l, h_r = st.columns([3, 1.2])
with h_r:
    horizon = st.segmented_control("Horizon", ["1Y", "3Y"],
                                   default="1Y", key="pf_h") or "1Y"
hkey = tuple((h["ticker"], h["shares"]) for h in holdings)
series = build_portfolio_series(hkey, horizon)
have_series = bool(series and series["value"] is not None
                   and len(series["value"]) > 20)


def _stat_cards(stats: dict, per_row: int = 5):
    cols = st.columns(per_row)
    for i, (label, val) in enumerate(stats.items()):
        with cols[i % per_row]:
            st.markdown(
                f'<div style="border:1px solid #252c3b;border-left:3px '
                f'solid #f97316;padding:0.4rem 0.6rem;margin-bottom:0.5rem;'
                f'background:#161b26;"><span style="font-family:Consolas,'
                f'monospace;font-size:0.63rem;letter-spacing:0.06em;'
                f'color:#8a93a6;">{label.upper()}</span><br>'
                f'<span style="font-family:Consolas,monospace;'
                f'font-weight:600;font-size:1.02rem;">{val}</span></div>',
                unsafe_allow_html=True)


def _safe(fn):
    try:
        fn()
    except Exception as e:
        st.error("This section hit a temporary data problem.")
        st.caption(f"Detail: {type(e).__name__}: {e}")


t_over, t_perf, t_attr, t_expo, t_risk, t_ai = st.tabs(
    ["Overview", "Performance", "Attribution", "Exposures", "Risk",
     "AI Review"])

# ================= OVERVIEW =================
with t_over:
    def _overview():
        hdr = ('<div style="display:grid;grid-template-columns:26px 4em '
               'minmax(0,1fr) 5em 5.5em 5em 6.5em 6.5em 5.5em;gap:8px;'
               'padding:4px 0;font-family:Consolas,monospace;'
               'font-size:0.65rem;letter-spacing:0.07em;color:#8a93a6;'
               'border-bottom:2px solid #252c3b;"><span></span>'
               '<span>TICKER</span><span>NAME</span>'
               '<span style="text-align:right;">WEIGHT</span>'
               '<span style="text-align:right;">PRICE</span>'
               '<span style="text-align:right;">DAY</span>'
               '<span style="text-align:right;">VALUE</span>'
               '<span style="text-align:right;">P&L</span>'
               '<span style="text-align:right;">P&L %</span></div>')
        st.markdown(hdr, unsafe_allow_html=True)
        for _, r in valid.sort_values("value", ascending=False).iterrows():
            info = infos.get(r["tk"]) or {}
            name = (info.get("shortName") or info.get("longName") or "")[:26]
            w = weights.get(r["tk"], 0)
            pnl = r["value"] - r["cost"]
            pnl_pct = (r["value"] / r["cost"] - 1) * 100 if r["cost"] else 0
            dc = GREEN if (r["chg"] or 0) >= 0 else RED
            pc = GREEN if pnl >= 0 else RED
            st.markdown(
                f'<div style="display:grid;grid-template-columns:26px 4em '
                f'minmax(0,1fr) 5em 5.5em 5em 6.5em 6.5em 5.5em;gap:8px;'
                f'align-items:center;padding:6px 0;border-bottom:1px solid '
                f'#1a2029;">{logo_img_html(r["tk"], 22)}'
                f'<b style="font-size:0.85rem;">{r["tk"]}</b>'
                f'<span style="color:#8a93a6;font-size:12px;white-space:'
                f'nowrap;overflow:hidden;text-overflow:ellipsis;">{name}'
                f'</span><span style="text-align:right;font-family:Consolas'
                f',monospace;font-size:0.85rem;">{w:.1%}</span>'
                f'<span style="text-align:right;font-family:Consolas,'
                f'monospace;font-size:0.85rem;">{r["price"]:,.2f}</span>'
                f'<span style="text-align:right;font-family:Consolas,'
                f'monospace;font-size:0.8rem;color:{dc};">'
                f'{(r["chg"] or 0):+.2f}%</span>'
                f'<span style="text-align:right;font-family:Consolas,'
                f'monospace;font-size:0.85rem;">${r["value"]:,.0f}</span>'
                f'<span style="text-align:right;font-family:Consolas,'
                f'monospace;font-size:0.85rem;color:{pc};">${pnl:,.0f}'
                f'</span><span style="text-align:right;font-family:Consolas'
                f',monospace;font-size:0.85rem;color:{pc};">'
                f'{pnl_pct:+.1f}%</span></div>', unsafe_allow_html=True)
        top = valid.sort_values("value", ascending=False)["value"]
        st.caption(f"{len(valid)} positions · top-3 concentration "
                   f"{top.head(3).sum() / total_value:.0%}")
    _safe(_overview)

# ================= PERFORMANCE =================
with t_perf:
    def _perf():
        if not have_series:
            st.caption("Performance history builds once holdings have "
                       "price data.")
            return
        v, b = series["value"], series["bench"]
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=v.index, y=v / v.iloc[0] * 100,
                                 name="Portfolio", mode="lines",
                                 line=dict(color="#f97316", width=2.2)))
        if b is not None and b.dropna().shape[0] > 5:
            bb = b.dropna()
            fig.add_trace(go.Scatter(x=bb.index, y=bb / bb.iloc[0] * 100,
                                     name="SPY", mode="lines",
                                     line=dict(color="#8a93a6", width=1.6,
                                               dash="dot")))
        fig.add_hline(y=100, line_color="#313a4d", line_width=1,
                      line_dash="dot")
        fig.update_layout(template="plotly_dark", height=360,
                          margin=dict(l=10, r=10, t=10, b=10),
                          legend=dict(orientation="h"),
                          yaxis_title="Indexed to 100",
                          paper_bgcolor="rgba(0,0,0,0)")
        st.plotly_chart(fig, use_container_width=True)

        _stat_cards(pa_engine.extended_stats(v, b))

        st.subheader("Drawdown")
        dd = pa_engine.drawdown_series(v)
        fig = go.Figure(go.Scatter(x=dd.index, y=dd, fill="tozeroy",
                                   mode="lines",
                                   line=dict(color=RED, width=1.4),
                                   fillcolor="rgba(185,28,28,0.12)"))
        fig.update_layout(template="plotly_dark", height=220,
                          margin=dict(l=10, r=10, t=10, b=10),
                          yaxis_ticksuffix="%",
                          paper_bgcolor="rgba(0,0,0,0)")
        st.plotly_chart(fig, use_container_width=True)

        st.subheader("Monthly returns")
        pm = pa_engine.monthly_returns(v)
        bm = pa_engine.monthly_returns(b.dropna()) if b is not None else None
        tbl = pd.DataFrame({"Portfolio": pm})
        if bm is not None:
            tbl["SPY"] = bm
            tbl["Active"] = tbl["Portfolio"] - tbl["SPY"]
        tbl.index = tbl.index.strftime("%b %Y")
        st.dataframe(tbl.style.format("{:+.1%}", na_rep="—").map(
            lambda x: f"color:{GREEN if x >= 0 else RED}"
            if isinstance(x, float) else ""), use_container_width=True)
    _safe(_perf)

# ================= ATTRIBUTION =================
with t_attr:
    def _attr():
        if not have_series:
            st.caption("Attribution builds once holdings have price data.")
            return
        rets = series["returns"]
        st.subheader("Contribution to return")
        st.caption(f"Position weight x {horizon} total return — "
                   "buy-and-hold approximation at current weights.")
        contrib = pa_engine.contribution_to_return(rets, weights)
        if not contrib.empty:
            c = contrib.sort_values(ascending=True)
            fig = go.Figure(go.Bar(
                x=c.values * 100, y=c.index, orientation="h",
                marker_color=[GREEN if x >= 0 else RED for x in c.values],
                text=[f"{x:+.1%}" for x in c.values],
                textposition="outside"))
            fig.update_layout(template="plotly_dark",
                              height=max(240, 34 * len(c)),
                              margin=dict(l=10, r=70, t=10, b=10),
                              xaxis_ticksuffix="%",
                              paper_bgcolor="rgba(0,0,0,0)")
            st.plotly_chart(fig, use_container_width=True)

        st.subheader("Brinson sector attribution vs SPY")
        st.caption("Allocation = over/underweight x sector-vs-market "
                   "return. Selection = your picks vs the sector ETF. "
                   "Sector benchmarks: SPDR ETFs; weights: SPY fund data.")
        sect_hist = get_history_bulk(
            tuple(pa_engine.SECTOR_ETF.values()) + ("SPY",), horizon)

        def tot(dfh):
            c = dfh["Close"].dropna()
            return c.iloc[-1] / c.iloc[0] - 1 if len(c) > 5 else None
        sector_rets = {sec: tot(sect_hist[etf])
                       for sec, etf in pa_engine.SECTOR_ETF.items()
                       if etf in sect_hist}
        bench_total = tot(sect_hist["SPY"]) if "SPY" in sect_hist else 0.0

        port_sectors, port_sec_rets, sec_num = {}, {}, {}
        for tk, w in weights.items():
            sec = sector_of(tk)
            port_sectors[sec] = port_sectors.get(sec, 0) + w
            r = rets[tk].dropna() if tk in rets else pd.Series(dtype=float)
            if len(r) > 5:
                tr = (1 + r).prod() - 1
                sec_num[sec] = sec_num.get(sec, 0) + w * tr
        for sec, wsum in port_sectors.items():
            if sec in sec_num and wsum > 0:
                port_sec_rets[sec] = sec_num[sec] / wsum

        br = pa_engine.brinson_attribution(
            port_sectors, sector_rets, pa_engine.spy_sector_weights(),
            bench_total or 0.0, port_sec_rets)
        if not br.empty:
            st.dataframe(br.style.format(
                {"Port wt": "{:.1%}", "Bench wt": "{:.1%}",
                 "Port ret": "{:+.1%}", "Bench ret": "{:+.1%}",
                 "Allocation": "{:+.2%}", "Selection": "{:+.2%}",
                 "Total": "{:+.2%}"}, na_rep="—"),
                hide_index=True, use_container_width=True)
            eff = br.dropna(subset=["Total"]).set_index("Sector")
            if not eff.empty:
                fig = go.Figure()
                fig.add_trace(go.Bar(name="Allocation", x=eff.index,
                                     y=eff["Allocation"] * 100,
                                     marker_color="#f97316"))
                fig.add_trace(go.Bar(name="Selection", x=eff.index,
                                     y=eff["Selection"] * 100,
                                     marker_color="#8a93a6"))
                fig.update_layout(template="plotly_dark", barmode="group",
                                  height=300, yaxis_ticksuffix="%",
                                  margin=dict(l=10, r=10, t=10, b=10),
                                  legend=dict(orientation="h"),
                                  paper_bgcolor="rgba(0,0,0,0)")
                st.plotly_chart(fig, use_container_width=True)
            tot_active = br["Total"].sum()
            st.caption(f"Estimated active return vs SPY over {horizon}: "
                       f"{tot_active:+.1%} (allocation "
                       f"{br['Allocation'].sum():+.1%}, selection "
                       f"{br['Selection'].sum():+.1%})")
    _safe(_attr)

# ================= EXPOSURES =================
with t_expo:
    def _expo():
        e_l, e_r = st.columns(2)
        with e_l:
            st.subheader("Sector weights vs SPY")
            port_sec = {}
            for tk, w in weights.items():
                sec = sector_of(tk)
                port_sec[sec] = port_sec.get(sec, 0) + w
            bench = pa_engine.spy_sector_weights()
            secs = sorted(set(port_sec) | set(bench),
                          key=lambda s: -port_sec.get(s, 0))
            fig = go.Figure()
            fig.add_trace(go.Bar(name="Portfolio", y=secs,
                                 x=[port_sec.get(s, 0) * 100 for s in secs],
                                 orientation="h", marker_color="#f97316"))
            fig.add_trace(go.Bar(name="SPY", y=secs,
                                 x=[bench.get(s, 0) * 100 for s in secs],
                                 orientation="h", marker_color="#313a4d"))
            fig.update_layout(template="plotly_dark", barmode="group",
                              height=max(300, 34 * len(secs)),
                              xaxis_ticksuffix="%",
                              margin=dict(l=10, r=10, t=10, b=10),
                              legend=dict(orientation="h"),
                              paper_bgcolor="rgba(0,0,0,0)")
            st.plotly_chart(fig, use_container_width=True)
        with e_r:
            st.subheader("Style profile")
            for label, val in pa_engine.style_snapshot(infos, weights):
                st.markdown(
                    f'<div style="display:flex;justify-content:'
                    f'space-between;padding:6px 0;border-bottom:1px solid '
                    f'#1a2029;"><span style="color:#8a93a6;font-size:'
                    f'0.85rem;">{label}</span><b style="font-family:'
                    f'Consolas,monospace;">{val}</b></div>',
                    unsafe_allow_html=True)
            st.subheader("Market cap")
            for label, w in sorted(pa_engine.cap_buckets(
                    infos, weights).items(), key=lambda x: -x[1]):
                st.markdown(f"- {label}: **{w:.0%}**")
            st.subheader("Geography")
            for label, w in sorted(pa_engine.geo_buckets(
                    infos, weights).items(), key=lambda x: -x[1])[:8]:
                st.markdown(f"- {label}: **{w:.0%}**")
    _safe(_expo)

# ================= RISK =================
with t_risk:
    def _risk():
        if not have_series:
            st.caption("Risk analytics build once holdings have price "
                       "data.")
            return
        v = series["value"]
        rets_p = v.pct_change().dropna()
        var95 = rets_p.quantile(0.05)
        cvar = rets_p[rets_p <= var95].mean()
        _stat_cards({
            "VaR 95% (1-day)": f"{var95:.2%}",
            "VaR 95% ($)": f"${abs(var95) * total_value:,.0f}",
            "CVaR 95% (1-day)": f"{cvar:.2%}",
            "CVaR 95% ($)": f"${abs(cvar) * total_value:,.0f}",
        }, per_row=4)

        g, t = st.columns([1, 1])
        risk = compute_risk_score(v, list(weights.values()))
        with g:
            st.plotly_chart(render_gauge(
                risk["score"], f"Risk: {risk['label']}",
                "Volatility, drawdown, concentration", bands="risk"),
                use_container_width=True)
        with t:
            st.markdown(f"- Annualized volatility: "
                        f"**{risk['volatility']:.1%}**")
            st.markdown(f"- Max drawdown ({horizon}): "
                        f"**{risk['max_drawdown']:.1%}**")
            st.markdown(f"- Concentration: **{risk['concentration']:.0%}**")

        st.subheader("Risk decomposition")
        st.caption("Marginal (MCTR) and total (CTR) contribution of each "
                   "position to portfolio volatility.")
        rd = pa_engine.risk_decomposition(series["returns"], weights)
        if not rd.empty:
            st.dataframe(rd.style.format(
                {"Weight": "{:.1%}", "Stand-alone vol": "{:.1%}",
                 "MCTR": "{:.3f}", "CTR": "{:.3f}", "% of risk": "{:.0%}"}),
                use_container_width=True)

        st.subheader("Holdings correlation")
        r = series["returns"]
        if r is not None and r.shape[1] >= 2:
            corr = r.corr().round(2)
            fig = go.Figure(go.Heatmap(
                z=corr.values, x=corr.columns, y=corr.index,
                zmin=-1, zmax=1,
                colorscale=[[0, "#ea3943"], [0.5, "#161b26"],
                            [1, "#16c784"]],
                text=corr.values, texttemplate="%{text}"))
            fig.update_layout(template="plotly_dark", height=380,
                              margin=dict(l=10, r=10, t=10, b=10),
                              paper_bgcolor="rgba(0,0,0,0)")
            st.plotly_chart(fig, use_container_width=True)
    _safe(_risk)

# ================= AI =================
with t_ai:
    def _ai():
        if claude_analyst.key_missing():
            st.info("Add your ANTHROPIC_API_KEY in the app Secrets to "
                    "enable AI analysis.")
            return
        if st.button("Generate review", key="pf_ai"):
            facts = "; ".join(
                f"{tk}: {w:.0%} weight, sector {sector_of(tk)}"
                for tk, w in weights.items())
            facts += f". Total ${total_value:,.0f}."
            if have_series:
                stats = pa_engine.extended_stats(series["value"],
                                                 series["bench"])
                facts += " Stats: " + "; ".join(
                    f"{k} {vv}" for k, vv in stats.items())
            with st.spinner("Analyzing…"):
                st.markdown(claude_analyst.portfolio_analysis(facts))
    _safe(_ai)

render_footer(st)
