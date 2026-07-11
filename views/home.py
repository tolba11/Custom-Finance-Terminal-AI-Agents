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
st.markdown('<div class="tt-subtitle">FUNCTIONS</div>',
            unsafe_allow_html=True)
from lib.registry import PAGES, url_path

funcs = [(f, t, d) for f, t, d in PAGES if t != "Home"]
st.caption(f"{len(funcs)} functions available")
cols = st.columns(3)
for i, (f, title, desc) in enumerate(funcs):
    with cols[i % 3]:
        st.markdown(
            f'<a href="{url_path(f)}" target="_self" '
            f'style="text-decoration:none;">'
            f'<div class="tt-func"><span class="tt-func-name">{title}'
            f'</span><br><span class="tt-func-desc">{desc}</span>'
            f'</div></a>', unsafe_allow_html=True)

render_footer(st)
