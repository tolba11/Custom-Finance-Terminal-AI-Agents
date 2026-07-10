"""Stock Market Analyst — landing page with quick market snapshot."""
import streamlit as st

from lib.config import apply_base_style, render_footer, render_sidebar
from lib.market_data import INDEX_TICKERS, get_quotes_bulk

st.set_page_config(page_title="Stock Market Analyst", page_icon="📊",
                   layout="wide")
apply_base_style(st)
render_sidebar(st)

st.title("📊 Stock Market Analyst")
st.caption("Personal research dashboard — educational use only. "
           "No buy/sell recommendations.")

st.subheader("Market snapshot")
quotes = get_quotes_bulk(tuple(INDEX_TICKERS.keys()))

cols = st.columns(5)
for i, (tk, name) in enumerate(INDEX_TICKERS.items()):
    q = quotes.get(tk, {})
    price, pct = q.get("price"), q.get("change_pct")
    with cols[i % 5]:
        if price is not None:
            st.metric(name, f"{price:,.2f}",
                      f"{pct:+.2f}%" if pct is not None else None)
        else:
            st.metric(name, "—")

st.divider()
st.subheader("Explore")
c1, c2, c3 = st.columns(3)
with c1:
    st.page_link("pages/1__Market_Pulse.py", label="📈 Market Pulse",
                 use_container_width=True)
    st.page_link("pages/4__Macro.py", label="🏛️ Macro",
                 use_container_width=True)
with c2:
    st.page_link("pages/2__Stock_Analyzer.py", label="🔍 Stock Analyzer",
                 use_container_width=True)
    st.page_link("pages/5__Portfolio.py", label="💼 Portfolio",
                 use_container_width=True)
with c3:
    st.page_link("pages/3__ETF_Analyzer.py", label="🧺 ETF Analyzer",
                 use_container_width=True)
    st.page_link("pages/6__News.py", label="📰 News",
                 use_container_width=True)

render_footer(st)
