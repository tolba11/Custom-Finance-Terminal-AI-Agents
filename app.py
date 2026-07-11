"""Tolba Terminal — entrypoint and router."""
import streamlit as st

st.set_page_config(page_title="Tolba Terminal", layout="wide",
                   initial_sidebar_state="expanded")

pages = [
    st.Page("views/home.py", title="Home", default=True),
    st.Page("views/market_pulse.py", title="Market Pulse"),
    st.Page("views/stock_analyzer.py", title="Stock Analyzer"),
    st.Page("views/equity_research.py", title="Equity Research"),
    st.Page("views/etf_analyzer.py", title="ETF Analyzer"),
    st.Page("views/macro.py", title="Macro"),
    st.Page("views/portfolio_view.py", title="Portfolio"),
    st.Page("views/news_view.py", title="News"),
    st.Page("views/events.py", title="Events & Insiders"),
    st.Page("views/pevc.py", title="PE/VC"),
    st.Page("views/compound_ai.py", title="Compound AI"),
    st.Page("views/perceptis_ai.py", title="Perceptis AI"),
]

pg = st.navigation(pages)

# Auto-refresh: rerun every 15 minutes so quotes, charts, and news stay
# current without a manual reload. Paused on Equity Research so a long
# agent run is never interrupted.
if pg.title != "Equity Research":
    try:
        from streamlit_autorefresh import st_autorefresh
        st_autorefresh(interval=15 * 60 * 1000, key="tt_autorefresh")
    except Exception:
        pass

from datetime import datetime, timezone
try:
    from zoneinfo import ZoneInfo
    _now = datetime.now(ZoneInfo("America/New_York"))
    _tz = "ET"
except Exception:
    _now = datetime.now(timezone.utc)
    _tz = "UTC"
st.sidebar.markdown(
    f'<div style="font-family:Consolas,monospace;font-size:0.68rem;'
    f'letter-spacing:0.08em;color:#71717a;padding-top:6px;">'
    f'AUTO-REFRESH 15 MIN<br>UPDATED '
    f'{_now.strftime("%H:%M")} {_tz} · {_now.strftime("%b %d")}'
    f'</div>', unsafe_allow_html=True)

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
