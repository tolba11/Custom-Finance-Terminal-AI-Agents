"""Events & Insiders — earnings/IPO calendars, analyst trends, insider
transactions (Finnhub)."""
import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from lib import finnhub_data as fh
from lib.config import apply_base_style, render_footer, render_sidebar
from lib.logos import logo_img_html

apply_base_style(st)
render_sidebar(st)
st.title("Events & Insiders")

if fh.key_missing():
    st.info("Add your free **FINNHUB_API_KEY** to the app Secrets to enable "
            "this page. Get one at finnhub.io — it takes a minute.")
    render_footer(st)
    st.stop()

# ---- Earnings calendar ----
st.subheader("Earnings calendar — next 2 weeks")
earnings = fh.earnings_calendar(14)
if earnings:
    rows = []
    for e in earnings[:60]:
        rows.append({
            "Date": e.get("date"),
            "Symbol": e.get("symbol"),
            "When": {"bmo": "Before open", "amc": "After close",
                     "dmh": "During market"}.get(e.get("hour"), "—"),
            "EPS est.": e.get("epsEstimate"),
            "EPS actual": e.get("epsActual"),
            "Revenue est. ($M)": round(e["revenueEstimate"] / 1e6, 0)
            if e.get("revenueEstimate") else None,
        })
    st.dataframe(pd.DataFrame(rows), hide_index=True,
                 use_container_width=True, height=420)
    st.caption("Source: analyst consensus estimates, Finnhub.")
else:
    st.warning("No earnings data returned — the free Finnhub tier limits "
               "this endpoint at times. Try again later.")

# ---- IPO calendar ----
with st.expander("Upcoming IPOs (next 30 days)"):
    ipos = fh.ipo_calendar(30)
    if ipos:
        st.dataframe(pd.DataFrame([{
            "Date": i.get("date"), "Symbol": i.get("symbol"),
            "Company": i.get("name"),
            "Exchange": i.get("exchange"),
            "Price range": i.get("price"),
            "Shares (M)": round(i["numberOfShares"] / 1e6, 1)
            if i.get("numberOfShares") else None,
        } for i in ipos]), hide_index=True, use_container_width=True)
    else:
        st.write("No IPOs found in the window.")

st.divider()

# ---- Per-ticker: analyst trends + insiders ----
ticker = st.text_input("Ticker for analyst & insider detail",
                       value="AAPL").strip().upper()
if ticker:
    c1, c2 = st.columns([1, 1])

    with c1:
        st.subheader("Analyst recommendation trends")
        recs = fh.recommendation_trends(ticker)
        if recs:
            df = pd.DataFrame(recs[:12]).sort_values("period")
            fig = go.Figure()
            series = [("strongBuy", "Strong positive", "#15803d"),
                      ("buy", "Positive", "#22c55e"),
                      ("hold", "Neutral", "#eab308"),
                      ("sell", "Negative", "#f87171"),
                      ("strongSell", "Strong negative", "#b91c1c")]
            for col, label, color in series:
                if col in df:
                    fig.add_trace(go.Bar(x=df["period"], y=df[col],
                                         name=label, marker_color=color))
            fig.update_layout(barmode="stack", template="plotly_white",
                              height=380, margin=dict(l=10, r=10, t=20, b=10),
                              legend=dict(orientation="h", y=-0.15),
                              paper_bgcolor="rgba(0,0,0,0)")
            st.plotly_chart(fig, use_container_width=True)
            st.caption("Source: analyst ratings, Finnhub.")
        else:
            st.write("No analyst trend data for this symbol.")

    with c2:
        st.subheader("Recent insider transactions")
        st.markdown(f"{logo_img_html(ticker, 28)} &nbsp;**{ticker}**",
                    unsafe_allow_html=True)
        ins = fh.insider_transactions(ticker)
        if ins:
            for t in ins[:15]:
                chg = t.get("change") or 0
                color = "#22c55e" if chg > 0 else "#ef4444" if chg < 0 else "#71717a"
                verb = "acquired" if chg > 0 else "disposed of" if chg < 0 else "held"
                price = t.get("transactionPrice")
                price_txt = f" @ ${price:,.2f}" if price else ""
                st.markdown(
                    f'<div style="padding:5px 0;border-bottom:1px solid '
                    f'#e4e4e7;"><b>{t.get("name", "?")}</b> '
                    f'<span style="color:{color};">{verb} '
                    f'{abs(chg):,.0f} shares</span>'
                    f'<span style="color:#71717a;">{price_txt} · '
                    f'{t.get("transactionDate", "")}</span></div>',
                    unsafe_allow_html=True)
            st.caption("Source: SEC Form 4 filings, Finnhub.")
        else:
            st.write("No recent insider transactions found.")

render_footer(st)
