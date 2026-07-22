"""Fundamental Analysis — statements, SEC filings, earnings & transcripts."""
import pandas as pd
import plotly.graph_objects as go
import streamlit as st
import yfinance as yf

from lib import alphavantage as av
from lib.config import apply_base_style, render_footer, render_sidebar
from lib.edgar import FORM_TYPES, get_filings
from lib.logos import logo_img_html
from lib.market_data import get_stock_fundamentals
from lib.symbol_search import symbol_search

apply_base_style(st)
render_sidebar(st)
st.title("Financial Statements")
st.markdown('<div class="tt-subtitle">STATEMENTS · SEC FILINGS · '
            'EARNINGS CALLS — YAHOO FINANCE + ALPHA VANTAGE + EDGAR</div>',
            unsafe_allow_html=True)

c1, c2 = st.columns([1.2, 2])
with c1:
    ticker = symbol_search("Company or ticker", "fa", "AAPL")

info = get_stock_fundamentals(ticker)
name = info.get("longName") or info.get("shortName") or ticker
with c2:
    st.markdown(
        f'<div style="display:flex;align-items:center;gap:12px;'
        f'padding-top:1.6rem;">'
        f'{logo_img_html(ticker, 44, domain=info.get("website"))}'
        f'<div><b style="font-size:1.05rem;">{name}</b> '
        f'<span style="color:#8a93a6;">{ticker}</span><br>'
        f'<span style="color:#8a93a6;font-size:0.8rem;">'
        f'{" · ".join(x for x in (info.get("sector"), info.get("industry")) if x)}'
        f'</span></div></div>', unsafe_allow_html=True)

k1, k2, k3, k4 = st.columns(4)
rev = info.get("totalRevenue")
k1.metric("Revenue (TTM)", f"${rev/1e9:,.1f}B" if rev else "—")
ni = info.get("netIncomeToCommon")
k2.metric("Net Income (TTM)", f"${ni/1e9:,.1f}B" if ni else "—")
fcf = info.get("freeCashflow")
k3.metric("Free Cash Flow", f"${fcf/1e9:,.1f}B" if fcf else "—")
om = info.get("operatingMargins")
k4.metric("Operating Margin", f"{om:.1%}" if om else "—")

section = st.segmented_control(
    "Section", ["Income Statement", "Balance Sheet", "Cash Flow",
                "SEC Filings", "Earnings & Transcripts"],
    default="Income Statement", key="fa_section") or "Income Statement"


@st.cache_data(ttl=900, show_spinner=False, max_entries=48)
def _statement(tk: str, which: str, freq: str) -> pd.DataFrame:
    t = yf.Ticker(tk)
    attr = {"income": "income_stmt", "balance": "balance_sheet",
            "cash": "cashflow"}[which]
    if freq == "Quarterly":
        attr = "quarterly_" + attr
    try:
        df = getattr(t, attr)
        return df if df is not None else pd.DataFrame()
    except Exception:
        return pd.DataFrame()


def render_statement(which: str, headline_rows: list):
    freq = st.segmented_control("Period", ["Annual", "Quarterly"],
                                default="Annual",
                                key=f"fa_freq_{which}") or "Annual"
    df = _statement(ticker, which, freq)
    if df.empty:
        st.warning("No statement data available for this symbol — "
                   "coverage is best for US-listed companies.")
        return
    # trend chart for the headline metric
    for hr in headline_rows:
        if hr in df.index:
            series = df.loc[hr].dropna().sort_index()
            fig = go.Figure(go.Bar(
                x=[str(c)[:10] for c in series.index],
                y=series.values / 1e9,
                marker_color=["#16c784" if v >= 0 else "#ea3943"
                              for v in series.values],
                text=[f"{v/1e9:,.1f}" for v in series.values],
                textposition="outside"))
            fig.update_layout(template="plotly_dark", height=240,
                              margin=dict(l=10, r=10, t=30, b=10),
                              yaxis_title="$B", title=hr,
                              paper_bgcolor="rgba(0,0,0,0)")
            st.plotly_chart(fig, use_container_width=True)
            break
    disp = df.copy()
    disp.columns = [str(c)[:10] for c in disp.columns]
    disp = (disp / 1e6).round(1)
    st.caption("All figures in $ millions. Source: Yahoo Finance.")
    st.dataframe(disp, use_container_width=True, height=560)
    st.download_button(
        "Download CSV",
        disp.to_csv().encode(),
        file_name=f"{ticker}_{which}_{freq.lower()}.csv",
        mime="text/csv", key=f"fa_dl_{which}")


if section == "Income Statement":
    render_statement("income", ["Total Revenue", "Net Income"])
elif section == "Balance Sheet":
    render_statement("balance", ["Total Assets"])
elif section == "Cash Flow":
    render_statement("cash", ["Free Cash Flow", "Operating Cash Flow"])

elif section == "SEC Filings":
    form = st.segmented_control("Form type", FORM_TYPES, default="10-K",
                                key="fa_form") or "10-K"
    title, filings, err = get_filings(ticker)
    if err and not filings:
        st.warning(f"EDGAR: {err}")
    else:
        shown = [f for f in filings
                 if form == "All" or f["form"] == form][:40]
        st.caption(f"{title or ticker} — {len(shown)} filings shown "
                   f"({form}), newest first. Source: SEC EDGAR.")
        for f in shown:
            st.markdown(
                f'<div style="display:grid;grid-template-columns:6.5em '
                f'7em minmax(0,1fr) 5em;gap:10px;align-items:center;'
                f'padding:7px 0;border-bottom:1px solid #1a2029;">'
                f'<span style="font-family:Consolas,monospace;'
                f'font-weight:600;font-size:0.8rem;">{f["form"]}</span>'
                f'<span style="font-family:Consolas,monospace;'
                f'font-size:0.8rem;color:#8a93a6;">{f["date"]}</span>'
                f'<span style="font-size:0.85rem;color:#b7c0d0;'
                f'white-space:nowrap;overflow:hidden;text-overflow:'
                f'ellipsis;">{f["desc"]}</span>'
                f'<a href="{f["url"]}" target="_blank" '
                f'style="color:#f97316;font-family:Consolas,monospace;'
                f'font-size:0.78rem;font-weight:600;">OPEN</a></div>',
                unsafe_allow_html=True)

elif section == "Earnings & Transcripts":
    if av.key_missing():
        st.info("Add your ALPHA_VANTAGE_API_KEY in the app Secrets to "
                "enable earnings history and call transcripts.")
    else:
        earn, err = av_earn = av.av_earnings(ticker)
        if err:
            st.warning(f"Alpha Vantage: {err}")
        q = (earn or {}).get("quarterlyEarnings", [])[:12]
        if q:
            st.markdown("**EPS — actual vs estimate (last 12 quarters)**")
            qs = list(reversed(q))
            fig = go.Figure()
            fig.add_trace(go.Bar(
                name="Estimate",
                x=[r.get("fiscalDateEnding", "")[:7] for r in qs],
                y=[float(r["estimatedEPS"]) if r.get("estimatedEPS")
                   not in (None, "None") else None for r in qs],
                marker_color="#313a4d"))
            fig.add_trace(go.Bar(
                name="Actual",
                x=[r.get("fiscalDateEnding", "")[:7] for r in qs],
                y=[float(r["reportedEPS"]) if r.get("reportedEPS")
                   not in (None, "None") else None for r in qs],
                marker_color=["#16c784" if (r.get("surprise") or "0")
                              not in ("None", None) and
                              float(r.get("surprise") or 0) >= 0
                              else "#ea3943" for r in qs]))
            fig.update_layout(barmode="group", template="plotly_dark",
                              height=300,
                              margin=dict(l=10, r=10, t=10, b=10),
                              legend=dict(orientation="h"),
                              paper_bgcolor="rgba(0,0,0,0)")
            st.plotly_chart(fig, use_container_width=True)

            st.divider()
            st.markdown("**Earnings call transcript**")
            quarters = []
            for r in q:
                d = r.get("fiscalDateEnding", "")
                if len(d) >= 7:
                    y, mth = int(d[:4]), int(d[5:7])
                    quarters.append(f"{y}Q{(mth - 1) // 3 + 1}")
            sel = st.selectbox("Quarter", quarters, key="fa_quarter")
            if st.button("Load transcript", key="fa_tr_btn"):
                data, terr = av.av_transcript(ticker, sel)
                tr = (data or {}).get("transcript", [])
                if terr:
                    st.warning(f"Alpha Vantage: {terr}")
                elif not tr:
                    st.info("No transcript available for this quarter.")
                else:
                    st.session_state["fa_transcript"] = (sel, tr)
            stored = st.session_state.get("fa_transcript")
            if stored and stored[0] == sel:
                tq = st.text_input("Search within transcript",
                                   key="fa_tr_q").strip().lower()
                shown = [s for s in stored[1]
                         if not tq or tq in (s.get("content") or "").lower()]
                st.caption(f"{len(shown)} passages"
                           + (f" matching '{tq}'" if tq else ""))
                for s in shown:
                    st.markdown(
                        f'<div style="padding:8px 0;border-bottom:1px '
                        f'solid #1a2029;"><span style="font-family:'
                        f'Consolas,monospace;font-size:0.72rem;'
                        f'letter-spacing:0.06em;color:#f97316;'
                        f'font-weight:600;">'
                        f'{(s.get("speaker") or "?").upper()} '
                        f'<span style="color:#5c6575;">'
                        f'{s.get("title") or ""}</span></span>'
                        f'<div style="font-size:0.88rem;color:#b7c0d0;'
                        f'padding-top:2px;">{s.get("content") or ""}'
                        f'</div></div>', unsafe_allow_html=True)
        else:
            st.info("No earnings history returned for this symbol.")
        st.caption("Transcripts and EPS history via Alpha Vantage — the "
                   "free tier allows ~25 requests/day, so results are "
                   "cached aggressively.")

render_footer(st)
