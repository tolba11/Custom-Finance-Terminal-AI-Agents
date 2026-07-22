"""Persistent watchlist stored in data/watchlist.json."""
import json
import os

_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)),
                     "data", "watchlist.json")
DEFAULT = ["AAPL", "MSFT", "NVDA", "TSLA", "AMZN", "GOOGL", "META", "SPY"]


def load_watchlist() -> list:
    try:
        with open(_PATH) as f:
            wl = json.load(f)
        return [str(t).upper() for t in wl if t] or list(DEFAULT)
    except Exception:
        return list(DEFAULT)


def save_watchlist(tickers: list):
    os.makedirs(os.path.dirname(_PATH), exist_ok=True)
    seen, out = set(), []
    for t in tickers:
        t = str(t).strip().upper()
        if t and t not in seen:
            seen.add(t)
            out.append(t)
    with open(_PATH, "w") as f:
        json.dump(out[:30], f)
