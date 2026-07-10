"""yfinance wrappers with caching."""
import pandas as pd
import streamlit as st
import yfinance as yf

INDEX_TICKERS = {
    "^GSPC": "S&P 500",
    "^NDX": "Nasdaq 100",
    "^DJI": "Dow Jones",
    "^RUT": "Russell 2000",
    "^VIX": "VIX",
    "^TNX": "10Y Yield",
    "GC=F": "Gold",
    "CL=F": "Crude WTI",
    "BTC-USD": "Bitcoin",
    "DX-Y.NYB": "US Dollar (DXY)",
}

SECTOR_ETFS = {
    "XLK": "Technology",
    "XLF": "Financials",
    "XLV": "Health Care",
    "XLE": "Energy",
    "XLI": "Industrials",
    "XLY": "Cons. Discretionary",
    "XLP": "Cons. Staples",
    "XLU": "Utilities",
    "XLRE": "Real Estate",
    "XLB": "Materials",
    "XLC": "Communication",
}

# period label -> (yfinance period, interval)
PERIOD_MAP = {
    "1D": ("1d", "5m"),
    "5D": ("5d", "15m"),
    "1M": ("1mo", "1d"),
    "3M": ("3mo", "1d"),
    "6M": ("6mo", "1d"),
    "YTD": ("ytd", "1d"),
    "1Y": ("1y", "1d"),
    "3Y": ("3y", "1wk"),
    "5Y": ("5y", "1wk"),
    "10Y": ("10y", "1wk"),
    "20Y": ("20y", "1mo"),
    "30Y": ("30y", "1mo"),
    "Max": ("max", "1mo"),
}


@st.cache_data(ttl=60, show_spinner=False)
def get_quote(ticker: str) -> dict:
    """Last price, previous close, change, and basic info for one ticker."""
    t = yf.Ticker(ticker)
    info = {}
    try:
        info = t.fast_info or {}
        price = info.get("last_price") or info.get("lastPrice")
        prev = info.get("previous_close") or info.get("previousClose")
    except Exception:
        price, prev = None, None
    if price is None or prev is None:
        try:
            h = t.history(period="5d", interval="1d")
            if len(h) >= 2:
                price = float(h["Close"].iloc[-1])
                prev = float(h["Close"].iloc[-2])
            elif len(h) == 1:
                price = prev = float(h["Close"].iloc[-1])
        except Exception:
            pass
    change = None
    change_pct = None
    if price is not None and prev not in (None, 0):
        change = price - prev
        change_pct = change / prev * 100
    return {
        "ticker": ticker,
        "price": price,
        "prev_close": prev,
        "change": change,
        "change_pct": change_pct,
    }


@st.cache_data(ttl=300, show_spinner=False)
def get_history(ticker: str, period_label: str) -> pd.DataFrame:
    """OHLCV history for a period label from PERIOD_MAP."""
    period, interval = PERIOD_MAP.get(period_label, ("1y", "1d"))
    df = yf.Ticker(ticker).history(period=period, interval=interval)
    if df is None:
        return pd.DataFrame()
    return df.dropna(subset=["Close"]) if "Close" in df else df


@st.cache_data(ttl=60, show_spinner=False)
def get_quotes_bulk(tickers: tuple) -> dict:
    """Quotes for many tickers via one bulk download."""
    out = {}
    try:
        df = yf.download(
            list(tickers), period="5d", interval="1d",
            group_by="ticker", progress=False, threads=True,
        )
        for tk in tickers:
            try:
                closes = (df[tk]["Close"] if len(tickers) > 1 else df["Close"]).dropna()
                if len(closes) >= 2:
                    price = float(closes.iloc[-1])
                    prev = float(closes.iloc[-2])
                    out[tk] = {
                        "ticker": tk, "price": price, "prev_close": prev,
                        "change": price - prev,
                        "change_pct": (price - prev) / prev * 100 if prev else None,
                    }
            except Exception:
                continue
    except Exception:
        pass
    # fill any misses individually
    for tk in tickers:
        if tk not in out:
            out[tk] = get_quote(tk)
    return out


@st.cache_data(ttl=300, show_spinner=False)
def get_history_bulk(tickers: tuple, period_label: str) -> dict:
    """Close-price history for many tickers keyed by ticker."""
    period, interval = PERIOD_MAP.get(period_label, ("1y", "1d"))
    out = {}
    try:
        df = yf.download(
            list(tickers), period=period, interval=interval,
            group_by="ticker", progress=False, threads=True,
        )
        for tk in tickers:
            try:
                sub = df[tk] if len(tickers) > 1 else df
                sub = sub.dropna(subset=["Close"])
                if not sub.empty:
                    out[tk] = sub
            except Exception:
                continue
    except Exception:
        pass
    return out


@st.cache_data(ttl=600, show_spinner=False)
def get_stock_fundamentals(ticker: str) -> dict:
    """Full .info dict (best-effort)."""
    try:
        return yf.Ticker(ticker).info or {}
    except Exception:
        return {}


@st.cache_data(ttl=600, show_spinner=False)
def get_etf_details(ticker: str) -> dict:
    """ETF metadata: info, top holdings, sector weights."""
    t = yf.Ticker(ticker)
    out = {"info": {}, "holdings": None, "sectors": None}
    try:
        out["info"] = t.info or {}
    except Exception:
        pass
    try:
        fd = t.funds_data
        try:
            th = fd.top_holdings
            if th is not None and not th.empty:
                out["holdings"] = th
        except Exception:
            pass
        try:
            sw = fd.sector_weightings
            if sw:
                out["sectors"] = sw
        except Exception:
            pass
    except Exception:
        pass
    return out


@st.cache_data(ttl=600, show_spinner=False)
def is_etf(ticker: str) -> bool:
    info = get_stock_fundamentals(ticker)
    return (info.get("quoteType") or "").upper() == "ETF"
