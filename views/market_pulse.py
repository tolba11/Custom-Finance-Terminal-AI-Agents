"""Market Pulse — indices grid, S&P chart, sector heatmap, movers, headlines."""
import pandas as pd
import streamlit as st
import yfinance as yf

from lib.charts import CHART_VIEWS, render_price_chart, render_sparkline
from lib.config import apply_base_style, render_footer, render_sidebar
from lib.logos import logo_img_html
from lib.market_data import (INDEX_TICKERS, REGION_BENCHMARK,
                             REGION_TICKERS, SECTOR_ETFS, PERIOD_MAP,
                             get_history, get_history_bulk,
                             get_history_fresh, get_quotes_bulk)
from lib.news import market_news, time_ago

apply_base_style(st)
render_sidebar(st)
t_l, t_r = st.columns([3, 1.6])
with t_l:
    st.title("Market Pulse")
with t_r:
    st.markdown("<div style='height:0.9rem'></div>", unsafe_allow_html=True)
    region = st.segmented_control("Region", list(REGION_TICKERS.keys()),
                                  default="U.S.",
                                  key="mp_region") or "U.S."

period = st.segmented_control("Period", list(PERIOD_MAP.keys()),
                              default="1D", key="mp_period") or "1D"

# ---- Index / asset cards with sparklines ----
region_map = REGION_TICKERS[region]
tickers = tuple(region_map.keys())
quotes = get_quotes_bulk(tickers)
hist = get_history_bulk(tickers, period)

rows = [list(region_map.items())[:5], list(region_map.items())[5:]]
for row in rows:
    cols = st.columns(len(row))
    for col, (tk, name) in zip(cols, row):
        q = quotes.get(tk, {})
        with col, st.container(border=True):
            price, pct = q.get("price"), q.get("change_pct")
            st.metric(name, f"{price:,.2f}" if price else "—",
                      f"{pct:+.2f}%" if pct is not None else None)
            df = hist.get(tk)
            if df is not None and not df.empty:
                closes = df["Close"]
                baseline = q.get("prev_close") if period == "1D" else None
                if period == "1D" and baseline:
                    # prepend yesterday's close as baseline bar
                    first_ts = closes.index[0] - pd.Timedelta(minutes=5)
                    closes = pd.concat(
                        [pd.Series([baseline], index=[first_ts]), closes])
                st.plotly_chart(
                    render_sparkline(closes, baseline=baseline),
                    use_container_width=True,
                    config={"displayModeBar": False},
                    key=f"spark_{tk}")

st.divider()

# ---- Big S&P 500 chart ----
bench_tk, bench_name = REGION_BENCHMARK[region]
st.subheader(f"{bench_name} ({bench_tk})")
view = st.segmented_control("View", CHART_VIEWS, default="Performance",
                            key="mp_view") or "Performance"
spx, spx_fresh = get_history_fresh(bench_tk, period)
spx_baseline = (quotes.get(bench_tk, {}).get("prev_close")
                if period == "1D" else None)
st.plotly_chart(render_price_chart(spx, view=view,
                                   baseline_price=spx_baseline),
                use_container_width=True)
if spx_fresh:
    st.markdown(f'<div style="font-family:Consolas,monospace;'
                f'font-size:0.68rem;letter-spacing:0.08em;color:#a1a1aa;">'
                f'{spx_fresh} · REFRESHES EVERY 15 MIN</div>',
                unsafe_allow_html=True)

st.divider()

# ---- Global markets: commodities, FX, rates & bonds ----
st.subheader("Commodities · FX · Rates")
from lib.markets_strip import render_markets_strip
render_markets_strip()

st.divider()


# ---- U.S.-only sections: sector heatmap + movers ----
@st.cache_data(ttl=300, show_spinner=False)
def get_movers():
    out = {}
    for key, scrid in (("gainers", "day_gainers"), ("losers", "day_losers"),
                       ("active", "most_actives")):
        try:
            df = yf.screen(scrid, count=6).get("quotes", [])
            out[key] = df
        except Exception:
            out[key] = []
    return out


def render_mover_rows(items):
    for it in items[:6]:
        sym = it.get("symbol", "")
        name = it.get("shortName") or it.get("longName") or ""
        price = it.get("regularMarketPrice")
        pct = it.get("regularMarketChangePercent")
        color = "#047857" if (pct or 0) >= 0 else "#b91c1c"
        if price is not None and pct is not None:
            st.markdown(
                f'<div style="display:grid;'
                f'grid-template-columns:26px 3.4em minmax(0,1fr) 4.6em 4.6em;'
                f'gap:8px;align-items:center;padding:6px 0;'
                f'border-bottom:1px solid #f4f4f5;">'
                f'{logo_img_html(sym, 22)}'
                f'<b style="font-size:0.85rem;">{sym}</b>'
                f'<span style="color:#71717a;font-size:12px;'
                f'white-space:nowrap;overflow:hidden;'
                f'text-overflow:ellipsis;">{name}</span>'
                f'<span style="text-align:right;font-family:Consolas,'
                f'monospace;font-size:0.85rem;">{price:,.2f}</span>'
                f'<span style="color:{color};text-align:right;'
                f'font-family:Consolas,monospace;font-size:0.85rem;">'
                f'{pct:+.2f}%</span></div>',
                unsafe_allow_html=True)
        else:
            st.markdown(f'<div style="padding:6px 0;">'
                        f'{logo_img_html(sym, 22)} <b>{sym}</b></div>',
                        unsafe_allow_html=True)


if region == "U.S.":
    st.subheader("Sector performance")
    sector_hist = get_history_bulk(tuple(SECTOR_ETFS.keys()), period)
    sector_quotes = get_quotes_bulk(tuple(SECTOR_ETFS.keys()))
    perf = {}
    for tk, name in SECTOR_ETFS.items():
        df = sector_hist.get(tk)
        if df is None or df.empty:
            continue
        if period == "1D":
            base = sector_quotes.get(tk, {}).get("prev_close") or float(
                df["Close"].iloc[0])
        else:
            base = float(df["Close"].iloc[0])
        perf[name] = (float(df["Close"].iloc[-1]) / base - 1) * 100
    if perf:
        import plotly.graph_objects as go
        s = pd.Series(perf).sort_values()
        fig = go.Figure(go.Bar(
            x=s.values, y=s.index, orientation="h",
            marker_color=["#047857" if v >= 0 else "#b91c1c"
                          for v in s.values],
            text=[f"{v:+.2f}%" for v in s.values],
            textposition="outside",
        ))
        fig.update_layout(template="plotly_white", height=420,
                          margin=dict(l=10, r=60, t=10, b=10),
                          xaxis_ticksuffix="%",
                          paper_bgcolor="rgba(0,0,0,0)")
        st.plotly_chart(fig, use_container_width=True)

    st.divider()

    movers = get_movers()
    c1, c2, c3 = st.columns(3)
    with c1:
        st.subheader("Top gainers")
        render_mover_rows(movers["gainers"])
    with c2:
        st.subheader("Top losers")
        render_mover_rows(movers["losers"])
    with c3:
        st.subheader("Most active")
        render_mover_rows(movers["active"])
else:
    st.caption("Sector heatmap and top movers cover U.S. markets — "
               "switch the region to U.S. to view them.")

st.divider()

# ---- Headlines ----
st.subheader("Top headlines")
for item in market_news(limit=3):
    with st.container(border=True):
        st.markdown(f"**{item['title']}**")
        meta = " · ".join(x for x in (item["publisher"],
                                      time_ago(item["published"])) if x)
        if meta:
            st.caption(meta)
        if item["summary"]:
            summary = item["summary"]
            st.write(summary[:220] + ("…" if len(summary) > 220 else ""))
        if item["link"]:
            st.markdown(f"[Read more]({item['link']})")

render_footer(st)
