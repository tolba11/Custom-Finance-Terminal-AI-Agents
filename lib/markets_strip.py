"""Shared live strip: commodities, FX, and rates/bond prices.
Quotes cache for 60s; pages refresh every 15 minutes."""
import streamlit as st

from lib.market_data import get_quotes_bulk

STRIP = {
    "Commodities": [("GC=F", "Gold"), ("SI=F", "Silver"),
                    ("CL=F", "WTI Crude"), ("BZ=F", "Brent"),
                    ("HG=F", "Copper"), ("NG=F", "Nat Gas")],
    "FX Rates": [("EURUSD=X", "EUR/USD"), ("GBPUSD=X", "GBP/USD"),
                 ("USDJPY=X", "USD/JPY"), ("AUDUSD=X", "AUD/USD"),
                 ("USDCAD=X", "USD/CAD"), ("DX-Y.NYB", "Dollar Index")],
    "Rates & Bonds": [("^IRX", "13W T-Bill yld"), ("^FVX", "5Y yld"),
                      ("^TNX", "10Y yld"), ("^TYX", "30Y yld"),
                      ("ZN=F", "10Y Note fut"), ("ZB=F", "30Y Bond fut")],
}


def render_markets_strip():
    syms = tuple(s for group in STRIP.values() for s, _ in group)
    quotes = get_quotes_bulk(syms)
    cols = st.columns(3)
    for col, (gname, items) in zip(cols, STRIP.items()):
        with col:
            st.markdown(f"**{gname}**")
            for sym, label in items:
                q = quotes.get(sym, {})
                p, pc = q.get("price"), q.get("change_pct")
                color = ("#047857" if (pc or 0) >= 0 else "#b91c1c")
                ptxt = f"{p:,.2f}" if p is not None else "—"
                ctxt = f"{pc:+.2f}%" if pc is not None else ""
                st.markdown(
                    f'<div style="display:grid;grid-template-columns:'
                    f'minmax(0,1fr) 5.5em 4.6em;gap:8px;align-items:center;'
                    f'padding:5px 0;border-bottom:1px solid #f4f4f5;">'
                    f'<span style="color:#3f3f46;font-size:0.85rem;'
                    f'white-space:nowrap;overflow:hidden;text-overflow:'
                    f'ellipsis;">{label}</span>'
                    f'<span style="text-align:right;font-family:Consolas,'
                    f'monospace;font-size:0.85rem;">{ptxt}</span>'
                    f'<span style="color:{color};text-align:right;'
                    f'font-family:Consolas,monospace;font-size:0.8rem;">'
                    f'{ctxt}</span></div>', unsafe_allow_html=True)
    st.caption("Live quotes, cached 60 seconds · auto-refresh every "
               "15 minutes")
