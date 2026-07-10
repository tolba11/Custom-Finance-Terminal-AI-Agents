"""Home — market snapshot board."""
import streamlit as st

from lib.config import apply_base_style, render_footer, render_sidebar
from lib.market_data import INDEX_TICKERS, get_quotes_bulk

apply_base_style(st)
render_sidebar(st)

st.title("Tolba Terminal")
st.markdown('<div class="tt-subtitle">MARKET SNAPSHOT</div>',
            unsafe_allow_html=True)

quotes = get_quotes_bulk(tuple(INDEX_TICKERS.keys()))

cols = st.columns(5)
for i, (tk, name) in enumerate(INDEX_TICKERS.items()):
    q = quotes.get(tk, {})
    price, pct = q.get("price"), q.get("change_pct")
    with cols[i % 5]:
        if price is not None:
            st.metric(name.upper(), f"{price:,.2f}",
                      f"{pct:+.2f}%" if pct is not None else None)
        else:
            st.metric(name.upper(), "—")

st.divider()
st.markdown('<div class="tt-subtitle">FUNCTIONS</div>', unsafe_allow_html=True)
c1, c2, c3 = st.columns(3)
funcs = [("Market Pulse", "Indices, sectors, movers, headlines"),
         ("Stock Analyzer", "Charts, factor scores, statistics, AI"),
         ("ETF Analyzer", "Returns, risk, holdings, cost peers"),
         ("Macro", "FRED indicators and yield curve"),
         ("Portfolio", "Holdings, allocation, risk"),
         ("Events & Insiders", "Earnings, IPOs, ratings, insiders")]
for i, (fn, desc) in enumerate(funcs):
    with (c1, c2, c3)[i % 3]:
        st.markdown(
            f'<div class="tt-func"><span class="tt-func-name">{fn}</span>'
            f'<br><span class="tt-func-desc">{desc}</span></div>',
            unsafe_allow_html=True)

render_footer(st)
