"""Treasury yield curve helpers (FRED)."""
import pandas as pd
import streamlit as st

from lib.macro import get_series

CURVE_SERIES = {
    "1M": "DGS1MO", "3M": "DGS3MO", "6M": "DGS6MO",
    "1Y": "DGS1", "2Y": "DGS2", "3Y": "DGS3", "5Y": "DGS5",
    "7Y": "DGS7", "10Y": "DGS10", "20Y": "DGS20", "30Y": "DGS30",
}


@st.cache_data(ttl=3600, show_spinner=False)
def get_yield_curve() -> pd.Series:
    """Latest yield per tenor. Empty series if no FRED key."""
    points = {}
    for tenor, sid in CURVE_SERIES.items():
        s = get_series(sid, years=1)
        if not s.empty:
            points[tenor] = float(s.iloc[-1])
    return pd.Series(points)


@st.cache_data(ttl=3600, show_spinner=False)
def get_curve_history(tenors=("2Y", "10Y"), years: int = 10) -> pd.DataFrame:
    df = pd.DataFrame({t: get_series(CURVE_SERIES[t], years=years)
                       for t in tenors if t in CURVE_SERIES})
    return df.dropna(how="all")
