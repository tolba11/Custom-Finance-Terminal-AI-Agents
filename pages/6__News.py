"""News — market headlines + by-ticker search."""
import streamlit as st

from lib.config import apply_base_style, render_footer, render_sidebar
from lib.logos import logo_img_html
from lib.news import market_news, ticker_news, time_ago

st.set_page_config(page_title="News", page_icon="📰", layout="wide")
apply_base_style(st)
render_sidebar(st)
st.title("📰 News")


def render_items(items):
    if not items:
        st.info("No headlines found right now — try again shortly.")
        return
    for item in items:
        with st.container(border=True):
            st.markdown(f"**{item['title']}**")
            meta = " · ".join(x for x in (item["publisher"],
                                          time_ago(item["published"])) if x)
            if meta:
                st.caption(meta)
            if item["summary"]:
                s = item["summary"]
                st.write(s[:260] + ("…" if len(s) > 260 else ""))
            if item["link"]:
                st.markdown(f"[Read more]({item['link']})")


tab1, tab2 = st.tabs(["Market headlines", "By ticker"])
with tab1:
    render_items(market_news(limit=15))
with tab2:
    tk = st.text_input("Ticker", value="AAPL").strip().upper()
    if tk:
        st.markdown(f"{logo_img_html(tk, 32)} &nbsp;**{tk}**",
                    unsafe_allow_html=True)
        render_items(ticker_news(tk, limit=12))

render_footer(st)
