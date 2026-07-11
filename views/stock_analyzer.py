"""Stock Analyzer — chart, snapshot gauges, key stats, AI analysis."""
import streamlit as st

from lib import claude_analyst
from lib.charts import CHART_VIEWS, render_gauge, render_price_chart
from lib.config import apply_base_style, render_footer, render_sidebar
from lib.logos import logo_img_html
from lib.market_data import (PERIOD_MAP, get_history, get_quote,
                             get_stock_fundamentals)
from lib.news import ticker_news, time_ago
from lib.signals import at_a_glance, fundamental_score, technical_score
from lib.symbol_search import symbol_search

apply_base_style(st)
render_sidebar(st)
st.title("Stock Analyzer")

c1, c2 = st.columns([1, 3])
with c1:
    ticker = symbol_search("Ticker or company", "sa", "AAPL")
with c2:
    period = st.segmented_control("Period", list(PERIOD_MAP.keys()),
                                  default="1Y", key="sa_period") or "1Y"

if not ticker:
    st.stop()

info = get_stock_fundamentals(ticker)
quote = get_quote(ticker)
df = get_history(ticker, period)

if df.empty and not info:
    st.warning(f"No data found for **{ticker}**. Check the symbol.")
    render_footer(st)
    st.stop()

# ---- Header ----
name = info.get("longName") or info.get("shortName") or ticker
sector = " · ".join(x for x in (info.get("sector"),
                                info.get("industry")) if x)
st.markdown(
    f'<div style="display:flex;align-items:center;gap:14px;">'
    f'{logo_img_html(ticker, 64, domain=info.get("website"))}'
    f'<div><h2 style="margin:0;">{name} '
    f'<span style="color:#71717a;font-size:0.7em;">{ticker}</span></h2>'
    f'<span style="color:#71717a;">{sector}</span></div></div>',
    unsafe_allow_html=True)

m1, m2, m3, m4 = st.columns(4)
price, pct = quote.get("price"), quote.get("change_pct")
m1.metric("Price", f"${price:,.2f}" if price else "—",
          f"{pct:+.2f}%" if pct is not None else None)
mc = info.get("marketCap")
m2.metric("Market Cap", f"${mc/1e9:,.1f}B" if mc else "—")
pe = info.get("trailingPE")
m3.metric("Trailing P/E", f"{pe:.1f}" if pe else "—")
beta = info.get("beta")
m4.metric("Beta", f"{beta:.2f}" if beta else "—")

# ---- Chart ----
view = st.segmented_control("View", CHART_VIEWS, default="Performance",
                            key="sa_view") or "Performance"
baseline = quote.get("prev_close") if period == "1D" else None
st.plotly_chart(render_price_chart(df, view=view, baseline_price=baseline,
                                   show_volume=True),
                use_container_width=True)

# ---- Snapshot ----
st.divider()
st.subheader("Snapshot")

tech = technical_score(get_history(ticker, "1Y"))
fund = fundamental_score(info)
chips = at_a_glance(info, tech)

g1, g2, g3 = st.columns(3)
with g1:
    with st.container(border=True):
        st.markdown("**At a glance**")
        for label, value in chips:
            st.markdown(
                f'<div style="display:flex;justify-content:space-between;'
                f'padding:5px 0;border-bottom:1px solid #e4e4e7;">'
                f'<span style="color:#71717a;">{label}</span>'
                f'<b>{value}</b></div>', unsafe_allow_html=True)
with g2:
    st.plotly_chart(render_gauge(tech["score"], "Technical strength",
                                 "Trend, momentum, position vs averages"),
                    use_container_width=True)
    for d in tech["drivers"]:
        st.markdown(f"- {d}")
with g3:
    st.plotly_chart(render_gauge(fund["score"], "Fundamental quality",
                                 "Margins, returns, leverage, growth"),
                    use_container_width=True)
    for d in fund["drivers"]:
        st.markdown(f"- {d}")

# ---- Key statistics ----
st.divider()
st.subheader("Key statistics")


def fmt(v, kind="num"):
    if v is None:
        return "—"
    if kind == "pct":
        return f"{v:.1%}"
    if kind == "big":
        return f"${v/1e9:,.1f}B"
    if kind == "num":
        return f"{v:,.2f}"
    return str(v)


stats = {
    "Valuation": [("Trailing P/E", fmt(info.get("trailingPE"))),
                  ("Forward P/E", fmt(info.get("forwardPE"))),
                  ("Price/Book", fmt(info.get("priceToBook"))),
                  ("PEG", fmt(info.get("trailingPegRatio")))],
    "Profitability": [("Net margin", fmt(info.get("profitMargins"), "pct")),
                      ("Operating margin",
                       fmt(info.get("operatingMargins"), "pct")),
                      ("ROE", fmt(info.get("returnOnEquity"), "pct")),
                      ("ROA", fmt(info.get("returnOnAssets"), "pct"))],
    "Balance sheet": [("Total cash", fmt(info.get("totalCash"), "big")),
                      ("Total debt", fmt(info.get("totalDebt"), "big")),
                      ("Debt/Equity", fmt(info.get("debtToEquity"))),
                      ("Current ratio", fmt(info.get("currentRatio")))],
    "Trading": [("Beta", fmt(info.get("beta"))),
                ("52w high", fmt(info.get("fiftyTwoWeekHigh"))),
                ("52w low", fmt(info.get("fiftyTwoWeekLow"))),
                ("Avg volume", f"{info.get('averageVolume'):,}"
                 if info.get("averageVolume") else "—")],
    "Income": [("Revenue", fmt(info.get("totalRevenue"), "big")),
               ("Revenue growth", fmt(info.get("revenueGrowth"), "pct")),
               ("EPS (ttm)", fmt(info.get("trailingEps"))),
               ("Dividend yield", fmt(info.get("dividendYield"), "pct")
                if info.get("dividendYield") else "—")],
    "Analyst": [("Mean target", fmt(info.get("targetMeanPrice"))),
                ("High target", fmt(info.get("targetHighPrice"))),
                ("Low target", fmt(info.get("targetLowPrice"))),
                ("# of analysts",
                 str(info.get("numberOfAnalystOpinions") or "—"))],
}
cols = st.columns(3)
for i, (group, rows) in enumerate(stats.items()):
    with cols[i % 3], st.container(border=True):
        st.markdown(f"**{group}**")
        for label, value in rows:
            st.markdown(
                f'<div style="display:flex;justify-content:space-between;'
                f'padding:3px 0;"><span style="color:#71717a;">{label}'
                f'</span><span>{value}</span></div>',
                unsafe_allow_html=True)

if info.get("longBusinessSummary"):
    with st.expander("Business summary"):
        st.write(info["longBusinessSummary"])

# ---- AI analysis ----
st.divider()
st.subheader("AI analysis")
tab1, tab2, tab3 = st.tabs(["Constructive vs cautious case",
                            "Deep analysis", "Recent headlines"])
facts = (f"Price ${price}, P/E {info.get('trailingPE')}, "
         f"market cap {info.get('marketCap')}, "
         f"margins {info.get('profitMargins')}, ROE {info.get('returnOnEquity')}, "
         f"revenue growth {info.get('revenueGrowth')}, beta {info.get('beta')}, "
         f"sector {info.get('sector')}, technical score {tech['score']}, "
         f"fundamental score {fund['score']}")

with tab1:
    if claude_analyst.key_missing():
        st.info("Add your ANTHROPIC_API_KEY in the app Secrets to enable AI analysis.")
    elif st.button("Generate", key="bb_btn"):
        with st.spinner("Analyzing…"):
            st.markdown(claude_analyst.bull_bear_case(ticker, facts))
with tab2:
    if claude_analyst.key_missing():
        st.info("Add your ANTHROPIC_API_KEY in the app Secrets to enable AI analysis.")
    elif st.button("Generate", key="da_btn"):
        with st.spinner("Analyzing…"):
            st.markdown(claude_analyst.deep_analysis(ticker, facts))
with tab3:
    from lib import alphavantage as av
    if not av.key_missing():
        s_data, s_err = av.av_news_sentiment(ticker)
        feed = (s_data or {}).get("feed", [])
        if feed:
            scores = []
            for a in feed:
                for t in a.get("ticker_sentiment", []):
                    if t.get("ticker") == ticker:
                        try:
                            scores.append(float(t["ticker_sentiment_score"]))
                        except (ValueError, KeyError):
                            pass
            if scores:
                avg = sum(scores) / len(scores)
                lbl = ("Bullish tilt" if avg > 0.15 else
                       "Bearish tilt" if avg < -0.15 else "Neutral")
                color = ("#047857" if avg > 0.15 else
                         "#b91c1c" if avg < -0.15 else "#71717a")
                st.markdown(
                    f'<div style="border:1px solid #e4e4e7;border-left:'
                    f'3px solid {color};padding:0.5rem 0.8rem;'
                    f'margin-bottom:0.6rem;background:#fff;">'
                    f'<span style="font-family:Consolas,monospace;'
                    f'font-size:0.7rem;letter-spacing:0.08em;'
                    f'color:#71717a;">NEWS SENTIMENT (ALPHA VANTAGE, '
                    f'{len(scores)} ARTICLES)</span><br>'
                    f'<b style="color:{color};">{lbl}</b> '
                    f'<span style="font-family:Consolas,monospace;'
                    f'color:#71717a;">score {avg:+.2f}</span></div>',
                    unsafe_allow_html=True)
    for item in ticker_news(ticker, limit=6):
        with st.container(border=True):
            st.markdown(f"**{item['title']}**")
            meta = " · ".join(x for x in (item["publisher"],
                                          time_ago(item["published"])) if x)
            if meta:
                st.caption(meta)
            if item["link"]:
                st.markdown(f"[Read more]({item['link']})")

render_footer(st)
