"""Tolba Terminal — entrypoint and router."""
import streamlit as st

st.set_page_config(page_title="Tolba Terminal", layout="wide",
                   initial_sidebar_state="expanded")

from lib.registry import PAGES

pages = [st.Page(f, title=t, default=(t == "Home"))
         for f, t, _ in PAGES]

pg = st.navigation(pages)

# Auto-refresh: rerun every 15 minutes so quotes, charts, and news stay
# current without a manual reload. Paused on Equity Research so a long
# agent run is never interrupted.
if pg.title not in ("Equity Research", "Deep Finance"):
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
except Exception as _e:
    st.error("This view hit a temporary problem — usually a rate-limited "
             "or briefly unavailable data source.")
    st.caption(f"Detail: {type(_e).__name__}: {_e}")
    c1, c2 = st.columns([1, 5])
    with c1:
        if st.button("Retry"):
            st.cache_data.clear()
            st.rerun()
    st.caption("If retries keep failing, the data provider may be "
               "throttling requests; it normally clears within a minute.")
