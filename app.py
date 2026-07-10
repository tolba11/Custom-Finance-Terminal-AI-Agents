"""Tolba Terminal — entrypoint and router."""
import streamlit as st

st.set_page_config(page_title="Tolba Terminal", layout="wide",
                   initial_sidebar_state="expanded")

pages = [
    st.Page("views/home.py", title="Home", default=True),
    st.Page("views/market_pulse.py", title="Market Pulse"),
    st.Page("views/stock_analyzer.py", title="Stock Analyzer"),
    st.Page("views/etf_analyzer.py", title="ETF Analyzer"),
    st.Page("views/macro.py", title="Macro"),
    st.Page("views/portfolio_view.py", title="Portfolio"),
    st.Page("views/news_view.py", title="News"),
    st.Page("views/events.py", title="Events & Insiders"),
]

pg = st.navigation(pages)

try:
    pg.run()
except Exception:
    st.error("This view hit a temporary problem — usually a rate-limited "
             "or briefly unavailable data source.")
    c1, c2 = st.columns([1, 5])
    with c1:
        if st.button("Retry"):
            st.cache_data.clear()
            st.rerun()
    st.caption("If retries keep failing, the data provider may be "
               "throttling requests; it normally clears within a minute.")
